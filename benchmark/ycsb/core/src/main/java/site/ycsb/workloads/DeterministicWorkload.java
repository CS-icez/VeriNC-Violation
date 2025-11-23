/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package site.ycsb.workloads;

import site.ycsb.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * A deterministic workload that replays operations from a trace file.
 * Each line: OP KEY (e.g., R user123 or U user456). Lines starting with # or blank are skipped.
 */
public class DeterministicWorkload extends Workload {
  private static final String PROP_TRACE = "deterministic.tracefile";
  private static final String PROP_TABLE = "table";

  // 不再 static，确保每次 YCSB 实例化都重新加载
  private List<String> ops = Collections.emptyList();
  private AtomicInteger cursor = new AtomicInteger(0);

  private String table = "usertable";

  private boolean isTransactionPhase = true;

  @Override
  public void init(Properties p) throws WorkloadException {
    String path = p.getProperty(PROP_TRACE);
    if (path == null) throw new WorkloadException("missing property: " + PROP_TRACE);
    try {
      ops = Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8);
    } catch (IOException e) {
      throw new WorkloadException("load trace failed: " + e.getMessage(), e);
    }
    cursor.set(0);
    String t = p.getProperty(PROP_TABLE);
    if (t != null) table = t;
    // dotransactions property: "true" for run phase, "false" for load phase
    isTransactionPhase = Boolean.parseBoolean(p.getProperty("dotransactions", "true"));
    System.out.println("[INFO][DeterministicWorkload] loaded trace lines: " + ops.size()
        + ", isTransactionPhase=" + isTransactionPhase);
  }

  @Override
  public boolean doInsert(DB db, Object threadState) {
    // 加载阶段: 将 R/U/W 统一当作一次写操作 (UPDATE/INSERT 语义)
    int i = cursor.getAndIncrement();
    if (i >= ops.size()) return false;
    String line = ops.get(i).trim();
    if (line.isEmpty() || line.startsWith("#")) return true;

    String[] parts = line.split("\\s+");
    if (parts.length < 2) return true;
    String op = parts[0].toUpperCase(Locale.ROOT);
    String key = parts[1];

    // 使用 8B 对齐的 value，避免底层 padding 触发断言
    HashMap<String, ByteIterator> values = new HashMap<>();
    values.put("field0", new StringByteIterator("v0000000")); // length = 8
    try {
      Status st = db.insert(table, key, values);
      System.out.println("[TRACE][DeterministicWorkload][LOAD] " + op + "->UPDATE " + key + " status=" + st);
      return st == Status.OK;
    } catch (Exception e) {
      System.out.println("[ERROR][DeterministicWorkload][LOAD] exception: " + e.getMessage());
      return false;
    }
  }

  @Override
  public boolean doTransaction(DB db, Object threadState) {
    // 事务阶段: 回放原始操作
    if (!isTransactionPhase) return true; // 防御
    return replayNext(db);
  }

  @Override
  public void cleanup() throws WorkloadException {
    // 允许重复运行时重新开始（若框架重用对象）
    cursor.set(ops.size()); // 标记已用完；真正重置在下一次 init()
  }

  private boolean replayNext(DB db) {
    int i = cursor.getAndIncrement();
    if (i >= ops.size()) return false;
    String raw = ops.get(i);
    String line = raw.trim();
    if (line.isEmpty() || line.startsWith("#")) {
      System.out.println("[DEBUG][DeterministicWorkload] skip line " + (i + 1));
      return true;
    }

    String[] parts = line.split("\\s+");
    if (parts.length < 2) {
      System.out.println("[WARN][DeterministicWorkload] malformed line " + (i + 1) + ": " + raw);
      return true;
    }
    String op = parts[0].toUpperCase(Locale.ROOT);
    String key = parts[1];

    try {
      if (op.equals("R")) {
        Map<String, ByteIterator> result = new HashMap<>();
        Status st = db.read(table, key, null, result);
        System.out.println("[TRACE][DeterministicWorkload] R " + key + " status=" + st);
        return st == Status.OK;
      } else if (op.equals("U") || op.equals("W")) {
        HashMap<String, ByteIterator> values = new HashMap<>();
        values.put("field0", new StringByteIterator("v0000000")); // 8B 对齐
        Status st = db.update(table, key, values);
        System.out.println("[TRACE][DeterministicWorkload] U " + key + " status=" + st);
        return st == Status.OK;
      } else {
        System.out.println("[WARN][DeterministicWorkload] unknown op '" + op + "' at line " + (i + 1));
        return true;
      }
    } catch (Exception e) {
      System.out.println("[ERROR][DeterministicWorkload] exception at line " + (i + 1) + ": " + e.getMessage());
      return false;
    }
  }
}
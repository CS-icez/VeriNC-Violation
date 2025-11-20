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
  private static volatile List<String> ops;
  private static final AtomicInteger cursor = new AtomicInteger(0);
  private String table = "usertable";

  @Override
  public void init(Properties p) throws WorkloadException {
    if (ops == null) {
      synchronized (DeterministicWorkload.class) {
        if (ops == null) {
          String path = p.getProperty(PROP_TRACE);
          if (path == null) throw new WorkloadException("missing property: " + PROP_TRACE);
          try {
            ops = Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8);
          } catch (IOException e) {
            throw new WorkloadException("load trace failed: " + e.getMessage(), e);
          }
        }
      }
    }
    String t = p.getProperty(PROP_TABLE);
    if (t != null) table = t;
  }

  @Override
  public Object initThread(Properties p, int mythreadid, int threadcount) {
    return null;
  }

  @Override
  public boolean doInsert(DB db, Object threadState) { return true; }

  @Override
  public boolean doTransaction(DB db, Object threadState) {
    int i = cursor.getAndIncrement();
    if (i >= ops.size()) return false;
    String line = ops.get(i).trim();
    if (line.isEmpty() || line.startsWith("#")) return true;

    String[] parts = line.split("\\s+");
    if (parts.length < 2) return true;
    String op = parts[0].toUpperCase(Locale.ROOT);
    String key = parts[1];

    try {
      if (op.equals("R")) {
        // DB.read requires (table, key, fields, resultMap). We don't restrict fields here.
        Map<String, ByteIterator> result = new HashMap<>();
        return db.read(table, key, null, result) == Status.OK;
      } else if (op.equals("U") || op.equals("W")) {
        HashMap<String, ByteIterator> values = new HashMap<>();
        values.put("field0", new StringByteIterator("v"));
        return db.update(table, key, values) == Status.OK;
      } else {
        return true;
      }
    } catch (Exception e) {
      return false;
    }
  }
}
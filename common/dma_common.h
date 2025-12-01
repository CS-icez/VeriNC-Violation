#ifndef DMA_COMMON_H
#define DMA_COMMON_H

// Transport abstraction header. Original RDMA implementation retained under USE_RDMA.
// When USE_RDMA is NOT defined, we provide a minimal UDP socket based fallback that
// preserves the public API (DMAcontext struct and functions) with drastically reduced fields.
// This allows the rest of the code (client/server) to run inside container networks
// without requiring RDMA or libibverbs.

#include "packet.h"
#include "utils.h"
#include <assert.h>
#include <cmath>
#include <inttypes.h>
#include <net/if.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/ipc.h>
#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <unistd.h>

#ifdef USE_RDMA
#include "mlx5_defs.h"
#include <rdma/rdma_cma.h>
#endif

#define POLLING_SIZE 400
#define ENTRY_SIZE 256 /* maximum size of each buffer */
#define PORT_NUM 1

#define DEBUG_PRINT_ALL_SENDING_PACKET false
#define DEBUG_PRINT_ALL_RECEIVING_PACKET false

#define DEBUG_CHECK_SEND_RECEIVE_TOTAL false

static constexpr size_t kAppRecvCQDepth = 8;
static constexpr size_t kAppRQDepth = 4; // Multi-packet RQ depth

static constexpr size_t kAppLogNumStrides = 9;
static constexpr size_t kAppLogStrideBytes = 9;
static constexpr size_t kAppMaxPostlist = 512;

static constexpr bool kAppVerbose = false;
static constexpr bool kAppCheckContents = true; // Check buffer contents

/// Size of one ring message buffer
static constexpr size_t kAppRingMbufSize = (1ull << kAppLogStrideBytes);

/// Number of strides in one multi-packet RECV WQE
static constexpr size_t kAppStridesPerWQE = (1ull << kAppLogNumStrides);

/// Packets after which the CQE snapshot cycles
static constexpr size_t kAppCQESnapshotCycle = 65536 * kAppStridesPerWQE;

/// Total number of entries in the RX ring
static constexpr size_t kAppNumRingEntries = (kAppStridesPerWQE * kAppRQDepth);

static constexpr size_t kAppRingSize = (kAppNumRingEntries * kAppRingMbufSize);

/// A consistent snapshot of CQE fields in host endian format
struct cqe_snapshot_t {
    uint16_t wqe_id;
    uint16_t wqe_counter;

    /// Return this packet's index in the CQE snapshot cycle
    size_t get_cqe_snapshot_cycle_idx() const
    {
        return wqe_id * kAppStridesPerWQE + wqe_counter;
    }

    std::string to_string()
    {
        std::ostringstream ret;
        ret << "[ID " << std::to_string(wqe_id) << ", counter "
            << std::to_string(wqe_counter) << "]";
        return ret.str();
    }
};

// Forward declare to keep signature compatibility when not using RDMA
struct ibv_device;

#ifdef USE_RDMA
struct DMAcontext {
    struct ibv_pd* pd;
    struct ibv_context* ctx;
    struct ibv_cq* receive_cq;
    struct ibv_cq* send_cq;
    struct ibv_mr* send_mr;
    void* send_region;
    struct ibv_qp* data_qp;

    struct ibv_qp* mp_recv_qp;
    struct ibv_cq* mp_recv_cq;
    struct ibv_exp_wq* mp_wq;
    struct ibv_exp_wq_family* mp_wq_family;
    struct ibv_exp_rwq_ind_table* mp_ind_tbl;
    volatile mlx5_cqe64* mp_cqe_arr;
    struct ibv_sge* mp_sge;
    uint8_t* mp_recv_ring;
    uint8_t* mp_send_ring;
    struct ibv_mr* mp_send_mr;

    int id;
    int total_received;
    int total_sent;
    int my_send_queue_length;
    int my_recv_queue_length;

    size_t ring_head;
    size_t nb_rx_rolling;
    size_t sge_idx;
    size_t cqe_idx;

    cqe_snapshot_t prev_snapshot;
    bool isPS;
    bool isMarkTimeStamp;
    bool* isSent;
    std::chrono::high_resolution_clock::time_point* first_send_time;
    std::chrono::high_resolution_clock::time_point* first_receive_time;
};
#else
// Socket fallback (no RDMA). Only keep fields actually referenced by higher layers.
struct DMAcontext {
    void* send_region;              // Buffer of P4ML layers (without IP/UDP headers)
    uint8_t* mp_recv_ring;          // Ring for received payloads
    int id;                         // Logical thread id
    int total_received;
    int total_sent;
    int my_send_queue_length;       // Capacity hint
    int my_recv_queue_length;       // Capacity hint
    size_t ring_head;               // Current ring head index
    size_t nb_rx_rolling;           // Dummy counter for compatibility
    size_t sge_idx;                 // Unused in socket mode
    size_t cqe_idx;                 // Unused in socket mode
    cqe_snapshot_t prev_snapshot;   // Placeholder for compatibility
    bool isPS;                      // Is parameter server side
    bool isMarkTimeStamp;           // Enable timestamp marking
    bool* isSent;
    std::chrono::high_resolution_clock::time_point* first_send_time;
    std::chrono::high_resolution_clock::time_point* first_receive_time;
    int sockfd;                     // UDP socket fd
    struct sockaddr_in peer_addr;   // Peer address (destination or client)
};
#endif

DMAcontext* DMA_create(struct ibv_device* ib_dev, int thread_id, bool isPS);
void send_packet(DMAcontext* dma_context, int packet_size, uint64_t offset);
size_t receive_packet(DMAcontext *dma_context, cqe_snapshot_t* new_snapshot);
void dma_postback(DMAcontext *dma_context);
void dma_update_snapshot(DMAcontext *dma_context, cqe_snapshot_t new_snapshot);

#ifdef USE_RDMA
const char* ibv_wc_opcode_str(enum ibv_wc_opcode opcode);
void dma_context_print(DMAcontext* dma_context, const char* caption);
void install_flow_rule(struct ibv_qp* qp, uint16_t thread_id, bool isPS);
void install_udp_flow_rule(struct ibv_qp* qp, uint16_t dst_port);
void snapshot_cqe(volatile mlx5_cqe64* cqe, cqe_snapshot_t& cqe_snapshot);
size_t get_cycle_delta(const cqe_snapshot_t& prev, const cqe_snapshot_t& cur);
#endif

// Header offset abstraction: with RDMA raw packets we have L2/L3/L4 headers inline.
// With socket fallback we only send application payload.
#ifdef USE_RDMA
#define P4ML_HEADER_OFFSET IP_ETH_UDP_HEADER_SIZE
#else
#define P4ML_HEADER_OFFSET 0
#endif
#endif

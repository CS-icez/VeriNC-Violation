
# All Target
RDMA ?= 0
DPDK ?= 1
CXX ?= g++
CXXFLAGS := -std=c++11 -O3 -g -I../common/
LDFLAGS := -lpthread

ifeq ($(RDMA),1)
  CXXFLAGS += -DUSE_RDMA
  LDFLAGS += -libverbs -lrdmacm
endif

ifeq ($(DPDK),1)
	ifeq ($(RDMA),1)
		$(error Cannot enable both RDMA=1 and DPDK=1)
	endif
	CXXFLAGS += -DUSE_DPDK $(shell pkg-config --cflags libdpdk 2>/dev/null)
	LDFLAGS += $(shell pkg-config --libs libdpdk 2>/dev/null)
else
	$(error UDP fallback removed. Build requires DPDK=1 or RDMA=1)
endif

all: app

app: ParameterServer.o ../common/dma_common.o ../common/HashTable.o
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

ParameterServer.o: ParameterServer.cc ParameterServer.h
	$(CXX) $(CXXFLAGS) -c -o $@ ParameterServer.cc

../common/dma_common.o: ../common/dma_common.cc ../common/dma_common.h
	$(CXX) $(CXXFLAGS) -c -o $@ ../common/dma_common.cc

../common/HashTable.o: ../common/HashTable.cc ../common/HashTable.h
	$(CXX) $(CXXFLAGS) -c -o $@ ../common/HashTable.cc


# Clean Target
clean:
	rm -f *.o ../common/*.o app

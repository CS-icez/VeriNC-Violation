
# All Target
RDMA ?= 0
CXX ?= g++
CXXFLAGS := -std=c++11 -O3 -g -I../common/
LDFLAGS := -lpthread

ifeq ($(RDMA),1)
  CXXFLAGS += -DUSE_RDMA
  LDFLAGS += -libverbs -lrdmacm
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

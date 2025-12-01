# CFLAGS  := -O3 -g
# LD      := g++
# LDFLAGS := ${LDFLAGS} -lrdmacm -libverbs -lrt -lpthread  -lm

# ROCE_COMMON_PATH = ../common/
# INCLUDES  = -I${ROCE_COMMON_PATH}
# CFLAGS := ${CFLAGS} ${INCLUDES}
# SOURCES := $(wildcard *.c *.h ${ROCE_COMMON_PATH}*.c ${ROCE_COMMON_PATH}*.h)


# all: app 
# app: main.o  p4ml_manager.o ${ROCE_COMMON_PATH}packet.o ${ROCE_COMMON_PATH}dma_common.o ${ROCE_COMMON_PATH}window_manager.o
# 	${LD} $(CFLAGS) -o $@ $^ ${LDFLAGS}


# # Clean Target
# clean:
# 	rm *.o ../common/*.o
# 	rm app

RDMA ?= 0
CXX ?= g++
CXXFLAGS := -std=c++11 -g -O3 -I../common/
LDFLAGS := -lpthread -lrt -lm

ifeq ($(RDMA),1)
  CXXFLAGS += -DUSE_RDMA
  LDFLAGS += -lrdmacm -libverbs
endif

all: app

app: main.o p4ml_manager.o ../common/HashTable.o ../common/dma_common.o
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

main.o: main.cc
	$(CXX) $(CXXFLAGS) -c -o $@ $<

p4ml_manager.o: p4ml_manager.cc
	$(CXX) $(CXXFLAGS) -mavx -c -o $@ $<

../common/HashTable.o: ../common/HashTable.cc
	$(CXX) $(CXXFLAGS) -c -o $@ $<

../common/dma_common.o: ../common/dma_common.cc ../common/dma_common.h
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f *.o ../common/*.o app

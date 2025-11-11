#  Copyright 2021 Intel-KAUST-Microsoft
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# SwitchML Project
# @file third_party makefile
# @brief The makefile to compile and prepare all needed third party libraries.
#
# Build Variables --
# Format: VARIABLE (type: default value): usage
#
# - DEBUG (boolean: 0): Disable optimizations and add debug symbols.
# - DPDK (boolean: 0): Compile all third party libraries needed by the DPDK backend.
# - MLX5 (boolean: 0): Configure DPDK for Mellanox ConnectX-4 ConnectX-5. 
# - MLX4 (boolean: 0): Configure DPDK for Mellanox ConnectX-3. 
# - RDMA (boolean: 0): Compile all third party libraries needed by the RDMA backend.
#

DEVROOT := $(realpath ../)

CMAKE ?= cmake
ifeq ($(DEBUG),1)
$(info Compiling third_party with DEBUG)
CXXFLAGS += -DDEBUG -O0 -g
else
CXXFLAGS += -O3
endif

DEPS = vcl

ifeq ($(DPDK),1)
DEPS += dpdk grpc
endif
ifeq ($(RDMA),1)
DEPS += grpc
endif

.PHONY: default
default: $(DEPS)

.PHONY: dpdk
dpdk:
	cd dpdk && git reset --hard
	cd dpdk && git apply ../dpdk.patch
ifeq ($(MLX5),1)
	sed -i 's/CONFIG_RTE_LIBRTE_MLX5_PMD=n/CONFIG_RTE_LIBRTE_MLX5_PMD=y/' dpdk/config/common_base
	sed -i 's/CONFIG_RTE_LIBRTE_MLX4_PMD=y/CONFIG_RTE_LIBRTE_MLX4_PMD=n/' dpdk/config/common_base
else
ifeq ($(MLX4),1)
	sed -i 's/CONFIG_RTE_LIBRTE_MLX5_PMD=y/CONFIG_RTE_LIBRTE_MLX5_PMD=n/' dpdk/config/common_base
	sed -i 's/CONFIG_RTE_LIBRTE_MLX4_PMD=n/CONFIG_RTE_LIBRTE_MLX4_PMD=y/' dpdk/config/common_base
endif
endif
	$(MAKE) -C dpdk defconfig T=x86_64-native-linuxapp-gcc
	# 修改生成的 build/.config（真正起作用的配置）
	# 启用纯用户态 vdev
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_AF_PACKET=)n/\1y/' dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_TAP=)n/\1y/'       dpdk/build/.config || true

	# 禁用会触发内核构建的开关
	sed -ri 's/^(CONFIG_RTE_KNI_KMOD=)y/\1n/'            dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_EAL_IGB_UIO=)y/\1n/'         dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_KNI=)y/\1n/'          dpdk/build/.config || true

	# 关闭易引入内核/专用硬件依赖的 raw/accel PMD
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_NTB_RAWDEV=)y/\1n/'               dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_IOAT_RAWDEV=)y/\1n/'              dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_OCTEONTX2_DMA_RAWDEV=)y/\1n/'     dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_QAT=)y/\1n/'                      dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_VIRTIO_CRYPTO=)y/\1n/'            dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_OCTEONTX_CRYPTO=)y/\1n/'          dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_OCTEONTX2_CRYPTO=)y/\1n/'         dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_NITROX=)y/\1n/'                   dpdk/build/.config || true
	sed -ri 's/^(CONFIG_RTE_LIBRTE_PMD_OCTEONTX_ZIPVF=)y/\1n/'           dpdk/build/.config || true

	@grep -E 'AF_PACKET|TAP|IGB_UIO|KNI' dpdk/build/.config || true
	$(MAKE) -C dpdk EXTRA_CFLAGS="-fPIC $(CXXFLAGS)" -j

.PHONY: vcl
vcl:
	# nothing to do for vcl

.PHONY: grpc
grpc:
	mkdir -p grpc/cmake/build
	cd grpc/cmake/build && \
	$(CMAKE) -DCMAKE_INSTALL_PREFIX=$(DEVROOT)/third_party/grpc/build -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release -DgRPC_INSTALL=ON -DgRPC_BUILD_TESTS=OFF -DgRPC_SSL_PROVIDER=package ../.. && \
	make -j8 && \
	make install
	@echo ***IMPORTANT***
	@echo Make sure that you register the grpc/protobuf libraries in the system before you try to run any program that runs switchml rdma.
	@echo You can do that by executing '"sudo bash -c '"'echo $(DEVROOT)/third_party/grpc/build/lib > /etc/ld.so.conf.d/00_switchml.conf'"'"' to add the path.
	@echo Then run '"sudo ldconfig"' to update the list of shared libraries in the same.
	@echo To undo you can simply remove the file '"sudo rm /etc/ld.so.conf.d/00_switchml.conf"' then updating the list of shared libraries using '"sudo ldconfig"'.
	@echo Alternatively, if you do not want to register this local grpc/protobuf installation, you can always set LD_LIBRARY_PATH=$(DEVROOT)/third_party/grpc/build in your environment before running any switchml program.

.PHONY: clean
clean:
	cd dpdk && git clean -fx
	$(RM) -r dpdk/build
	cd grpc && git clean -fx
	$(RM) -r grpc/build grpc/cmake/build

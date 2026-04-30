# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/VSARM/sdk/pico/pico-sdk/tools/pioasm"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pioasm"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pioasm-install"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/tmp"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp/${subDir}")
endforeach()

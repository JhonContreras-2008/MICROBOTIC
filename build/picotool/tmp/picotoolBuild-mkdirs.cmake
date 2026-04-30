# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/_deps/picotool-src"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/_deps/picotool-build"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/_deps"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/picotool/tmp"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/picotool/src/picotoolBuild-stamp"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/picotool/src"
  "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/picotool/src/picotoolBuild-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/Users/jhons/Documents/MICROBOTICA/SEGUIDOR/build/picotool/src/picotoolBuild-stamp/${subDir}")
endforeach()

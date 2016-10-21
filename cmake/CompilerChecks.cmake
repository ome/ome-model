# #%L
# Bio-Formats C++ libraries (cmake build infrastructure)
# %%
# Copyright © 2006 - 2016 Open Microscopy Environment:
#   - Massachusetts Institute of Technology
#   - National Institutes of Health
#   - University of Dundee
#   - Board of Regents of the University of Wisconsin-Madison
#   - Glencoe Software, Inc.
# %%
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of any organization.
# #L%

# Use new variable expansion policy.
if (POLICY CMP0053)
  cmake_policy(SET CMP0053 NEW)
endif(POLICY CMP0053)
if (POLICY CMP0054)
  cmake_policy(SET CMP0054 NEW)
endif(POLICY CMP0054)

include(CheckIncludeFileCXX)
include(CheckCXXCompilerFlag)
include(CheckCXXSourceCompiles)

# Try to enable the -pedantic flag.  This one needs special casing
# since it may break building with older compilers where int64_t (long
# long) isn't available in pedantic mode because it's not part of the
# C++98 standard.  Newer compilers support long long properly.
if (NOT MSVC)
  set(flag -pedantic)
  set(test_cxx_flag "CXX_FLAG${flag}")
  CHECK_CXX_COMPILER_FLAG(${flag} "${test_cxx_flag}")
  if (${test_cxx_flag})
    SET(CMAKE_CXX_FLAGS_SAVE ${CMAKE_CXX_FLAGS})
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
    check_cxx_source_compiles(
  "int main() {
    long long l;
  }"
  CXX_PEDANTIC_LONG_LONG)
    SET(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS_SAVE})
    if (${CXX_PEDANTIC_LONG_LONG})
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
    endif (${CXX_PEDANTIC_LONG_LONG})
  endif (${test_cxx_flag})
endif (NOT MSVC)

# Check if the compiler supports each of the following additional
# warning flags, and enable them if supported.  This greatly improves
# the quality of the build by checking for a number of common
# problems, some of which are quite serious.
if (NOT MSVC)
  set(test_flags
      -Wall
      -Wcast-align
      -Wcast-qual
      -Wctor-dtor-privacy
      -Wextra
      -Wformat=2
      -Wimplicit-atomic-properties
      -Wmissing-declarations
      -Wno-long-long
      -Wnon-virtual-dtor
      -Woverlength-strings
      -Woverloaded-virtual
      -Wredundant-decls
      -Wreorder
      -Wswitch-default
      -Wunused-variable
      -Wwrite-strings
      -Wno-variadic-macros
      -fstrict-aliasing)
  if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    list(APPEND test_flags
         -Wno-unused-local-typedef
         -Wno-language-extension-token)
  endif()
  if (extra-warnings)
    list(APPEND test_flags
        -Wconversion
        -Wdocumentation
        -Wfloat-equal
        -Wmissing-prototypes
        -Wold-style-cast
        -Wunreachable-code)
  endif (extra-warnings)
  if (fatal-warnings)
    list(APPEND test_flags
         -Werror)
  endif (fatal-warnings)
else (NOT MSVC)
  set(test_flags
      /bigobj)
  if (extra-warnings)
    list(APPEND test_flags
         /W4)
  else (extra-warnings)
    list(APPEND test_flags
         /W3)
  endif (extra-warnings)
  if (fatal-warnings)
    list(APPEND test_flags
         /WX)
  endif (fatal-warnings)
endif (NOT MSVC)

foreach(flag ${test_flags})
  string(REGEX REPLACE "[^A-Za-z0-9]" "_" flag_var "${flag}")
  set(test_cxx_flag "CXX_FLAG${flag_var}")
  CHECK_CXX_COMPILER_FLAG(${flag} "${test_cxx_flag}")
  if (${test_cxx_flag})
     set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${flag}")
  endif (${test_cxx_flag})
endforeach(flag ${test_flags})

# May be inlined, so check it compiles:
check_cxx_source_compiles("
#include <stdio.h>
int main(void) {
  char buf[10];
  snprintf(buf, 10, \"Test %d\", 1);
  return 0;
}"
  OME_HAVE_SNPRINTF)

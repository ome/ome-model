# #%L
# OME C++ libraries (cmake build infrastructure)
# %%
# Copyright © 2017 Open Microscopy Environment:
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

find_package(Git)

set(SOURCE_ARCHIVE_DIR "${PROJECT_BINARY_DIR}" CACHE PATH "Location to store source archives")

function(source_archive name version)
  if(GIT_FOUND AND SOURCE_ARCHIVE_DIR AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
    set(basename "${name}-${version}")
    set(basepath "${SOURCE_ARCHIVE_DIR}/${basename}")

    add_custom_command(OUTPUT "${basename}.tar.xz"
                       COMMAND "${CMAKE_COMMAND}" -E make_directory
                               "${SOURCE_ARCHIVE_DIR}"
                       COMMAND "${GIT_EXECUTABLE}" archive -v
                               --format=tar
                               "--prefix=${basename}/"
                               -o "${basepath}.tar"
                               HEAD
                        COMMAND xz "${basepath}.tar"
                        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}")

    add_custom_command(OUTPUT "${basename}.zip"
                       COMMAND "${CMAKE_COMMAND}" -E make_directory
                               "${SOURCE_ARCHIVE_DIR}"
                       COMMAND "${GIT_EXECUTABLE}" archive -v
                               --format=zip
                               "--prefix=${basename}/"
                               -o "${basepath}.zip"
                               HEAD
                        WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}")

    add_custom_target(source-archive DEPENDS "${basename}.tar.xz" "${basename}.zip")
  endif()
endfunction()

# #%L
# OME C++ libraries (cmake build infrastructure)
# %%
# Copyright © 2006 - 2015 Open Microscopy Environment:
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

function(git_info GITDIR)
  set(OME_VERSION UNKNOWN)
  set(OME_VERSION_SHORT UNKNOWN)
  set(OME_VCS_SHORTREVISION UNKNOWN)
  set(OME_VCS_REVISION UNKNOWN)
  set(OME_VCS_DATE UNKNOWN)
  set(OME_VCS_DATE_S UNKNOWN)
  set(OME_VCS_DEV "")

  find_package(Git)

  if(GIT_FOUND)
    execute_process(COMMAND "${GIT_EXECUTABLE}" log -1 HEAD --pretty=%h
      OUTPUT_VARIABLE commit_hash_short RESULT_VARIABLE git_log_fail ERROR_QUIET
      WORKING_DIRECTORY ${GITDIR})
    if (NOT git_log_fail)
      string(REPLACE "\n" "" commit_hash_short "${commit_hash_short}")
      set(OME_VCS_SHORTREVISION ${commit_hash_short})
    endif()

    execute_process(COMMAND "${GIT_EXECUTABLE}" log -1 HEAD --pretty=%H
      OUTPUT_VARIABLE commit_hash RESULT_VARIABLE git_log_fail ERROR_QUIET
      WORKING_DIRECTORY ${GITDIR})
    if (NOT git_log_fail)
      string(REPLACE "\n" "" commit_hash "${commit_hash}")
      set(OME_VCS_REVISION ${commit_hash})
    endif()

    execute_process(COMMAND "${GIT_EXECUTABLE}" log -1 "${commit_hash}" --pretty=%ai
      OUTPUT_VARIABLE commit_date_string RESULT_VARIABLE git_log_fail ERROR_QUIET
      WORKING_DIRECTORY ${GITDIR})
    if (NOT git_log_fail)
      string(REPLACE "\n" "" commit_date_string "${commit_date_string}")
      set(OME_VCS_DATE_S ${commit_date_string})
    endif()

    execute_process(COMMAND "${GIT_EXECUTABLE}" log -1 "${commit_hash}" --pretty=%at
      OUTPUT_VARIABLE commit_date_unix RESULT_VARIABLE git_log_fail ERROR_QUIET
      WORKING_DIRECTORY ${GITDIR})
    if (NOT git_log_fail)
      string(REPLACE "\n" "" commit_date_unix "${commit_date_unix}")
      set(OME_VCS_DATE ${commit_date_unix})
    endif()

    execute_process(COMMAND "${GIT_EXECUTABLE}" describe --match=v[0-9]* --exact
                    OUTPUT_VARIABLE describe_exact_output
                    RESULT_VARIABLE describe_exact_fail
                    ERROR_QUIET
                    WORKING_DIRECTORY ${GITDIR})
    if(NOT describe_exact_fail)
      string(REPLACE "\n" "" describe_exact_output "${describe_exact_output}")
    endif()

    execute_process(COMMAND "${GIT_EXECUTABLE}" describe --match=v[0-9]*
                    OUTPUT_VARIABLE describe_output
                    RESULT_VARIABLE describe_fail
                    ERROR_QUIET
                    WORKING_DIRECTORY ${GITDIR})
    if(NOT describe_fail)
      string(REPLACE "\n" "" describe_output "${describe_output}")
    endif()

    if(describe_exact_fail AND NOT describe_fail AND OME_VCS_SHORTREVISION)
      set(OME_VCS_DEV "-DEV-${OME_VCS_SHORTREVISION}")
    endif()
  endif()

  set(OME_VCS_SHORTREVISION "${OME_VCS_SHORTREVISION}" PARENT_SCOPE)
  set(OME_VCS_REVISION "${OME_VCS_REVISION}" PARENT_SCOPE)
  set(OME_VCS_DATE "${OME_VCS_DATE}" PARENT_SCOPE)
  set(OME_VCS_DATE_S "${OME_VCS_DATE_S}" PARENT_SCOPE)
  set(OME_VCS_DEV "${OME_VCS_DEV}" PARENT_SCOPE)

endfunction(git_info)

macro(git_version_info project_desc git_dir)
  git_info("${git_dir}")

  message(STATUS "Configuring ${project_desc} (${PROJECT_NAME} ${PROJECT_VERSION}${OME_VCS_DEV})")
  if(NOT OME_VCS_SHORTREVISION STREQUAL UNKNOWN AND
     NOT OME_VCS_DATE_S STREQUAL UNKNOWN)
    message(STATUS "Using git commit ${OME_VCS_SHORTREVISION} on ${OME_VCS_DATE_S}")
  endif()
endmacro()

# #%L
# OME Files C++ libraries (cmake build infrastructure)
# %%
# Copyright © 2015 Open Microscopy Environment:
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

cmake_minimum_required(VERSION 3.2.0)

# For building standalone
if(NOT PROJECT_NAME)
  project(ome-files)
# Add our own modules to the include path
list(APPEND CMAKE_MODULE_PATH
     "${CMAKE_CURRENT_LIST_DIR}/../../cmake")
include(Options)
endif()


include(Sphinx)

if (BUILD_SPHINX AND SPHINX_BUILD)
  message(STATUS "Checking manual page dependencies")

  # Create build directory and conf.py
  set(sphinx_srcdir "${CMAKE_CURRENT_SOURCE_DIR}")
  set(sphinx_builddir "${CMAKE_CURRENT_BINARY_DIR}")
  file(MAKE_DIRECTORY "${sphinx_builddir}")
  file(MAKE_DIRECTORY "${sphinx_builddir}/_static")
  configure_file("${sphinx_srcdir}/conf.py"
                 "${sphinx_builddir}/conf.py"
                 @ONLY)

  sphinx_manpages("${sphinx_srcdir}" "${sphinx_builddir}"
                  "${PROJECT_BINARY_DIR}/man" MAN_PAGES)
  sphinx_manpage_dependencies("${sphinx_srcdir}" "${sphinx_builddir}"
                              MAN_PAGE_DEPENDENCIES)
  sphinx_dependencies("${sphinx_srcdir}" SPHINX_DEPENDENCIES)

  # Generate and install man pages

  unset(man_target)
  if(MAN_PAGES)
    add_custom_command(OUTPUT ${MAN_PAGES}
                       COMMAND ${CMAKE_COMMAND} -E make_directory "${sphinx_builddir}/cache"
                       COMMAND ${CMAKE_COMMAND} -E make_directory "${PROJECT_BINARY_DIR}/man"
                       COMMAND ${SPHINX_BUILD}
                               -D "release=${OME_VERSION_SHORT}"
                               -D "version=${OME_VERSION_MAJOR}.${OME_VERSION_MINOR}"
                               -c "${sphinx_builddir}"
                               -d "${sphinx_builddir}/cache"
                               -b man
                               "${sphinx_srcdir}" "${PROJECT_BINARY_DIR}/man"
                       WORKING_DIRECTORY "${sphinx_srcdir}"
                       DEPENDS ${MAN_PAGE_DEPENDENCIES})

    add_custom_target(man ALL DEPENDS ${MAN_PAGES})
    set(man_target man)

    foreach (man ${MAN_PAGES})
      string(REGEX REPLACE ".*(.)\$" "\\1" man_section "${man}")
      install(FILES "${man}"
              DESTINATION "${CMAKE_INSTALL_MANDIR}/man${man_section}"
              COMPONENT "runtime")
    endforeach()
    endif()

  # Generate and install HTML manual
  # Depends on man to allow sharing of cache with parallel build.

  add_custom_command(OUTPUT "${sphinx_builddir}/html/index.html"
                     COMMAND ${CMAKE_COMMAND} -E make_directory "${sphinx_builddir}/cache"
                     COMMAND ${CMAKE_COMMAND} -E make_directory "${sphinx_builddir}/html"
                     COMMAND ${SPHINX_BUILD}
                             -D "release=${OME_VERSION_SHORT}"
                             -D "version=${OME_VERSION_MAJOR}.${OME_VERSION_MINOR}"
                             -c "${sphinx_builddir}"
                             -d "${sphinx_builddir}/cache"
                             -b html
                             "${sphinx_srcdir}" "${sphinx_builddir}/html"
                     WORKING_DIRECTORY "${sphinx_srcdir}"
                     DEPENDS ${man_target} ${SPHINX_DEPENDENCIES})

  add_custom_target(doc-html ALL DEPENDS "${sphinx_builddir}/html/index.html")

  install(DIRECTORY "${sphinx_builddir}/html"
          DESTINATION "${CMAKE_INSTALL_DOCDIR}/manual"
          COMPONENT "runtime")

  if(sphinx-linkcheck)
    set(sphinx_linkcheck_all ALL)
  endif()

  add_custom_target(doc-linkcheck ${sphinx_linkcheck_all}
                    COMMAND ${CMAKE_COMMAND} -E make_directory "${sphinx_builddir}/cache"
                    COMMAND ${CMAKE_COMMAND} -E make_directory "${sphinx_builddir}/linkcheck"
                    COMMAND ${SPHINX_BUILD}
                            -D "release=${OME_VERSION_SHORT}"
                            -D "version=${OME_VERSION_MAJOR}.${OME_VERSION_MINOR}"
                            -c "${sphinx_builddir}"
                            -d "${sphinx_builddir}/cache"
                            -b linkcheck
                            "${sphinx_srcdir}" "${sphinx_builddir}/linkcheck"
                     COMMENT "Checking remote links in sphinx documentation"
                     WORKING_DIRECTORY "${sphinx_srcdir}"
                     DEPENDS doc-api ${man_target} ${SPHINX_DEPENDENCIES})

  add_custom_target(doc-locallinkcheck ${sphinx_linkcheck_all}
                    COMMAND ${CMAKE_COMMAND}
                            "-DOUTPUT=${sphinx_builddir}/linkcheck/output.txt"
                            "-DSPHINX_INSTALL_PATH=${PROJECT_NAME}/manual/html"
                            "-DINTERNAL_REFERENCE=${sphinx_builddir}/html"
                            "-DEXTERNAL_REFERENCE=${CMAKE_INSTALL_FULL_DATAROOTDIR}/doc"
                            "-DDOXYGEN_REFERENCE=${PROJECT_BINARY_DIR}/docs/doxygen/${PROJECT_NAME}/html"
                            "-DDOXYGEN_INSTALL_PATH=${PROJECT_NAME}/api/html"
                            -P "${PROJECT_SOURCE_DIR}/cmake/SphinxCheckInternalLinks.cmake"
                     COMMENT "Checking local links in sphinx documentation"
                     WORKING_DIRECTORY "${sphinx_srcdir}"
                     DEPENDS doc-linkcheck)
else()
  message(WARNING "Manual pages and HTML manual will not be generated or installed")
endif()

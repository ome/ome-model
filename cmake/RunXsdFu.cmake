# Run xsd-fu from a build target

string(REPLACE "^^" ";" XSD_FU "${XSD_FU}")
string(REPLACE "^^" ";" XSD_FU_ARGS "${XSD_FU_ARGS}")
string(REPLACE "^^" ";" XSD_FU_PYTHONPATH "${XSD_FU_PYTHONPATH}")

if(WIN32)
  set(ENV{PYTHONPATH} "${XSD_FU_PYTHONPATH}")
else()
  set(ENV{PYTHONPATH} "${XSD_FU_PYTHONPATH}")
endif()

execute_process(COMMAND ${XSD_FU} ${XSD_FU_COMMAND} --quiet --file-type=${XSD_FU_FILETYPE} ${XSD_FU_ARGS}
                RESULT_VARIABLE xsdfu_result)

if (xsdfu_result)
  message(FATAL_ERROR "xsd-fu: Failed to generate files for target ${XSD_FU_COMMAND} (${XSD_FU_FILETYPE}s): ${xsdfu_result}")
endif()

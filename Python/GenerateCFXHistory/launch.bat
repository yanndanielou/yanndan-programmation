@CALL ..\SET_PYTHON_HOME.bat


@CALL :LAUNCH_IN_ONCE_MULTITHREADS 4
@CALL :LAUNCH_IN_ONCE_MULTITHREADS 3
@CALL :LAUNCH_IN_ONCE_MULTITHREADS 2
@CALL :LAUNCH_IN_ONCE_MULTITHREADS 1

@CALL :LAUNCH_IN_ONCE_MULTITHREADS_TOP_200 4
@CALL :LAUNCH_IN_ONCE_MULTITHREADS_TOP_200 3
@CALL :LAUNCH_IN_ONCE_MULTITHREADS_TOP_200 2
@CALL :LAUNCH_IN_ONCE_MULTITHREADS_TOP_200 1

@rem @CALL :LAUNCH_IN_ONCE

@rem CALL :LAUNCH_CHUNK START 1 100
@rem :LAUNCH_CHUNK START 100 1000

@rem :CALL :LAUNCH_CHUNK START 0 2000
@rem :CALL :LAUNCH_CHUNK START 2001 4000
@rem :CALL :LAUNCH_CHUNK START 4001 6000
@rem :CALL :LAUNCH_CHUNK START 6001 10000
rem CALL :LAUNCH_CHUNK START 3001 10000


@GOTO :END_OF_FILE

:LAUNCH_IN_ONCE_MULTITHREADS_TOP_200
@SET number_of_threads=%1
@echo LAUNCH_IN_ONCE_MULTITHREADS with %number_of_threads% threads
@rem @CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py --number_of_threads %number_of_threads% --last_cfx_index 100
@CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py --number_of_threads %number_of_threads% --last_cfx_index 100 --do_not_open_website_and_treat_previous_results
@EXIT /B 0

:LAUNCH_IN_ONCE_MULTITHREADS
@SET number_of_threads=%1
@echo LAUNCH_IN_ONCE_MULTITHREADS with %number_of_threads% threads
@CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py --number_of_threads %number_of_threads%
@EXIT /B 0


:LAUNCH_IN_ONCE
@echo LAUNCH_IN_ONCE
@CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py
@EXIT /B 0

:LAUNCH_BY_CHUNKS

echo LAUNCH_BY_CHUNKS
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 0000 --last_cfx_index 1000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 1000 --last_cfx_index 2000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 2000 --last_cfx_index 3000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 3000 --last_cfx_index 4000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 4000 --last_cfx_index 5000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 5000 --last_cfx_index 6000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 6000
@EXIT /B 0

:LAUNCH_CHUNK
@SET FROM_=%2
@SET TO_=%3
@SET COMMAND_=%1
@Echo LAUNCH_CHUNK_BLOCKING from %2 to %3 with command %1
%COMMAND_% %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index %FROM_% --last_cfx_index %TO_%
@EXIT /B 0


:END_OF_FILE
@pause

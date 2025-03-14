CALL ..\SET_PYTHON_HOME.bat

CALL :LAUNCH_IN_ONCE

CALL :LAUNCH_CHUNK START 1 3000
CALL :LAUNCH_CHUNK START 3001 10000


@GOTO :END_OF_FILE

:LAUNCH_IN_ONCE

echo LAUNCH_IN_ONCE


echo CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py

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
SET FROM_=%2
SET TO_=%3
SET COMMAND_=%1
@Echo LAUNCH_CHUNK_BLOCKING from %2 to %3 with command %1

%COMMAND_% %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index %FROM_% --last_cfx_index %TO_%
@EXIT /B 0



:END_OF_FILE
pause

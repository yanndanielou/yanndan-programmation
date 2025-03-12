CALL ..\SET_PYTHON_HOME.bat
rem CALL %PYTHON_HOME%\python.exe save_cfx_webpage.py

rem call %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 0000 --last_cfx_index 0010
rem exit

rem call %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 0000 --last_cfx_index 1000
rem pause
rem exit
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 1000 --last_cfx_index 2000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 2000 --last_cfx_index 3000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 3000 --last_cfx_index 4000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 4000 --last_cfx_index 5000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 5000 --last_cfx_index 6000
start %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 6000
rem 
rem pause
rem exit
rem timeout /t 10
rem START %PYTHON_HOME%\python.exe save_cfx_webpage.py --first_cfx_index 1000 --last_cfx_index 2000
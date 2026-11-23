@CALL ..\SET_PYTHON_HOME.bat


@CALL %PYTHON_HOME%\python.exe  save_cfx_requests_to_files.py

timeout /t 1000
@CALL ..\SET_PYTHON_HOME.bat

@CALL %PYTHON_HOME%\python.exe  download_and_clean_dml.py

timeout /t 100

exit
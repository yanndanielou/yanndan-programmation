@CALL SET_PYTHON_HOME.bat

CALL :INSTALL_INTERNAL_PYTHON_LIB ShutTheBox
pause

rem CALL :INSTALL_INTERNAL_PYTHON_LIB Common
CALL :INSTALL_INTERNAL_PYTHON_LIB Logger
pause

@GOTO :END_OF_FILE


:INSTALL_INTERNAL_PYTHON_LIB
@Title install internal python library %1
@Echo install internal python library %1
call %PYTHON_HOME%\python.exe -m pip install -e %1
@EXIT /B 0

:INSTALL_WITH_MANUAL_FILE_COPYINTERNAL_PYTHON_LIB
@Title install internal python library %1
@Echo install internal python library %1
call %PYTHON_HOME%\python.exe -m pip install -e %1
@EXIT /B 0


:END_OF_FILE

@timeout /t 100
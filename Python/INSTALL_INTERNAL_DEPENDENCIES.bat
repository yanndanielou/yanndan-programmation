@CALL SET_PYTHON_HOME.bat

@CALL :UNINSTALL_INTERNAL_PYTHON_LIB ShutTheBox
@CALL :UNINSTALL_INTERNAL_PYTHON_LIB ExampleLibrary
@CALL :UNINSTALL_INTERNAL_PYTHON_LIB Logger
@CALL :UNINSTALL_INTERNAL_PYTHON_LIB Common
@CALL :UNINSTALL_INTERNAL_PYTHON_LIB Game

@timeout /t 5

CALL :UNINSTALL_UNKNWOWN_LIBS
rem exit
@timeout /t 5


@CALL :INSTALL_INTERNAL_PYTHON_LIB Common
@CALL :INSTALL_INTERNAL_PYTHON_LIB Logger
@CALL :INSTALL_INTERNAL_PYTHON_LIB Game
@CALL :INSTALL_INTERNAL_PYTHON_LIB ExampleLibrary
@CALL :INSTALL_INTERNAL_PYTHON_LIB ShutTheBox

@timeout /t 100

@GOTO :END_OF_FILE




:UNINSTALL_UNKNWOWN_LIBS
@Echo .
del %PYTHON_HOME%\Lib\site-packages\__editable__.UNKNOWN-0.0.0.pth
RD /S /Q %PYTHON_HOME%\Lib\site-packages\UNKNOWN-0.0.0.dist-info
@Echo .
@EXIT /B 0


:INSTALL_INTERNAL_PYTHON_LIB
@Echo .
@Title install internal python library %1
@Echo install internal python library %1
call %PYTHON_HOME%\python.exe -m pip install -e %1
@Echo .
@EXIT /B 0

:UNINSTALL_INTERNAL_PYTHON_LIB
@Echo .
@Title uninstall internal python library %1
@Echo uninstall internal python library %1
call %PYTHON_HOME%\python.exe -m pip uninstall %1 -y

del %PYTHON_HOME%\Lib\site-packages\__editable__.%1%*.pth
RD /S /Q %PYTHON_HOME%\Lib\site-packages\%1%-0.0.0.dist-info
@Echo .

@EXIT /B 0


:END_OF_FILE

@timeout /t 100
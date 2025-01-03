CALL :HANDLE_ONE_PROJECT DirectoryStats
CALL :HANDLE_ONE_PROJECT M3uToFreebox



@GOTO :END_OF_FILE



:HANDLE_ONE_PROJECT
CD %1

@RD /S /Q Dependencies
@MD Dependencies
@echo "" > Dependencies\__init__.py

CALL :COPY_DEPENDENCY Common
CALL :COPY_DEPENDENCY Logger
CD ..
@EXIT /B 0



:COPY_DEPENDENCY
@Echo install %1
@MD Dependencies\%1
ROBOCOPY ..\%1 Dependencies\%1 *.py
@EXIT /B 0


:END_OF_FILE

@timeout /t 100

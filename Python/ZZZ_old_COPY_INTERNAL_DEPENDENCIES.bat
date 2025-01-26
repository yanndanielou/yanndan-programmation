@SET SCRIPT_DIRECTORY=%CD%
@ECHO Execute script %SCRIPT_DIRECTORY%

CALL :HANDLE_ONE_PROJECT DirectoryStats
CALL :HANDLE_ONE_PROJECT M3uToFreebox
CALL :HANDLE_ONE_PROJECT Sandbox\multilanguage-application-tkinter



@GOTO :END_OF_FILE



:HANDLE_ONE_PROJECT
CD %1

@RD /S /Q Dependencies
@MD Dependencies
@echo "" > Dependencies\__init__.py

CALL :COPY_DEPENDENCY Common
CALL :COPY_DEPENDENCY Logger
rem CALL :CREATE_PYPROJECT_TOML
CD %SCRIPT_DIRECTORY%
@EXIT /B 0



:COPY_DEPENDENCY
@Echo install %1
@MD Dependencies\%1
ROBOCOPY %SCRIPT_DIRECTORY%\%1 Dependencies\%1 *.py
@EXIT /B 0

:____OLD____CREATE_PYPROJECT_TOML

echo [tool.pylint.'MESSAGES CONTROL'] > pyproject.toml
echo max-line-length = 130 >> pyproject.toml
@EXIT /B 0


:END_OF_FILE

@timeout /t 100

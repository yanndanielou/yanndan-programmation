set SIEMENS_SOURCES=M:\NEXT_PCC_V0_40_BLD

CALL next_common_env_variables_setting.bat

"%DEVENV_HOME%\devenv.exe" %SIEMENS_SOURCES%\ATSP\AF\AFP\Server\ServerApplication.sln

timeout /t 100
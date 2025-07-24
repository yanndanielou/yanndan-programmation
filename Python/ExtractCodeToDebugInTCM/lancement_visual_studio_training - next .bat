set SIEMENS_SOURCES=M:\NEXT_PCC_V0_40_BLD

CALL next_common_env_variables_setting.bat

"%DEVENV_HOME%\devenv.exe" %SIEMENS_SOURCES%\XT_PCC\AF\AF\Simulator\Training\AfTrainingApplication.sln

timeout /t 100
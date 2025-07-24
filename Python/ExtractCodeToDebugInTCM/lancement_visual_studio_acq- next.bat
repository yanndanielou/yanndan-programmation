set SIEMENS_SOURCES=M:\NEXT_PCC_V0_40_BLD

CALL next_common_env_variables_setting.bat


"%DEVENV_HOME%\devenv.exe" %GCL_AF%\Af\Acquisition\AfAcquisitionApplication.sln

timeout /t 100
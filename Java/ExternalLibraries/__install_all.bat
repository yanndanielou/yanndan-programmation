@echo off
setlocal EnableDelayedExpansion

set "exclude=__install_all.bat"


for %%x in (*.bat)do (
   rem echo %%x
   if %%x == __install_all.bat (
	Echo Ingore current file %~nx0
   )   else (
    Start %%x
   )
)

timeout /t 30
timeout /t 30
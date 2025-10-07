
@SET FULL_LINK=%1
@for /f "delims=" %%i in ("%FULL_LINK%") do @set "fileName=%%~nxi"

@echo Download file %fileName% from %FULL_LINK%, started at %DATE% %TIME% 


powershell -Command "(New-Object Net.WebClient).DownloadFile('%FULL_LINK%', '%fileName%')

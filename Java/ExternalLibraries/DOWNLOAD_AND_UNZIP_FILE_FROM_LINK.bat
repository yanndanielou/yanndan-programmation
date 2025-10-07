@SET FULL_LINK=%1
@for /f "delims=" %%i in ("%FULL_LINK%") do @set "fileName=%%~nxi"


@set fileNameLast3Digits=%fileName:~-3%
@set fileNameLast4Digits=%fileName:~-4%

Echo fileNameLast3Digits : %fileNameLast3Digits%
Echo fileNameLast4Digits : %fileNameLast4Digits%

@set fileNameWithoutExtension=%fileName:~0,-10%
IF .7z == %fileNameLast3Digits% set fileNameWithoutExtension=%fileName:~0,-3% & echo Extension found: .7z
IF .zip == %fileNameLast4Digits% set fileNameWithoutExtension=%fileName:~0,-4% & echo .zip

@echo fileName %fileName% 
@echo FULL_LINK %FULL_LINK% 
@echo fileNameWithoutExtension %fileNameWithoutExtension% 

timeout /t 1

@CALL DOWNLOAD_FILE_FROM_LINK %1
powershell -command "Expand-Archive -Force '%fileName%' '%fileNameWithoutExtension%'"


timeout /t 1
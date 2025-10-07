
CALL DOWNLOAD_FILE_FROM_LINK "https://dlcdn.apache.org/pdfbox/2.0.30/pdfbox-app-2.0.30.jar"


CALL DOWNLOAD_FILE_FROM_LINK "https://dlcdn.apache.org/pdfbox/3.0.1/pdfbox-app-3.0.1.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://dlcdn.apache.org/pdfbox/3.0.1/debugger-app-3.0.1.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://dlcdn.apache.org/pdfbox/3.0.1/preflight-app-3.0.1.jar"

powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/apache/pdfbox/archive/refs/heads/trunk.zip', 'pdfbox_trunk.zip')
powershell -command "Expand-Archive -Force 'pdfbox_trunk.zip' 'pdfbox_trunk'"



timeout /t 1

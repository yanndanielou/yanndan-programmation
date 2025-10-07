
start DOWNLOAD_AND_UNZIP_FILE_FROM_LINK.bat "https://download.java.net/java/GA/jdk21.0.1/415e3f918a1f4062a0074a2794853d0d/12/GPL/openjdk-21.0.1_windows-x64_bin.zip"
call DOWNLOAD_AND_UNZIP_FILE_FROM_LINK.bat "https://download2.gluonhq.com/openjfx/21.0.1/openjfx-21.0.1_windows-x64_bin-sdk.zip"
CALL DOWNLOAD_FILE_FROM_LINK.bat "https://repo1.maven.org/maven2/org/testfx/testfx-junit5/4.0.17/testfx-junit5-4.0.17.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://repo1.maven.org/maven2/org/testfx/testfx-core/4.0.17/testfx-core-4.0.17.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://repository.mulesoft.org/nexus/content/repositories/public/javax/script/script-api/1.0-osgi/script-api-1.0-osgi.jar"
CALL DOWNLOAD_FILE_FROM_LINK "http://www.java2s.com/Code/JarDownload/script/script-10.jar.zip"


CALL DOWNLOAD_FILE_FROM_LINK "https://repo1.maven.org/maven2/org/fuin/utils4j/0.12.0/utils4j-0.12.0.jar"

cd openjfx-21.0.1_windows-x64_bin-sdk\javafx-sdk-21.0.1
powershell -command "Expand-Archive -Force 'src.zip' 'src'"



timeout /t 1


CALL DOWNLOAD_FILE_FROM_LINK "https://repo1.maven.org/maven2/com/massisframework/j3d/java3d-core/1.6.0.1/java3d-core-1.6.0.1.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://repo1.maven.org/maven2/javax/vecmath/vecmath/1.5.2/vecmath-1.5.2.jar"
CALL DOWNLOAD_FILE_FROM_LINK https://repo1.maven.org/maven2/java3d/j3d-core-utils/1.3.1/j3d-core-utils-1.3.1.jar


echo read https://jogamp.org/wiki/index.php/Downloading_and_installing_JOGL
CALL DOWNLOAD_AND_UNZIP_FILE_FROM_LINK "https://jogamp.org/deployment/jogamp-current/archive/jogamp-all-platforms.7z"


timeout /t 1


start DOWNLOAD_AND_UNZIP_FILE_FROM_LINK.bat "https://oss.sonatype.org/content/groups/public/com/axway/ats/distrib/ats-distrib/4.1.0-SNAPSHOT/ats-distrib-4.1.0-20180928.101205-138.zip"
call DOWNLOAD_FILE_FROM_LINK.bat "https://oss.sonatype.org/content/groups/public/com/axway/ats/distrib/ats-distrib/4.1.0-SNAPSHOT/ats-distrib-4.1.0-20180928.101205-138.jar"
CALL DOWNLOAD_FILE_FROM_LINK "https://oss.sonatype.org/content/groups/public/com/axway/ats/distrib/ats-distrib/4.1.0-SNAPSHOT/ats-distrib-4.1.0-20180928.101205-138-sources.jar"
start DOWNLOAD_AND_UNZIP_FILE_FROM_LINK "https://oss.sonatype.org/content/groups/public/com/axway/ats/distrib/ats-distrib/4.1.0-SNAPSHOT/ats-distrib-4.1.0-20180928.101205-138-javadoc.zip"

timeout /t 1

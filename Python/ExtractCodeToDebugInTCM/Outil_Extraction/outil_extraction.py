import os
import zipfile
import sys
import logging
import param
import warnings
import traitement_json as jsonFunctions
import time
import getopt


def printAndLogInfo(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    print(log_timestamp + '\t' + toPrintAndLog)
    logging.info(toPrintAndLog)


def printAndLogCriticalAndKill(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    print(log_timestamp + '\t' + toPrintAndLog)
    logging.critical(toPrintAndLog)
    sys.exit(toPrintAndLog)


def configureLogger():
    logger_directory = "logs"

    if not os.path.exists(logger_directory):
        os.makedirs(logger_directory)

    logger_level = param.logger_level

    #print("Logger level:" + str(logger_level))

    logging.basicConfig(level=logger_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logger_directory + '\LogsOfCompression.log',
                        filemode='w')
    # logging.debug
    # logging.info
    # logging.warning
    # logging.error
    # logging.critical


def main(argv):

    configureLogger()

    
    
    list_arguments_names = ["json_config_file="]
        
    json_config_file = None
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:", list_arguments_names)
    except getopt.GetoptError as err:
        errorMessage = "Unsupported arguments list." + str(err) + " Allowed arguments:" + str(list_arguments_names) + ". Application stopped"
        printAndLogCriticalAndKill(errorMessage)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printAndLogInfo("Allowed arguments:" + str(list_arguments_names) + ". Application stopped")
            sys.exit()
        elif opt == "--json_config_file":
            json_config_file = arg
        else:
            printAndLogCriticalAndKill (" Option:" + opt + " unknown with value:" + opt + ". Allowed arguments:" + str(list_arguments_names) + ". Application stopped")

    # Path to the json config file.
    jsonPath = json_config_file
    if jsonPath == None:
        printAndLogCriticalAndKill("Missing argument " + str(list_arguments_names))

    # Gets filled with all the Files/Folders that will be in the zip
    filesToZip = set(sorted(jsonFunctions.getPathsFromJson(jsonPath)))
    printAndLogInfo("There are " + str(len(filesToZip)) + " files to zip")
    number_of_files_zipped = 0

    printAndLogInfo("Zipping files...")
    # Creates the zip with all the files needed.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        zip_file = zipfile.ZipFile(jsonFunctions.zipName, 'w', zipfile.ZIP_DEFLATED)
        for file in filesToZip:
            number_of_files_zipped  = number_of_files_zipped+1
            if number_of_files_zipped % 100 ==0:
                printAndLogInfo(str(number_of_files_zipped) + " files have been zipped")
            if not os.path.exists(str(file)):
                printAndLogInfo("Failed to zip file: " + str(file)); continue
            logging.debug("Zipping File: " + str(file))
            zip_file.write(file)

    printAndLogInfo("Zipping files done")
    # SUCCESS
    logging.info("\nZIPPED PATHS")
    for file in filesToZip:
        logging.info("filesToZip:" + file)
    printAndLogInfo("Files archived to '" + jsonFunctions.zipName + "'.")


if __name__ == "__main__":
    main(sys.argv[1:])

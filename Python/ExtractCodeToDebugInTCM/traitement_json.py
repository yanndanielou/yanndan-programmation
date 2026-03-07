import os
import sys
import json
import logging
import param
import time
from operator import itemgetter  


excudedExtensions = []
excludedPaths = []
reccursivePathsExcluded = set()
includedPaths = []
includedExtensions = []


# Name of the zip that will be created.
zipName = ""


def printAndLogInfo(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    print(log_timestamp + '\t' + toPrintAndLog)
    logging.info(toPrintAndLog)


def printAndLogCriticalAndKill(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    print(log_timestamp + '\t' + toPrintAndLog)
    logging.critical(toPrintAndLog)
    sys.exit(toPrintAndLog)


def fileHasExtension(fileName):
    return len(fileName.rsplit('.', 1)) == 2

def get_file_extension(fileName):
    file_extension = fileName.rsplit('.', 1)[1]
    return file_extension
    
def has_file_forbidden_extension(fileName):
    return get_file_extension(fileName) in excudedExtensions
    
def has_file_forbidden_path(filePath):
    return filePath in excludedPaths
    
def has_file_included_extension(fileName):
    return (includedExtensions == [] or get_file_extension(fileName) in includedExtensions)

# Declare the function to return all file paths of the particular directory
def collectFilePaths(dirName):
    printAndLogInfo("collectFilePaths: " + dirName)
    number_of_files = 0
    number_of_files_added = 0
    all_extensions = set()
    number_of_files_per_extension = {}
    # List to be filled with all the paths in the directory
    filePaths = []
    # Read all directory, subdirectories and file lists
    for root, directories, files in os.walk(dirName):
        root_as_str = str(root)
        file_forbidden_path = has_file_forbidden_path(root_as_str)
        logging.info("Root:" + root_as_str + ", number of directories:" + str(len(directories)) + ", NbOfFiles: " + str(len(files)) + ", file_forbidden_path:" + str(file_forbidden_path) )
        if  file_forbidden_path:
            if not (root_as_str in reccursivePathsExcluded):
                reccursivePathsExcluded.add(root_as_str)
                printAndLogInfo("Walking sub directories of excluded path " + root_as_str + " in order to exclude its sub folders")
                for  sub_root, sub_directories, sub_files in os.walk(root):
                    reccursivePathsExcluded.add(sub_root)
                    sub_root_str = str(sub_root)
                    logging.debug("All subdirectories of " +sub_root_str + " , which are: " + str(sub_directories) + " will be excluded. This folder  contains " + str(len(sub_files)) + " files that are ignored")
                    for sub_directory_to_forbid in sub_directories:
                        logging.debug("Also need to forbid directory " + sub_directory_to_forbid + " because parent directory "  + sub_root_str  + " is forbidden path")
                        excludedPaths.append(sub_root_str + "\\" + sub_directory_to_forbid)
                printAndLogInfo("All sub directories of excluded path " + root_as_str + " have been excluded. New number of excluded paths:" + str(len(excludedPaths)))
                        
        
        else:
            for fileName in files:
                number_of_files += 1
                #printAndLogInfo("NbOfFiles: " + str(number_of_files))
                # Creates the full filepath.
                filePath = os.path.join(root, fileName)
                logging.debug(filePath)
                # Checks if excluded extension or excluded file
                if fileHasExtension(fileName):
                    file_extension = get_file_extension(fileName)
                    if (not (file_extension in excudedExtensions or filePath in excludedPaths)
                        and has_file_included_extension(fileName)
                            and filePath not in includedPaths):
                        logging.debug("Add " + filePath)
                        filePaths.append(filePath)
                        all_extensions.add(file_extension)
                        number_of_files_added += 1
                        
                        if file_extension in number_of_files_per_extension:
                            number_of_files_per_extension[file_extension] = number_of_files_per_extension[file_extension] + 1
                        else:
                            number_of_files_per_extension[file_extension] = 1
                        
                # Not included in first if for code clarity
                elif (not fileHasExtension(fileName)) and (not has_file_forbidden_path(filePath)):
                        logging.debug("File added because no extension:" + filePath)
                        filePaths.append(filePath)
                        number_of_files_added += 1
                        file_extension = "No extension"
                        if file_extension in number_of_files_per_extension:
                            number_of_files_per_extension[file_extension] = number_of_files_per_extension[file_extension] + 1
                        else:
                            number_of_files_per_extension[file_extension] = 1
            """for directory in directories:
            dirPath = os.path.join(root, directory)
            if dirPath not in includedPaths and dirPath not in excludedPaths:
                filePaths.append(dirPath)"""
    printAndLogInfo(str(number_of_files) + " files found and " + str(number_of_files_added) + " files added")
    printAndLogInfo("Extensions found:" + (", ".join(all_extensions)))
    #printAndLogInfo("Number of files per extension:" + str(sorted(number_of_files_per_extension, key=number_of_files_per_extension.get, reverse=True)))
    
    for key, value in sorted(number_of_files_per_extension.items(), key = itemgetter(1), reverse = True):
        printAndLogInfo("Number of files for extension " + key + " : " + str(value))
    
    # return all paths
    return filePaths


# Returns list of all path to folders
def handleFolders(folderPath):
    if not os.path.isdir(folderPath):
        printAndLogCriticalAndKill("Path is not a folder: " + str(folderPath))
    return collectFilePaths(folderPath)


# Returns a list containing the file after looking for errors
def handleFiles(filePath):
    if not os.path.isfile(filePath):
        printAndLogCriticalAndKill("Path is not a file: " + str(filePath))
    return filePath


# This function takes the Json content
def getDataFromJson(jsonContent, dataType):

    # Checks if the datatype is present in Json. ("IncludedPaths", "ExcludedExtensions" or "ExcludedPaths")
    if dataType not in jsonContent:
        return -1

    for elem in jsonContent[dataType]:

        # Adds files and folders paths to the includedPaths List and checks exceptions.
        if dataType == "IncludedPaths":
            for key in elem:
                if key.lower() == "folder":
                    includedPaths.extend(handleFolders(elem[key]))
                elif key.lower() == "file":
                    not elem[key] in includedPaths and includedPaths.append(str(handleFiles(elem[key])))
                else:
                    printAndLogCriticalAndKill("Json has unknown key in IncludedPaths: " + str(key))

        # Adds excluded extensions to the excludedExtensions List and checks exceptions.
        elif dataType == "ExcludedExtensions":
            for key in elem:
                if key.lower() == "extension":
                    excudedExtensions.append(str(elem[key]))
                else:
                    printAndLogCriticalAndKill("Json has unknown key in ExcludedExtensions: " + str(key))

        # Adds excluded files paths to the excludedPaths List and checks exceptions.
        elif dataType == "ExcludedPaths":
            for key in elem:
                if key.lower() == "file" or key.lower() == "folder":
                    excludedPaths.append(str(elem[key]))
                else:
                    printAndLogCriticalAndKill("Json has unknown key in ExcludedPaths: " + str(key))

        # Adds included extensions to the includedExtensions List and checks exceptions
        elif dataType == "IncludedExtensions":
            for key in elem:
                if key.lower() == "extension":
                    includedExtensions.append(elem[key])
                else:
                    printAndLogCriticalAndKill("Json has unknown key in IncludedExtensions: " + str(key))
        else:
            printAndLogCriticalAndKill("Json has unknown key: " + str(dataType))


def formatJson(jsonTab):
    if "ExcludedExtensions" not in jsonTab:
        pass
    if "IncludedExtensions" not in jsonTab:
        pass
    if "ExcludedPaths" not in jsonTab:
        pass
    if "IncludedPaths" not in jsonTab:
        printAndLogCriticalAndKill("Missing 'IncludedPaths' field in Json file.")


# "main" function called in "outil_extraction", iterates through the Json and calls other functions on each element
def getPathsFromJson(jsonFile):

    # Exception cases if file not found or is not a Json
    global zipName
    if not os.path.exists(jsonFile):
        printAndLogCriticalAndKill("Json file not found")
    if not jsonFile.endswith(".json"):
        printAndLogCriticalAndKill("Please provide a .json file")

    # Opens Json and stores its data in 'jsonContent' as a Dict
    file = open(jsonFile, "r")
    textContent = file.read()
    file.close()
    jsonContent = json.loads(textContent)

    for jsonTab in jsonContent:
        if "Zipname" in jsonTab:
            if len(jsonTab) > 1:
                printAndLogCriticalAndKill("Invalid Json, 'Zipname' should be the only parameter in his section")
            zipName += jsonTab["Zipname"]

        printAndLogInfo("zipName:" + zipName)
            
        # Fills the excludedExtensions List
        getDataFromJson(jsonTab, "ExcludedExtensions")

        # Fills the excludedPaths List
        getDataFromJson(jsonTab, "ExcludedPaths")

        # Fills the includedExtensions List
        getDataFromJson(jsonTab, "IncludedExtensions")

        # Fills the includedPaths List with path and extensions that are not excluded
        getDataFromJson(jsonTab, "IncludedPaths")

        excudedExtensions.clear()
        excludedPaths.clear()
        includedExtensions.clear()

    return includedPaths



# print("Extensions: " + str(extensionsz))
# print("ExcludedPaths: " + str(excludedPaths))
# print("IncludedPaths: " + str(includedPaths))
# -*-coding:Utf-8 -*
#
#
# Input: file with columns
#metric_name,metric_timestamp,_value
#project.mesure,2024-07-15T00:25:46.992+03:00,"-1"
#
# Output: file with columns
#metric_timestamp,metric_name,_value
#2024-06-12T00:43:37.495+00:00,Computer.LogicalDisk_D.Free_Space,73.252541527397269761

import Dependencies.Logger.LoggerConfig as LoggerConfig

import subprocess
import glob
import os
from os.path import basename
import sys

import random

import zipfile

import re

import csv

import param
import metric

import pandas

import shutil

import queue
import threading
import time

#import datetime
import time

 
def get_metric_file_content_lines_from_metrics(metrics):
    splunk_ready_file_content_as_list = list()
    splunk_ready_file_content_as_list.append("metric_timestamp,metric_name,_value")

    for metric in metrics:
        splunk_ready_file_content_as_list.append(metric._time_stamp + "," + metric._name + "," + metric._value_as_string)

    return splunk_ready_file_content_as_list
    

def process_input_zip_files(input_zip_files):
    LoggerConfig.print_and_log_info("process_input_zip_files")
    for input_zip_file in input_zip_files:
        process_input_zip_file( input_zip_file)


def process_input_zip_file(input_zip_file):
    LoggerConfig.print_and_log_info("process_input_zip_files")

    LoggerConfig.print_and_log_info("processing " + basename(input_zip_file))

    input_zip_file_file_name = basename(input_zip_file)
    LoggerConfig.print_and_log_info("File name:" + input_zip_file_file_name)
    
    input_zip_file_directory_name = os.path.dirname(input_zip_file)    
    LoggerConfig.print_and_log_info("Directory name:" + input_zip_file_directory_name)
    
    input_zip_file_file_without_extension = os.path.splitext(input_zip_file_file_name)[0]
    LoggerConfig.print_and_log_info("File name without extension:" + input_zip_file_file_without_extension)
    
    temp_folder_name = "temp_" + input_zip_file_file_without_extension
    
    temp_folder_full_path_name = param.output_metrics_ready_for_splunk_directory + "\\" + temp_folder_name
    
    if os.path.exists(temp_folder_full_path_name):
        LoggerConfig.print_and_log_info("\t" + "Removing:" + temp_folder_full_path_name + ". Previous execution of the tool was probably interrupted")
        shutil.rmtree(temp_folder_full_path_name, ignore_errors=False, onerror=None)
        
    os.makedirs(temp_folder_full_path_name)
    
    LoggerConfig.print_and_log_info("extract to temporary folder")
    subprocess.call(r'"C:\Program Files\7-Zip\7z.exe" e ' + "\"" + input_zip_file + "\"" + ' -o' + "\"" + temp_folder_full_path_name + "\"")
    LoggerConfig.print_and_log_info("Extraction done")
    
    output_zip_file_name = input_zip_file_file_without_extension.replace("_actual","")
    if len(param.metric_name_fixed_prefix_for_all_mesures) > 0:
        output_zip_file_name = output_zip_file_name + "_" + param.metric_name_fixed_prefix_for_all_mesures
    
    output_zip_file_name = output_zip_file_name + param.output_files_suffix + "_splunk." +  param.output_files_extension
    output_zip_file = zipfile.ZipFile(param.output_metrics_ready_for_splunk_directory + "\\" + output_zip_file_name,'w')
    
    LoggerConfig.print_and_log_info("Convert all performance_counter_log to csv")
    
    for performance_counter_log_file in glob.glob(temp_folder_full_path_name + "\\*.csv"):
        handle_performance_counter_log_file(performance_counter_log_file, temp_folder_full_path_name, output_zip_file)

    #Close the zip
    LoggerConfig.print_and_log_info("Zip DONE")
    output_zip_file.close()            
        
    LoggerConfig.print_and_log_info("Remove temporary directory:" + temp_folder_full_path_name)
    shutil.rmtree(temp_folder_full_path_name)


def convert_performance_counter_log_file_to_metric_file( performance_counter_log_file_file_name, performance_counter_log_file_full_path):
    LoggerConfig.print_and_log_info( "Convert performance_counter_log file:" + performance_counter_log_file_file_name)  

    LoggerConfig.print_and_log_info( "Open file to tranform: " + performance_counter_log_file_full_path)        
    performance_counter_log_file_pandas_data = pandas.read_csv(performance_counter_log_file_full_path)  

    # Obtenir la liste des noms de colonnes
    performance_counter_log_file_pandas_columns_names = performance_counter_log_file_pandas_data.columns

    #metric_name,metric_timestamp,_value
    metrics = list()
    # Itérer sur les lignes du DataFrame
    for index, row in performance_counter_log_file_pandas_data.iterrows():
        
        # Itérer sur les cellules de la ligne courante en utilisant les noms des colonnes
        original_time_stamp = row["metric_timestamp"]
        original_value = row["_value"]
        original_metric_name = row['metric_name']

        value = str(original_value)
        metricCreated = metric.Metric(original_time_stamp, original_metric_name, value)
        metrics.append(metricCreated)

    return metrics
    
def handle_performance_counter_log_file( performance_counter_log_file_full_path, temp_folder_full_path_name, output_zip_file: zipfile.ZipFile):
    performance_counter_log_file_file_name = basename(performance_counter_log_file_full_path)        
    performance_counter_log_file_without_extension = os.path.splitext(performance_counter_log_file_file_name)[0]
    
    metrics = convert_performance_counter_log_file_to_metric_file( performance_counter_log_file_file_name, performance_counter_log_file_full_path)
    LoggerConfig.print_and_log_info("Number of metrics created:" + str(len(metrics)))

    metric_file_content_lines = get_metric_file_content_lines_from_metrics(metrics)
    LoggerConfig.print_and_log_info("Metric file content computed")
    

    splunk_ready_file_name = performance_counter_log_file_without_extension + "_as_splunk_metric.csv"
    splunk_ready_file_full_path =  temp_folder_full_path_name + "\\" + splunk_ready_file_name

    
    splunk_ready_file_full_path = create_splunk_ready_metric_file(splunk_ready_file_full_path, metric_file_content_lines)

    # add to zip
    add_splunk_ready_metric_file_to_zip(output_zip_file, splunk_ready_file_full_path, splunk_ready_file_name)

    os.remove(splunk_ready_file_full_path)
 
def create_splunk_ready_metric_file( splunk_ready_file_name, splunk_ready_file_content_as_list):
    LoggerConfig.print_and_log_info( "Create final Splunk ready file: " + splunk_ready_file_name)    
    splunk_ready_file = open(splunk_ready_file_name, "w")

    LoggerConfig.print_and_log_info( "Fill final Splunk ready file: " + splunk_ready_file_name)    
    splunk_ready_file_content = param.end_line_character_in_text_file.join(splunk_ready_file_content_as_list)
    splunk_ready_file.write(splunk_ready_file_content)

    LoggerConfig.print_and_log_info( "Close final Splunk ready file:" + splunk_ready_file_name)
    splunk_ready_file.close()
    
    return splunk_ready_file_name
 

def add_splunk_ready_metric_file_to_zip(output_zip_file: zipfile.ZipFile, splunk_ready_file_full_path, splunk_ready_file_name):
    output_zip_file.write(splunk_ready_file_full_path, arcname=splunk_ready_file_name, compress_type=zipfile.ZIP_DEFLATED)
            
def main(argv):

    log_file_name = os.path.basename(__file__) + str(random.randrange(100000)) + ".log"
    LoggerConfig.configureLogger(log_file_name)    
    
    LoggerConfig.print_and_log_info('Start application')
    
    # Get the list of input zips

    input_zip_files = glob.glob(param.input_files_directory + "\\*.zip")
    input_7z_files = glob.glob(param.input_files_directory + "\\*.7z")
    
    LoggerConfig.print_and_log_info('input_zip_files:' + ",".join(input_zip_files))
    LoggerConfig.print_and_log_info('input_7z_files:' + ",".join(input_7z_files))

    input_files = input_zip_files+input_7z_files
       
    LoggerConfig.print_and_log_info('input_files:' + ",".join(input_zip_files))
        
    process_input_zip_files(input_files)
    

    LoggerConfig.print_and_log_info("Exiting main thread")

    
    LoggerConfig.print_and_log_info("End. Nominal end of application")
    

if __name__ == "__main__":
   main(sys.argv[1:])
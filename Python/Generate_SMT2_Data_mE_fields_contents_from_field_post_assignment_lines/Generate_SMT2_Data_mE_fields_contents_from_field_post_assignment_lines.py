# -*-coding:Utf-8 -*

#For logs
import random
import logging
import os
import sys

# To get line number for logs
from inspect import currentframe, getframeinfo
import inspect

#Dates
import datetime
import time

#Reges
import re

#param
end_line_character_in_text_file = "\n"
input_SMT2_Data_mE_file_name = "SMT2_Data_mE.m"
logger_level = logging.INFO


#Constants
matlab_line_continuation_operator = "..."
matlab_return_operator = "return"
matlab_field_separator = ","
matlab_end_instruction_separator = ";"
matlab_structure_fields_table_begin = "{"
matlab_structure_fields_table_end = "}"
matlab_structure_field_end = "}"
matlab_structure_operator = "struct"
matlab_structure_begin = matlab_structure_operator + "("
matlab_empty_array_field = "[]"

def print_and_log_critical_and_kill(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    
    previous_stack = inspect.stack(1)[1]
    line_number = previous_stack.lineno

    print(log_timestamp + '\t' + "line#" + str(line_number) + '\t' +toPrintAndLog)
    logging.critical("line#" + str(line_number) + '\t' +toPrintAndLog)
    sys.exit()

def print_and_log_info(toPrintAndLog):
    
    log_timestamp = time.asctime( time.localtime(time.time()))

    previous_stack = inspect.stack(1)[1]
    line_number = previous_stack.lineno

    print(log_timestamp + '\t' + "line#" + str(line_number) + '\t' + str() + toPrintAndLog)
    logging.info("line#" + str(line_number) + '\t' +toPrintAndLog)
    
    
def print_and_log_warning(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))

    previous_stack = inspect.stack(1)[1]
    line_number = previous_stack.lineno

    print(log_timestamp + '\t' + "line#" + str(line_number) + '\t' +toPrintAndLog)
    logging.warning("line#" + str(line_number) + '\t' +toPrintAndLog)
    
def print_and_log_error(toPrintAndLog):
    log_timestamp = time.asctime( time.localtime(time.time()))
    
    previous_stack = inspect.stack(1)[1]
    line_number = previous_stack.lineno

    print(log_timestamp + '\t' + "!!ERROR!!")
    print(log_timestamp + '\t' "line#" + str(line_number))
    print(log_timestamp + '\t' + toPrintAndLog)
    logging.error("line#" + str(line_number) + '\t' +toPrintAndLog)

    
def configureLogger(log_file_name):
    logger_directory = "logs"
    
    if not os.path.exists(logger_directory):
        os.makedirs(logger_directory)
    
    print(time.asctime( time.localtime(time.time())) + '\t' + "Logger level:" +str(logger_level))
    
    logging.basicConfig(level=logger_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logger_directory+ '\\' + log_file_name,
                        filemode='w')
    #logging.debug
    #logging.info
    #logging.warning
    #logging.error
    #logging.critical

class execution_time(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        logging.info("Entering " +  self.f.__name__)
        logging.debug("Arguments passed to " + self.f.__name__ + ":" + str(locals()))
        start_time = time.time()
        
        #Call method
        ret = self.f(*args)
    
        elapsed_time = time.time() - start_time    
        logging.info("Exited " +  self.f.__name__ + ". Elapsed:" + format(elapsed_time, '.2f') + " s")
        return ret

class TableFieldInMainStructureModificationInstruction:

    def __init__(self):
        self.full_content_as_string = None

        self.main_structure_name = None
        self.main_structure_index = None
        self.field_name = None
        self.field_index_1 = None
        self.field_index_2 = None
        self.new_value = None

    def build_from_string_and_regex(self, full_content_as_string, match_result):
        self.full_content_as_string = full_content_as_string

        self.main_structure_name = match_result.group("main_structure_name")
        self.main_structure_index = int(match_result.group("main_structure_index"))
        self.field_name = match_result.group("field_name")
        self.field_index_1 = int(match_result.group("field_index_1"))
        self.field_index_2 = int(match_result.group("field_index_2"))
        self.new_value = int(match_result.group("new_value"))


    def build_from_fields_values(self, full_content_as_string, main_structure_name, main_structure_index, field_name, field_index_1, field_index_2, new_value):
        self.full_content_as_string = full_content_as_string

        self.main_structure_name = main_structure_name
        self.main_structure_index = main_structure_index
        self.field_name = field_name
        self.field_index_1 = field_index_1
        self.field_index_2 = field_index_2
        self.new_value = new_value

class Level2FieldContent:
    def __init__(self, parent):
        self.parent = parent
        self.assingment_instructions = list()

class Level1FieldContent:
    def __init__(self, parent):
        self.parent = parent
        self.assingment_instructions = list()
        self.level2FieldContents = list()

    def compute_level_2_fields(self):

        for assingment_instruction in self.assingment_instructions:
            field_index_2 = assingment_instruction.field_index_2
            
            level2FieldContent = None
            while len(self.level2FieldContents) < field_index_2:
                 level2FieldContent = Level2FieldContent(self)
                 self.level2FieldContents.append(level2FieldContent)
            else:
                level2FieldContent = self.level2FieldContents[field_index_2-1]

            level2FieldContent.assingment_instructions.append(assingment_instruction)

class StructureSpecifcIndex:
    def __init__(self, parent):
        self.fields = list()
        self.last_index_computed = None
        self.assingment_instructions = list()
        self.max_dimension1 = None
        self.max_dimension2 = None
        self.parent = parent
        self.level1FieldContents = list()
        self.max_index_of_level_2_field_from_all_level_one_fields = None


    """
    def create_tables_for_empty_fields_depending_on_dimension(self):

        #self.fields = list()
        #current_fields = self.fields

        for i in range(0, self.max_dimension1):
            self.fields.append(list())
            for j in range(1, self.max_dimension2):
                self.fields[len(self.fields)-1].append(list())

      def fill_fields_until_size(self, new_size):

        while len(self.fields) < new_size - 1:
            self.fields.append(list())
    """

    def compute_max_dimension_of_level_2_fields(self):
        self.max_index_of_level_2_field_from_all_level_one_fields = 0
        
        for level1FieldContent in self.level1FieldContents:
            for level2FieldContent in level1FieldContent.level2FieldContents:
                for assingment_instruction in level2FieldContent.assingment_instructions:
                    if assingment_instruction.field_index_2 > self.max_index_of_level_2_field_from_all_level_one_fields:
                        self.max_index_of_level_2_field_from_all_level_one_fields = assingment_instruction.field_index_2

    def align_all_level_1_field_to_same_dimension_based_on_max_level_2_field(self):
        level1FieldContent_number = 0
        for level1FieldContent in self.level1FieldContents:
            level1FieldContent_number += 1
            while len(level1FieldContent.level2FieldContents) < self.max_index_of_level_2_field_from_all_level_one_fields:
                full_content_as_string = "created by align_all_level_1_field_to_same_dimension_based_on_max_level_2_field"
                main_structure_name = self.parent.parent.name
                main_structure_index = None
                field_name = self.parent.name
                field_index_1 = level1FieldContent_number
                field_index_2 = len(level1FieldContent.level2FieldContents)
                new_value  = 0

                level2FieldContent = Level2FieldContent(level1FieldContent)
                assingment_instruction = TableFieldInMainStructureModificationInstruction()
                assingment_instruction.build_from_fields_values(full_content_as_string, main_structure_name, main_structure_index, field_name, field_index_1, field_index_2, new_value)
                level2FieldContent.assingment_instructions.append(assingment_instruction)
                level1FieldContent.level2FieldContents.append(level2FieldContent)


    def compute_max_dimensions(self):

        self.max_dimension1 = 0
        self.max_dimension2 = 0

        for assingment_instruction in self.assingment_instructions:
            if assingment_instruction.field_index_1 > self.max_dimension1:
                self.max_dimension1 = assingment_instruction.field_index_1
            if assingment_instruction.field_index_2 > self.max_dimension2:
                self.max_dimension2 = assingment_instruction.field_index_2

    def compute_level_1_fields(self):
        for assingment_instruction in self.assingment_instructions:
            field_index_1 = assingment_instruction.field_index_1
            field_index_2 = assingment_instruction.field_index_2
            
            level1FieldContent = None
            while len(self.level1FieldContents) < field_index_1:
                 level1FieldContent = Level1FieldContent(self)
                 self.level1FieldContents.append(level1FieldContent)
            else:
                level1FieldContent = self.level1FieldContents[field_index_1-1]

            level1FieldContent.assingment_instructions.append(assingment_instruction)
    
    def compute_level_2_fields(self):

        for level1FieldContent in self.level1FieldContents:
            level1FieldContent.compute_level_2_fields()

    """
    def compute_fields_old(self):

        for assingment_instruction in self.assingment_instructions:
            field_index_1 = assingment_instruction.field_index_1
            field_index_2 = assingment_instruction.field_index_2
            
            table =  self.fields[field_index_1-1]

            while len(table) < field_index_2 - 1:
                table.append(list())

            #if len(table) != field_index_2 - 1:
            #    print_and_log_critical_and_kill("Error when assigning " + assingment_instruction.full_content_as_string + " in " + str(table))

            table.append(assingment_instruction.new_value)

        end_of_function=1
#class FieldOfStructureWithModificationInstruction:
    """

class FieldOfStructureWithModificationInstruction:
    def __init__(self, name, parent):
        self.name = name
        self.last_index_computed = None
        self.array_items_by_structure_indice = list()
        self.parent = parent
        print_and_log_info("Create " + self.__class__.__name__ + " created with name:" + self.name)

    def add_assignment_instructions(self, tableFieldInMainStructureModificationInstruction):
        main_structure_index_starting_at_0 = tableFieldInMainStructureModificationInstruction.main_structure_index - 1
        arrayItemOfFieldOfStructureWithModificationInstruction = None
        
        if tableFieldInMainStructureModificationInstruction.main_structure_index > len(self.array_items_by_structure_indice):
            arrayItemOfFieldOfStructureWithModificationInstruction = StructureSpecifcIndex(self)
            self.array_items_by_structure_indice.append(arrayItemOfFieldOfStructureWithModificationInstruction)
        else:
            arrayItemOfFieldOfStructureWithModificationInstruction = self.array_items_by_structure_indice[main_structure_index_starting_at_0]

        arrayItemOfFieldOfStructureWithModificationInstruction.assingment_instructions.append(tableFieldInMainStructureModificationInstruction)
    

    def save_field(self, file_content_as_list_of_lines, in_one_line):
        file_content_as_list_of_lines_in_multiple_lines = list()

        file_content_as_list_of_lines_in_multiple_lines.append(",{...")

        content_as_string_in_one_line = ""


        structure_indice_number = 0
        for array_item_of_structure_indice in self.array_items_by_structure_indice:
            structure_indice_number += 1

            current_item_content_as_string = ""

            if array_item_of_structure_indice.max_index_of_level_2_field_from_all_level_one_fields > 1:
                current_item_content_as_string += "["


            level_1_field_content_number = 0
            for level_1_field_content in array_item_of_structure_indice.level1FieldContents:
                level_1_field_content_number += 1
                
                if len(level_1_field_content.level2FieldContents) > 1:
                    current_item_content_as_string += "["
                
                level_2_field_content_number = 0
                for level_2_field_content in level_1_field_content.level2FieldContents:
                    level_2_field_content_number += 1

                    #content_as_string += "["

                    assingment_instruction_number = 0
                    for assingment_instruction in level_2_field_content.assingment_instructions:
                        assingment_instruction_number += 1
                        #current_item_content_as_string += "["
                        current_item_content_as_string +=  str(assingment_instruction.new_value)
                        #current_item_content_as_string += "]"
                        
                        if assingment_instruction_number > 1:
                            print_and_log_critical_and_kill("assingment_instruction_number" + str(assingment_instruction_number))

                    #content_as_string += "]"

                    if level_2_field_content_number < len(level_1_field_content.level2FieldContents):
                        current_item_content_as_string += ","

                
                if len(level_1_field_content.level2FieldContents) > 1:
                    current_item_content_as_string += "]"

                if level_1_field_content_number < len(array_item_of_structure_indice.level1FieldContents):
                    current_item_content_as_string += ";"


            if array_item_of_structure_indice.max_index_of_level_2_field_from_all_level_one_fields > 1:
                current_item_content_as_string += "]"

            if structure_indice_number <  len(self.array_items_by_structure_indice) :
                file_content_as_list_of_lines_in_multiple_lines.append(current_item_content_as_string + ",...")
                
                content_as_string_in_one_line += ","
            else:
                file_content_as_list_of_lines_in_multiple_lines.append(current_item_content_as_string+ "...")
                file_content_as_list_of_lines_in_multiple_lines.append("}...")
                
                content_as_string_in_one_line += "}"


                last_line=1
            
            content_as_string_in_one_line += current_item_content_as_string


        if in_one_line:
            file_content_as_list_of_lines.append(content_as_string_in_one_line)
        else:
            file_content_as_list_of_lines += file_content_as_list_of_lines_in_multiple_lines

        end_of_save_field = 1


    """
    def save_field_old(self, file_content_as_list_of_lines):
        content_as_string = ""

        array_item_number = 0
        for array_item in self.array_items_by_structure_indice:
            if array_item.max_dimension1 > 1:
                content_as_string += "["

            array_item_number += 1
            array_item_as_string = str(array_item.fields)
            
            field_number = 0
            for field in array_item.fields:
                field_number += 1

                content_as_string += str(field)

                if field_number < len (array_item.fields):
                    content_as_string += " "

                    
            if array_item.max_dimension1 > 1:
                content_as_string += "]"
                    
            if array_item_number < len (self.array_items_by_structure_indice):
                content_as_string += ","

        file_content_as_list_of_lines.append("content of field " + self.name + " for structure:" + self.parent.name)
        file_content_as_list_of_lines.append(content_as_string)
        file_content_as_list_of_lines.append("")

        print_and_log_info("Print content of field " + self.name + " for structure:" + self.parent.name + " = " + content_as_string[:60] + ", ...,  etc.")
        logging.debug("Print content of field " + self.name + " for structure:" + self.parent.name + " = " + content_as_string)

        
    """

class StructureWithModificationInstruction:
    def __init__(self, name):
        self.fields = list()
        self.name = name
        print_and_log_info("Create " + self.__class__.__name__ + " created with name:" + self.name)

class SMT2_Data_mE_Content:

    def __init__(self):
        self.tableFieldInMainStructureModificationInstructions = list()
        self.structureFieldInMainStructureModificationInstructionLines = list()
        self.structuresWithModificationInstructions = list()

    def create_structure_fields_objects(self):
        for tableFieldInMainStructureModificationInstruction in self.tableFieldInMainStructureModificationInstructions:
            structureWithModificationInstruction = None
            #check if there is already a known structure
            for structureWithModificationInstructionIt in self.structuresWithModificationInstructions:
                if structureWithModificationInstructionIt.name == tableFieldInMainStructureModificationInstruction.main_structure_name:
                    structureWithModificationInstruction = structureWithModificationInstructionIt

            if structureWithModificationInstruction is None:
                structureWithModificationInstruction = StructureWithModificationInstruction(tableFieldInMainStructureModificationInstruction.main_structure_name)  
                self.structuresWithModificationInstructions.append(structureWithModificationInstruction)

            #check if there is already a known field
            fieldOfStructureWithModificationInstruction = None
            for fieldWithModificationInstructionIt in structureWithModificationInstruction.fields:
                if fieldWithModificationInstructionIt.name == tableFieldInMainStructureModificationInstruction.field_name:
                    fieldOfStructureWithModificationInstruction = fieldWithModificationInstructionIt

            if fieldOfStructureWithModificationInstruction is None:
                fieldOfStructureWithModificationInstruction = FieldOfStructureWithModificationInstruction(tableFieldInMainStructureModificationInstruction.field_name, structureWithModificationInstruction)  
                structureWithModificationInstruction.fields.append(fieldOfStructureWithModificationInstruction)

            fieldOfStructureWithModificationInstruction.add_assignment_instructions(tableFieldInMainStructureModificationInstruction)

    def fill_structure_fields_objects(self):
        print_and_log_info("fill_structure_fields_objects")
        
        print_and_log_info("compute_max_dimensions")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.compute_max_dimensions()

        """         print_and_log_info("create_tables_for_empty_fields_depending_on_dimension")
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.create_tables_for_empty_fields_depending_on_dimension() 
        

        print_and_log_info("compute_fields_old")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.compute_fields_old()
        """
        print_and_log_info("compute_level_1_fields")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.compute_level_1_fields()

        print_and_log_info("compute_level_2_fields")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.compute_level_2_fields()

        print_and_log_info("compute_max_dimension_of_level_2_fields")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.compute_max_dimension_of_level_2_fields()

        print_and_log_info("align_all_level_1_field_to_same_dimension_based_on_max_level_2_field")                
        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
                    array_item.align_all_level_1_field_to_same_dimension_based_on_max_level_2_field()
                    
        # for structureWithModificationInstruction in self.structuresWithModificationInstructions:
        #     for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
        #         for array_item in fieldWithModificationInstruction.array_items_by_structure_indice:
        #             array_item.fill_fields_until_size(7042)

    def save_results(self, file_content_as_list_of_lines):
        print_and_log_info("save_results")

        for structureWithModificationInstruction in self.structuresWithModificationInstructions:
            file_content_as_list_of_lines.append("Structure:" + structureWithModificationInstruction.name)

            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                file_content_as_list_of_lines.append("Structure:" + structureWithModificationInstruction.name + " field:" + fieldWithModificationInstruction.name + " in multiple lines") 
                #fieldWithModificationInstruction.save_field_old(file_content_as_list_of_lines)
                fieldWithModificationInstruction.save_field(file_content_as_list_of_lines, False)

                
            for fieldWithModificationInstruction in structureWithModificationInstruction.fields:
                file_content_as_list_of_lines.append("Structure:" + structureWithModificationInstruction.name + " field:" + fieldWithModificationInstruction.name + " in one line") 
                #fieldWithModificationInstruction.save_field_old(file_content_as_list_of_lines)
                fieldWithModificationInstruction.save_field(file_content_as_list_of_lines, True)

        file_content_as_list_of_lines.append("")
        file_content_as_list_of_lines.append("structureFieldInMainStructureModificationInstructionLines:")
        file_content_as_list_of_lines += self.structureFieldInMainStructureModificationInstructionLines


def open_text_file_and_return_lines(input_file_name):  
    logging.info('Check existence of input file:' + input_file_name)

    if not os.path.exists(input_file_name):
        logging.critical("Input file:" + input_file_name + " does not exist. Application stopped")
        sys.exit()

    print_and_log_info('Full path:' + os.path.abspath(input_file_name))


    print_and_log_info('Opening input file:' + input_file_name)    
    input_file = open(input_file_name, "r")
    
    print_and_log_info('Read input file:' + input_file_name)
    input_file_read = input_file.read()
    
    print_and_log_info('Close input file:' + input_file_name)
    input_file.close()

    input_file_lines = input_file_read.split(end_line_character_in_text_file)
    print_and_log_info(input_file_name + " has " + str(len(input_file_lines)) + " lines")

    return input_file_lines
 

def load_SMT2_Data_mE(sMT2_Data_mE_file_name, sMT2_Data_mE_Content):
    sMT2_Data_mE_file_lines = open_text_file_and_return_lines(sMT2_Data_mE_file_name)

    table_field_of_main_structure_modification_instruction_line_regex_as_string = "(?P<main_structure_name>[0-9A-Za-z_]*)[(](?P<main_structure_index>\\d+)[)][.](?P<field_name>[0-9A-Za-z_]*)[(](?P<field_index_1>\\d+)[,](?P<field_index_2>\\d+)[)]\s[=]\s(?P<new_value>-?\\d+)[;]"
    table_field_of_main_structure_modification_instruction_line_regex_compiled = re.compile(table_field_of_main_structure_modification_instruction_line_regex_as_string)
        
    structure_field_of_main_structure_modification_instruction_line_regex_as_string = "(?P<main_structure_name>[0-9A-Za-z_]*)[(](?P<main_structure_index>\\d+)[)][.](?P<second_level_structure_name>[0-9A-Za-z_]*)[(](?P<second_level_structure_index>\\d+)[)][.](?P<field_name>[0-9A-Za-z_]*)[(](?P<field_index>\\d+)[)]\s[=]\s(?P<new_value>-?\\d+)[;]"
    structure_field_of_main_structure_modification_instruction_line_regex_compiled = re.compile(structure_field_of_main_structure_modification_instruction_line_regex_as_string)

    sMT2_Data_mE_line_number = 0

    for sMT2_Data_mE_file_line in sMT2_Data_mE_file_lines:
        sMT2_Data_mE_file_line_stripped = sMT2_Data_mE_file_line.strip()
        sMT2_Data_mE_line_number += 1

        match_table_field_of_main_structure_modification_instruction = table_field_of_main_structure_modification_instruction_line_regex_compiled.match(sMT2_Data_mE_file_line_stripped)
        match_structure_field_of_main_structure_modification_instruction = structure_field_of_main_structure_modification_instruction_line_regex_compiled.match(sMT2_Data_mE_file_line_stripped)

        if match_table_field_of_main_structure_modification_instruction is not None:
            structureModificationInstruction = TableFieldInMainStructureModificationInstruction()
            structureModificationInstruction.build_from_string_and_regex(sMT2_Data_mE_file_line_stripped, match_table_field_of_main_structure_modification_instruction)
            sMT2_Data_mE_Content.tableFieldInMainStructureModificationInstructions.append(structureModificationInstruction)

        elif match_structure_field_of_main_structure_modification_instruction is not None:
            sMT2_Data_mE_Content.structureFieldInMainStructureModificationInstructionLines.append(sMT2_Data_mE_file_line)

    

    
def create_and_fill_output_file(output_directory, input_file_name, file_content_as_list_of_lines):

    if not os.path.exists(output_directory):
        print_and_log_info('Create output directory:' + output_directory)
        os.makedirs(output_directory)

    print_and_log_info('Create output file:' + input_file_name)
    output_file = open(output_directory + "\\" + input_file_name, "w")
    logging.info('Fill output file:' + input_file_name)

    logging.info('Converting output content to string')
    output_file_content = end_line_character_in_text_file.join(file_content_as_list_of_lines)

    output_file.write(output_file_content)
    logging.info('Close output file:' + input_file_name)
    output_file.close()


def Generate_SMT2_Data_mE_fields_contents_from_field_post_assignment_lines():
    sMT2_Data_mE_Content = SMT2_Data_mE_Content()

    load_SMT2_Data_mE(input_SMT2_Data_mE_file_name, sMT2_Data_mE_Content)


    sMT2_Data_mE_Content.create_structure_fields_objects()
    sMT2_Data_mE_Content.fill_structure_fields_objects()
    
    file_content_as_list_of_lines = list()
    sMT2_Data_mE_Content.save_results(file_content_as_list_of_lines)
    create_and_fill_output_file("output", "Generate_SMT2_Data_mE_fields_contents_from_field_post_assignment_lines.txt", file_content_as_list_of_lines)


def main():
    log_file_name = 'Generate_SMT2_Data_mE_fields_contents_from_field_post_assignment_lines' + ".log"
    #log_file_name = 'Generate_SMT2_Data_mE_fields_contents_from_field_post_assignment_lines' + "." +  str(random.randrange(10000)) + ".log"
    configureLogger(log_file_name)    
    print_and_log_info('Start application. Log file name: ' + log_file_name)
    Generate_SMT2_Data_mE_fields_contents_from_field_post_assignment_lines()
    print_and_log_info('End application')

if __name__ == '__main__':
    main()

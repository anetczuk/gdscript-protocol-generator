#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys, os
import logging
import argparse

from string import Template

import csv

from pandas import DataFrame


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory


# ====================================================================
# ====================================================================


def generate( input_csv_path, output_dir ):
    _LOGGER.info( "parsing file %s", input_csv_path )

    configDict, dataMatrix = parse_csv( input_csv_path )

    configDict[ 'input_file' ] = input_csv_path
    
    generate_gdscript( configDict, dataMatrix, output_dir )
    generate_python( configDict, dataMatrix, output_dir )


def generate_gdscript( configDict, dataMatrix, outputDir ):
    _LOGGER.info( "generating GDScript file" )
    
    class_name  = configDict[ "class_name" ]
    output_name = class_name + ".gd"

    template_message_id_handle_switch = ""
    template_message_receive_funcs = ""
    template_message_send_funcs = ""

    for index, row in dataMatrix.iterrows():
        message_id = row['message id']
        _LOGGER.info( "gdscript: handling message %s", message_id )
        
        method_args_list = read_args( row )

        message_exploded_list = []
        for i in range( 0, len(method_args_list) ):
            message_exploded_list.append( "message[%s]" % (i+1) )
        
        message_exploded_args = ", ".join( message_exploded_list )
        if len(message_exploded_args) > 0:
            message_exploded_args = " " + message_exploded_args + " "

        template_message_id_handle_switch += "\t\t\"%s\": _receive_%s(%s)\n" % ( message_id, message_id, message_exploded_args )

        method_args_def  = ", ".join( method_args_list )
        if len(method_args_def) > 0:
            method_args_def = " " + method_args_def + " "
        
        method_args_send = ", ".join( ["\"" + message_id + "\""] + method_args_list )
        
        template_message_receive_funcs += \
"""
func _receive_%(message_id)s(%(method_args_def)s):
\t## implement in derived class
\tprint( "unimplemented method '_receive_%(message_id)s'" )
""" % {
        "message_id": message_id,
        "method_args_def": method_args_def
    }

        template_message_send_funcs += \
"""
func send_%(message_id)s(%(method_args_def)s):
\tvar message = [ %(method_args_send)s ]
\t_send_message_raw( message )
""" % {
        "message_id": message_id,
        "method_args_def": method_args_def,
        "method_args_send": method_args_send
    }

    template_message_funcs = ""
    template_message_funcs += template_message_send_funcs
    template_message_funcs += """
## ============= virtual methods ===============
"""
    template_message_funcs += template_message_receive_funcs 
    
    contentData = { 'TEMPLATE_MESSAGE_ID_HANDLE_SWITCH': template_message_id_handle_switch,
                    'TEMPLATE_MESSAGE_FUNCS': template_message_funcs }

    ## ====================================

    templatePath = os.path.join( SCRIPT_DIR, "template", "protocol.gd.template" )
 
    with open( templatePath, "r" ) as templateFile:
        #read it
        template = Template( templateFile.read() )
        #do the substitution
        script_content = template.substitute( contentData )

    ### === writing to file ===
    os.makedirs( outputDir, exist_ok=True )
    outputFile = os.path.join( outputDir, output_name )
    with open( outputFile, "w" ) as enumFile:
        enumFile.write( script_content )


def generate_python( configDict, dataMatrix, outputDir ):
    _LOGGER.info( "generating Python file" )
    
    class_name  = configDict[ "class_name" ]
    output_name = class_name.lower() + ".py"

    template_class_name = class_name
    template_message_id_handle_dict = ""
    template_message_receive_funcs = ""
    template_message_send_funcs = ""

    for index, row in dataMatrix.iterrows():
        message_id = row['message id']
        _LOGGER.info( "python: handling message %s", message_id )
        
        template_message_id_handle_dict += \
            """                \"%(message_id)s\": self._receive_%(message_id)s,\n""" % { 'message_id': message_id }
       
        method_args_list = read_args( row )

        method_args_def  = ", ".join( ["self"] + method_args_list )
        if len(method_args_def) > 0:
            method_args_def = " " + method_args_def + " "
        
        method_args_send = ", ".join( ["\"" + message_id + "\""] + method_args_list )

        template_message_receive_funcs += \
"""
    @abc.abstractmethod
    def _receive_%(message_id)s(%(method_args_def)s):
        raise NotImplementedError('You need to define this method in derived class!')
""" % {
        "message_id": message_id,
        "method_args_def": method_args_def
    }

        template_message_send_funcs += \
"""
    def send_%(message_id)s(%(method_args_def)s):
        message = [ %(method_args_send)s ]
        self._send_message_raw( message )
""" % {
        "message_id": message_id,
        "method_args_def": method_args_def,
        "method_args_send": method_args_send
    }

    template_message_funcs = ""
    template_message_funcs += template_message_send_funcs
    template_message_funcs += """
    ## ============= virtual methods ===============
"""

    template_message_id_handle_dict = "{\n" + template_message_id_handle_dict + "            }"
    template_message_funcs += template_message_receive_funcs 

    contentData = { 'TEMPLATE_CLASS_NAME': template_class_name,
                    'TEMPLATE_MESSAGE_ID_HANDLE_DICT': template_message_id_handle_dict,
                    'TEMPLATE_MESSAGE_FUNCS': template_message_funcs }

    ## ====================================

    templatePath = os.path.join( SCRIPT_DIR, "template", "protocol.py.template" )
 
    with open( templatePath, "r" ) as templateFile:
        #read it
        template = Template( templateFile.read() )
        #do the substitution
        script_content = template.substitute( contentData )

    ### === writing to file ===
    os.makedirs( outputDir, exist_ok=True )
    outputFile = os.path.join( outputDir, output_name )
    with open( outputFile, "w" ) as enumFile:
        enumFile.write( script_content )


def read_args( row ):
    method_args_list = []
    field_index = -1
    while True:
        field_index += 1
        field_name  = "field " + str( field_index )
        field_value = get_row_value( row, field_name, None )
        if field_value is None:
            break
        method_args_list.append( field_value )
    return method_args_list


def get_row_value( row, key, default_value ):
    try:
        rowVal = row[ key ]
        if not is_field_empty( rowVal ):
            return rowVal
        return default_value
    except KeyError:
        return None


def is_field_empty( value ):
    if value is None:
        return True
    if len( str( value ) ) < 1:
        return True
    return False


# ===================================================================


## returns tuple ( config_dict, data_matrix )
def parse_csv( csv_path ):
    with open( csv_path, newline='' ) as csvfile:
        dataReader = csv.reader( csvfile, delimiter=',', quotechar='|' )
        
        configPart = False
        dataPart   = False
    
        configList = list()
        dataList   = list()
        
        for line in dataReader:
            # print( line )
            rawLine = ''.join( line )
            if len(rawLine) > 0:
                if rawLine == "Config:":
                    configPart = True
                    continue
                if rawLine == "Data:":
                    dataPart = True
                    continue
                # if rawLine[0] == '#':
                #    continue
                # if rawLine.startswith( "//" ):
                #    continue
            else:
                configPart = False
                dataPart   = False
                continue

            if configPart is True:
                configList.append( line )
            elif dataPart is True:
                dataList.append( line )

        configMatrix = create_matrix( configList )
        dataMatrix   = create_matrix( dataList )
        
        ## convert matrix to dict
        zip_iterator = zip( configMatrix["parameter"], configMatrix["value"] )
        configDict   = dict( zip_iterator )
        
        return ( configDict, dataMatrix )
    return ( None, None )


def create_matrix( dataList ):
    if len(dataList) < 1:
        raise Exception( "No data field found" )

    matrixHeader = dataList[ 0 ]
    matrixData   = DataFrame( dataList )

    ## remove redundant columns
    headerSize = len(matrixHeader)
    colsNum = len(matrixData.columns)
    if colsNum > headerSize:
        for _ in range( headerSize, colsNum ):
            colName = matrixData.columns[len(matrixData.columns)-1]
            matrixData.drop(colName, axis=1, inplace=True)

    matrixData.columns = matrixHeader

    matrixData = matrixData.iloc[1:]        ## remove first row (containing header labels)

    return matrixData


# ====================================================================
# ====================================================================


def configure_logger( level=None ):
    formatter = create_formatter()
    consoleHandler = logging.StreamHandler( stream=sys.stdout )
    consoleHandler.setFormatter( formatter )

    logging.root.addHandler( consoleHandler )
    if level is None:
        logging.root.setLevel( logging.INFO )
    else:
        logging.root.setLevel( level )


def create_formatter(loggerFormat=None):
    if loggerFormat is None:
        loggerFormat = '%(asctime)s,%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
#        loggerFormat = ('%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s '
#                        '[%(filename)s:%(lineno)d] %(message)s')
    dateFormat = '%H:%M:%S'
#    dateFormat = '%Y-%m-%d %H:%M:%S'
    return logging.Formatter( loggerFormat, dateFormat )


def main():
    parser = argparse.ArgumentParser(description='GDScript protocol generator')
    parser.add_argument('-ll', '--log_level', action='store', default='INFO', help='Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL, default: INFO' )
    parser.add_argument('--input_config', action='store', required=True, help='Configuration file (csv)' )
    parser.add_argument('--output_dir', action='store', required=True, help='Directory to output data' )

    args = parser.parse_args()

    configure_logger( args.log_level )
    
    generate( args.input_config, args.output_dir )
    
    _LOGGER.info( "done" )


if __name__ == '__main__':
    main()

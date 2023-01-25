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
import copy

import csv

from pandas import DataFrame

import texthon


_LOGGER = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(__file__)      ## full path to script's directory


# ====================================================================
# ====================================================================


ALLOWED_DIRECTION = [ "BOTH", "TO_PY", "TO_GD", "DISABLED" ]


def generate( input_csv_path, output_dir ):
    _LOGGER.info( "parsing file %s", input_csv_path )

    configDict, dataMatrix = parse_csv( input_csv_path )

    configDict[ 'input_file' ] = input_csv_path
    
    class_name  = configDict[ "class_name" ]
    messages_defs = read_messages_defs( dataMatrix )
    template_params = { "class_name": class_name,
                        "messages_list": messages_defs }
#     PARAMS_PATH   = os.path.join( SCRIPT_DIR, "template", "protocol.param" )
    
    # print( "xxxx:", template_params )
    
    os.makedirs( output_dir, exist_ok=True )
    
    _LOGGER.info( "generating GDScript file" )
    template_path = os.path.join( SCRIPT_DIR, "template", "protocol.gd.tmpl" )
    output_path   = os.path.join( output_dir, class_name + ".gd" )
    generate_file( template_path, template_params, output_path )
    
    _LOGGER.info( "generating Python file" )
    template_path = os.path.join( SCRIPT_DIR, "template", "protocol.py.tmpl" )
    output_path   = os.path.join( output_dir, class_name.lower() + ".py" )
    generate_file( template_path, template_params, output_path )


def generate_file( template_path, template_params, output_path ):
    engine     = texthon.Engine()
    module_def = engine.load_file( template_path )              # parse and store the parsed module
    module_id  = module_def.path                                # store the path so we can find the compiled module later

    engine.make()                                               # compile all modules
    
#     with open( PARAMS_PATH, "r" ) as params_file:
#         params_content = params_file.read()
#         params = eval( params_content )
    
    module = engine.modules[module_id]

    # call the template function named 'main'
#     script_content = module.main( messages = messages_defs )
    script_content = module.main( **template_params )
    
    ### === writing to file ===
    with open( output_path, "w" ) as out_file:
        out_file.write( script_content )


# ===================================================================


def filter_message_direction( template_params, allowed_directions ):
    filtered_params   = copy.deepcopy( template_params )
    filtered_messages = []
    for message in filtered_params[ "messages" ]:
        if message["direction"] in allowed_directions:
            filtered_messages.append( message )
    filtered_params[ "messages" ] = filtered_messages
    return filtered_params


def read_messages_defs( dataMatrix ):
    messages_defs = []
    
    for index, row in dataMatrix.iterrows():
        message_id = row['message id']
        _LOGGER.info( "handling message %s", message_id )

        direction: str = row['direction']
        direction = direction.strip()
        if not direction:
            direction = "BOTH"
        elif direction not in ALLOWED_DIRECTION:
            _LOGGER.error( "invalid 'direction' parameter: '%s' allowed: %s", direction, ALLOWED_DIRECTION )
            direction = "BOTH"

        method_args_list = read_args( row )

        messages_dict = {}
        messages_dict[ 'id' ]        = message_id
        messages_dict[ 'direction' ] = direction
        messages_dict[ 'params' ]    = method_args_list
        
        messages_defs.append( messages_dict )

    return messages_defs


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

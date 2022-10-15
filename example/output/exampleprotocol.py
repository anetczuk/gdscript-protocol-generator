##
## File was automatically generated using 'gdscript-protocol-generator'
##
## Project website: https://github.com/anetczuk/gdscript-protocol-generator
##

import logging
import abc


_LOGGER = logging.getLogger(__name__)


class ExampleProtocol():

    ##### constructor
    ##def _init():
    ##    _LOGGER.info( "Protocol handler created" )
    
    def handleMessage( self, message ):
        if typeof( message ) != TYPE_ARRAY:
            _LOGGER.warning( "invalid message type (array expected): %s message: %s", type( message ), message )
            return
        message_len = len( message )
        if message_len < 1:
            _LOGGER.warning( "empty message array: %s", message )
            return

        message_id   = message[0]
        message_args = message[ 1: ]
    
        if message_id == "DO_STEP":
            _receive_DO_STEP( *message_args )
            return
        if message_id == "ADD_ITEM":
            _receive_ADD_ITEM( *message_args )
            return
        if message_id == "REMOVE_ITEM":
            _receive_REMOVE_ITEM( *message_args )
            return
        if message_id == "MOVE_ITEM":
            _receive_MOVE_ITEM( *message_args )
            return

        _LOGGER.warning( "unhandled message: ", message )

    ## ============= handling methods ===============

    @abc.abstractmethod
    def _send_message( self, message ):
        raise NotImplementedError('You need to define this method in derived class!')

    def _send_DO_STEP( self ):
        message = [ "DO_STEP" ]
        _send_message( message )

    def _send_ADD_ITEM( self, item_id ):
        message = [ "ADD_ITEM", item_id ]
        _send_message( message )

    def _send_REMOVE_ITEM( self, item_id ):
        message = [ "REMOVE_ITEM", item_id ]
        _send_message( message )

    def _send_MOVE_ITEM( self, item_id, position, heading ):
        message = [ "MOVE_ITEM", item_id, position, heading ]
        _send_message( message )

    ## ============= virtual methods ===============

    @abc.abstractmethod
    def _receive_DO_STEP( self ):
        raise NotImplementedError('You need to define this method in derived class!')

    @abc.abstractmethod
    def _receive_ADD_ITEM( self, item_id ):
        raise NotImplementedError('You need to define this method in derived class!')

    @abc.abstractmethod
    def _receive_REMOVE_ITEM( self, item_id ):
        raise NotImplementedError('You need to define this method in derived class!')

    @abc.abstractmethod
    def _receive_MOVE_ITEM( self, item_id, position, heading ):
        raise NotImplementedError('You need to define this method in derived class!')

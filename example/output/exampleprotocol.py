##
## File was automatically generated using 'gdscript-protocol-generator'
##
## Project website: https://github.com/anetczuk/gdscript-protocol-generator
##

import logging
import abc


_LOGGER = logging.getLogger(__name__)


class ExampleProtocol():

    ### constructor
    def __init__(self):
        self.receiver_dict = {
                "DO_STEP": self._receive_DO_STEP,
                "ADD_ITEM": self._receive_ADD_ITEM,
                "REMOVE_ITEM": self._receive_REMOVE_ITEM,
                "MOVE_ITEM": self._receive_MOVE_ITEM,
            }


    def handleMessages( self ):
        while True:
            data = self._recv_message_raw()
            error_code = data[0]
            if error_code != 0:
                ## return received error code
                return error_code
            message = data[1]
            if message == None:
                ## no new messages
                break
            self.handleMessage( message )
        return 0

    def handleMessage( self, message ):
        if isinstance( message, list ) is False:
            _LOGGER.warning( "invalid message type (array expected): %s message: %s", type( message ), message )
            return
        message_len = len( message )
        if message_len < 1:
            _LOGGER.warning( "empty message array: %s", message )
            return

        message_id   = message[0]
        message_args = message[ 1: ]

        receiver_func = self.receiver_dict.get( message_id )
        if receiver_func is None:
            _LOGGER.warning( "unhandled message: ", message )
            return

        receiver_func( *message_args )

    def receive_message( self ):
        response = self._recv_message_raw()
        if response[0] != 0:
            ## return received error code
            _LOGGER.warning( "unable to receive message, code: %s", response[0] )
            return None
        message = response[1]
        if not isinstance( message, list ):
            _LOGGER.warning( "invalid message: %s", message )
            return None
        return message

    ## ============= handling methods ===============

    def send_DO_STEP( self ):
        message = [ "DO_STEP" ]
        self._send_message_raw( message )

    def send_ADD_ITEM( self, item_id ):
        message = [ "ADD_ITEM", item_id ]
        self._send_message_raw( message )

    def send_REMOVE_ITEM( self, item_id ):
        message = [ "REMOVE_ITEM", item_id ]
        self._send_message_raw( message )

    def send_MOVE_ITEM( self, item_id, position, heading ):
        message = [ "MOVE_ITEM", item_id, position, heading ]
        self._send_message_raw( message )

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

    @abc.abstractmethod
    def _recv_message_raw( self ):
        ## implement in derived class
        raise NotImplementedError('You need to define this method in derived class!')

    @abc.abstractmethod
    def _send_message_raw( self, message ):
        ## implement in derived class
        raise NotImplementedError('You need to define this method in derived class!')

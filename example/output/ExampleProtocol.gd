##
## File was automatically generated using 'gdscript-protocol-generator'
##
## Project website: https://github.com/anetczuk/gdscript-protocol-generator
##


### constructor
##func _init():
##  print( "Protocol handler created" )

func handleMessage( message ):
    if typeof( message ) != TYPE_ARRAY:
        print( "invalid message type (array expected): ", typeof( message ), " message: ", message )
        return
    const message_len = len( message )
    if message_len < 1:
        print( "empty message array: ", message )
        return
            
    var message_id   = message[0]
    var message_args = message.slice( 1, message_len )

    match message_id:
        "DO_STEP": _receive_DO_STEP( *message_args )
        "ADD_ITEM": _receive_ADD_ITEM( *message_args )
        "REMOVE_ITEM": _receive_REMOVE_ITEM( *message_args )
        "MOVE_ITEM": _receive_MOVE_ITEM( *message_args )

        ## unknown message
        _: print( "unhandled message: ", message )

## ============= handling methods ===============

func _send_DO_STEP():
    var message = [ "DO_STEP" ]
    _send_message( message )

func _send_ADD_ITEM( item_id ):
    var message = [ "ADD_ITEM", item_id ]
    _send_message( message )

func _send_REMOVE_ITEM( item_id ):
    var message = [ "REMOVE_ITEM", item_id ]
    _send_message( message )

func _send_MOVE_ITEM( item_id, position, heading ):
    var message = [ "MOVE_ITEM", item_id, position, heading ]
    _send_message( message )

## ============= virtual methods ===============

func _receive_DO_STEP():
    ## implement in derived class
    pass

func _receive_ADD_ITEM( item_id ):
    ## implement in derived class
    pass

func _receive_REMOVE_ITEM( item_id ):
    ## implement in derived class
    pass

func _receive_MOVE_ITEM( item_id, position, heading ):
    ## implement in derived class
    pass

func _send_message( message ):
    ## implement in derived class
    pass

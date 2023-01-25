##
## File was automatically generated using 'gdscript-protocol-generator'
##
## Project website: https://github.com/anetczuk/gdscript-protocol-generator
##


### constructor
##func _init():
##  print( "Protocol handler created" )

## handling peding messages
func handleMessages():
	while true:
		var data = _recv_message_raw()
		var error_code = data[0]
		if error_code != 0:
			## return received error code
			return error_code
		var message = data[1]
		if message == null:
			## no new messages
			break
		handleMessage( message )
	return 0

## handling received message
func handleMessage( message ):
	if typeof( message ) != TYPE_ARRAY:
		print( "invalid message type (array expected): ", typeof( message ), " message: ", message )
		return
	var message_len = len( message )
	if message_len < 1:
		print( "empty message array: ", message )
		return

	match message[0]:
		"ADD_ITEM": _receive_ADD_ITEM( message[1] )
		"REMOVE_ITEM": _receive_REMOVE_ITEM( message[1] )
		"MOVE_ITEM": _receive_MOVE_ITEM( message[1], message[2], message[3] )
		"PAUSE": _receive_PAUSE()

		## unknown message
		_: print( "unhandled message: ", message )

	## end of handler

## receive pending message
func receiveMessage():
	var response = _recv_message_raw()
	if response[0] != 0:
		## return received error code
		print( "unable to receive message, code: %s", response[0] )
		return null
	var message = response[1]
	if typeof( message ) != TYPE_ARRAY:
		print( "invalid message type (array expected): ", typeof( message ), " message: ", message )
		return null
	return message

## ============= handling methods ===============

## method is responsible for receiving raw data from communiation channel
func _recv_message_raw():
	## implement in derived class
	print( "unimplemented method '_recv_message_raw'" )
	return [-1, null]

## method is responsible for sending raw data through communiation channel
func _send_message_raw( message ):
	## implement in derived class
	print( "unimplemented method '_send_message_raw'" )

## ============= send methods ===============

## sender of 'DO_STEP' message
func send_DO_STEP():
	var message = [ "DO_STEP" ]
	_send_message_raw( message )

## sender of 'ADD_ITEM' message
func send_ADD_ITEM( item_id ):
	var message = [ "ADD_ITEM", item_id ]
	_send_message_raw( message )

## sender of 'REMOVE_ITEM' message
func send_REMOVE_ITEM( item_id ):
	var message = [ "REMOVE_ITEM", item_id ]
	_send_message_raw( message )

## sender of 'MOVE_ITEM' message
func send_MOVE_ITEM( item_id, position, heading ):
	var message = [ "MOVE_ITEM", item_id, position, heading ]
	_send_message_raw( message )

## ============= receive methods ===============

## callback of reveived 'ADD_ITEM' message
func _receive_ADD_ITEM( item_id ):
	## implement in derived class
	print( "unimplemented method '_receive_ADD_ITEM'" )

## callback of reveived 'REMOVE_ITEM' message
func _receive_REMOVE_ITEM( item_id ):
	## implement in derived class
	print( "unimplemented method '_receive_REMOVE_ITEM'" )

## callback of reveived 'MOVE_ITEM' message
func _receive_MOVE_ITEM( item_id, position, heading ):
	## implement in derived class
	print( "unimplemented method '_receive_MOVE_ITEM'" )

## callback of reveived 'PAUSE' message
func _receive_PAUSE():
	## implement in derived class
	print( "unimplemented method '_receive_PAUSE'" )


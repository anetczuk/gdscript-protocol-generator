##
##
##

extends Node

var server: TCPServer
var connection_dict: Dictionary			## Dict[ int, Connection ]
var connection_counter = 0


##
class Connection:
	extends "res://output/ExampleProtocol.gd"

	var master							## TraffCtrlConnector
	var conn_id

	var tcp_stream: StreamPeerTCP
	

	### constructor
	func _init( owner, conn_id ):
		master = owner
		conn_uuid = conn_id
		
		tcp_stream = master.server.take_connection()
		tcp_stream.set_no_delay(true)

		print( "received connection" )

	func handleConnection():
		handleMessages()
		_send_DO_STEP()

	func closeConnection():
		tcp_stream.disconnect_from_host()
		master.connection_dict.erase( conn_uuid )

	## ============= protocol methods ===============

	#func _receive_DO_STEP():
    #    ## implement in derived class
    #    print( "unimplemented method '_receive_DO_STEP'" )

    func _receive_ADD_ITEM( item_id ):
        print( "adding new item: ", item_id )
    
    func _receive_REMOVE_ITEM( item_id ):
        print( "removing item: ", item_id )
    
    func _receive_MOVE_ITEM( item_id, position, heading ):
        print( "moving item to: ", item_id, " ", position, " ", heading )
    
    ## error code:
    ##      -1 -- not implemented
    ##       0 -- valid
    ##       1 -- no more messages
    ##       2 -- connection terminated
    func _receive_message():
        var av_bytes = tcp_stream.get_available_bytes()
        if av_bytes == 0:
            ## no waiting bytes to receive
            return [1, null]
        if av_bytes < 0:
            ## connection error
            print( "connection terminated" )
            closeConnection()
            return [2, null]
        ## reading data
        var message = tcp_stream.get_var()
        return [0, message]
    
    func _send_message( message ):
        tcp_stream.put_var( message )


## ============================================================================


func _ready():
	server = TCPServer.new()
	server.listen(42424, "*")
	print( "server started" )

func _process( _delta ):
	if server.is_listening():
		if server.is_connection_available():
			var new_connection = Connection.new( self, connection_counter )
			connection_counter += connection_counter
			connection_dict[ new_connection.conn_uuid ] = new_connection

	for key in connection_dict:
		var curr_connection: Connection = connection_dict[ key ]
		curr_connection.handleMessages()

var net = require('net');

var server = net.createServer(function(socket) {
	socket.setEncoding('utf8')
	
	// confrim to client that connection was succesful
	socket.write('connection confirmation\n');
	console.log('SERVER: Connected');
	
	// handle incoming requests of format "up:2" - "<two char command>:<optional float quantity>"
	socket.on('data', function (data) {
		console.log("SERVER: " + data);
		
		var command = data.slice(0,2);
		var amount = parseFloat(data.slice(3));
		switch(command) {
			case 'to': //takeoff
				// do take off
				console.log('SERVER: to received');
				
				console.log('SERVER: to finished');
				socket.write(command + ":finished");
				break;
			case "la": //land
				console.log('SERVER: la received');
				                     
				console.log('SERVER: la finished');
				socket.write(command + ":finished");
				break;
			case "up": // up
				console.log('SERVER: up received');
				
				console.log('SERVER: up finished');
				socket.write(command + ":finished");
				break;
			case "fo": // forward
				console.log('SERVER: fo received');
				
				console.log('SERVER: fo finished');
				socket.write(command + ":finished");
				break;
			case "rl": // rotate left
				console.log('SERVER: rl received');
				
				console.log('SERVER: rl finished');
				socket.write(command + ":finished");
				break;
			case "ra": // request acceleration data
				console.log('SERVER: ra received');
				
				console.log('SERVER: ra finished');
				socket.write(command + ":<all that sweet, sweet sensor data>");
				break;
			default:
				console.log('SERVER: un recognized command');
				socket.write("un recognized command");
		}
	});
	//socket.pipe(socket);
});

server.listen(1337, '127.0.0.1');

/*
And connect with a tcp client from the command line using netcat, the *nix 
utility for reading and writing across tcp/udp network connections.  I've only 
used it for debugging myself.
$ netcat 127.0.0.1 1337
You should see:
> Echo server
*/

/* Or use this example tcp client written in node.js.  (Originated with 
example code from 
http://www.hacksparrow.com/tcp-socket-programming-in-node-js.html.) */

//var net = require('net');
//
//var client = new net.Socket();
//client.setEncoding('utf8');
//client.connect(1337, '127.0.0.1', function() {
//	console.log('Connected');
//	client.write('to:');
//	client.
//	client.write('la:');
//});
//
//client.on('data', function(data) {
//	console.log('Received: ' + data);
//	//client.destroy(); // kill client after server's response
//});
//
//client.on('close', function() {
//	console.log('Connection closed');
//});
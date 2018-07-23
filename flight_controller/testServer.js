var net = require('net');

var arDrone = require('ar-drone');
var client  = arDrone.createClient({ip:"10.42.0.8"});
client.config('general:navdata_demo', 'FALSE');

var count = 0;
var accelerationData;

var foo = function(yolo) {
	if (count % 40 == 0) {
		accelerationData = yolo.physMeasures
	}
	count++;
}

client.on('navdata', foo);

// client.config('general:navdata_demo', 'FALSE');
// client.on('navdata', console.log);

var server = net.createServer(function(socket) {
	socket.setEncoding('utf8')
	
	// confrim to client that connection was succesful
	socket.write('connection confirmation\n');
	console.log('SERVER: Connected');
	
	// handle incoming requests of format "up:2" - "<two char command>:<optional float quantity>"
	socket.on('data', function (data) {
		console.log("SERVER: " + data);
		
		var command = data.slice(0,2);
		var direction = parseFloat(data.slice(2));
		switch(command) {
			case 'to': //takeoff
				// do take off
				console.log('SERVER: to received');

				client.takeoff(function () {
					console.log('SERVER: to finished');
					socket.write(command + ":finished");
				})
				
				break;
			case "la": //land
				console.log('SERVER: la received');

				client.stop();
				client.land(function () {
					console.log('SERVER: la finished');
					socket.write(command + ":finished");
				})
				                     
				break;
			case "up": // up
				console.log('SERVER: up received');
				
				console.log('SERVER: up finished');
				socket.write(command + ":finished");
				break;
			case "fo": // forward
				console.log('SERVER: fo received');

				console.log(direction)
    			client
	  				.after(1000, function() {
	    			this.front(direction*0.1);
	  			}).after(1000, function() {
	  				this.stop();
	  			})
				
				console.log('SERVER: fo finished');
				socket.write(command + ":finished");
				break;
			case "rl": // rotate left
				console.log('SERVER: rl received');

				client
	  				.after(1000, function() {
	    			this.clockwise(direction*0.1);
	  			}).after(1000, function() {
	  				this.stop();
	  			})
				
				console.log('SERVER: rl finished');
				socket.write(command + ":finished");
				break;
			case "ra": // request acceleration data
				console.log('SERVER: ra received');
				
				console.log('SERVER: ra finished');
				socket.write(JSON.stringify(accelerationData));
				break;
			default:
				console.log('SERVER: un recognized command');
				socket.write("un recognized command");
		}
	});

	socket.on('error', function (data) {
		console.log("error: "  + data);
	})

	//socket.pipe(socket);
});

server.listen(1337, '127.0.0.1');

process.on('SIGINT', function() {
    console.log("Caught interrupt signal");
    client.stop();
    console.log("Stop");
    client.land(function () {
    	process.exit();
    });
});

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
var net = require('net');

var arDrone = require('ar-drone');

var client  = arDrone.createClient();
// When we are telnetting
// var client  = arDrone.createClient({ip:"10.42.0.8"});
client.config('general:navdata_demo', 'FALSE');

var count = 0;
var accelerationData;
var payload = {};
var prevTimestamp = null
var socketToPython = null


var getData = function(data) {
	// if (count % 0 == 0) {
	accelerationData = data.physMeasures //  pyardrone.navdata.options.PhysMeasures

	if (!accelerationData) return

	payload.timestamp = data.time
	payload.accelerometers = accelerationData.accelerometers
	payload.gyroscopes = accelerationData.gyroscopes

	payload.controlState = data.demo.controlState
	payload.flyState = data.demo.flyState
	// payload.batteryPercentage = data.demo.batteryPercentage
	payload.frontBackDegrees = data.demo.frontBackDegrees
	payload.leftRightDegrees = data.demo.leftRightDegrees
	payload.clockwiseDegrees = data.demo.clockwiseDegrees
	// payload.altitude = data.demo.altitude
	// payload.velocity = data.demo.velocity
	payload.xVelocity = data.demo.xVelocity
	payload.yVelocity = data.demo.yVelocity
	payload.zVelocity = data.demo.zVelocity

	payload.command = "ra"
	// payload.num = num
	payload.dataValid = true

	if(socketToPython){
		socketToPython.write(JSON.stringify(payload))
	}
	//console.log(JSON.stringify(payload))
	// }
	count++;
}

client.on('navdata', getData);

// client.config('general:navdata_demo', 'FALSE');
// client.on('navdata', console.log);

var server = net.createServer(function(socket) {
	socket.setEncoding('utf8')
	socketToPython = socket;
	// confrim to client that connection was succesful
	socket.write('connection confirmation');
	console.log('SERVER: Connected');

	// setInterval(function() {
  //   	if (payload && (!prevTimestamp || prevTimestamp < payload.timestamp)) {
	// 		payload.command = "ra"
	// 		// payload.num = num
	// 		payload.dataValid = true
	// 		socket.write(JSON.stringify(payload))
	// 		prevTimestamp = payload.timestamp
	// 		console.log(JSON.stringify(payload))
	// 	}
	// }, 100)

	// handle incoming requests of format "up:2" - "<two char command>:<optional float quantity>"
	socket.on('data', function (data) {
		console.log("SERVER RAW COMMAND RECEIVED: " + data);

		var array = data.split(',');
		var command = array[0]
		var num = array[1]

		var direction = parseFloat(data.slice(2));
		switch(command) {
			case 'to': //takeoff
				// do take off
				console.log('SERVER: to received');

				client.takeoff(function () {
					console.log('SERVER: to finished');
					payload.command = command
					payload.num = num
					socket.write(JSON.stringify(payload));
				})

				break;
			case "la": //land
				console.log('SERVER: la received');

				client.stop();
				client.land(function () {
					console.log('SERVER: la finished');
					payload.command = command
					payload.num = num
					socket.write(JSON.stringify(payload));
				})

				break;
			case "up": // up
				console.log('SERVER: up received');

				console.log('SERVER: up finished');
				payload.command = command
				payload.num = num
				socket.write(JSON.stringify(payload));
				break;
			case "fo": // forward
				console.log('SERVER: fo received');

				console.log(direction)
    			client
	  				.after(1000, function() {
	    			this.front(0.1);
	  			}).after(2000, function() {
	  				this.stop();
	  				console.log('SERVER: fo finished');
					payload.command = command
					payload.num = num
					socket.write(JSON.stringify(payload));
	  			})
				break;
			case "rl": // rotate left
				console.log('SERVER: rl received');

				client
	  				.after(1000, function() {
	    			this.clockwise(0.3);
	  			}).after(1250, function() {
	  				this.stop();
	  			})

				console.log('SERVER: rl finished');
				payload.command = command
				payload.num = num
				socket.write(JSON.stringify(payload));
				break;
			case "ra": // request acceleration data
				console.log('SERVER: ra received');

				console.log('SERVER: ra finished');

				if (!prevTimestamp || prevTimestamp != payload.timestamp) {
					payload.command = command
					payload.num = num
					payload.dataValid = true
					socket.write(JSON.stringify(payload));
					prevTimestamp = payload.timestamp

				} else {
					payload.command = command
					payload.num = num
					payload.dataValid = false
					socket.write(JSON.stringify(payload));
				}
				break;
			default:
				console.log('SERVER: un recognized command');
				payload.command = "unknown"
				payload.num = "-1"
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

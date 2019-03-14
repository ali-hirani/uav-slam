var net = require('net');

var arDrone = require('ar-drone');

// var droneClient  = arDrone.createClient();
// When we are telnetting
var droneClient  = arDrone.createClient({ip:"192.168.1.1"});
droneClient.config('general:navdata_demo', 'FALSE');

var piBuffer = ""
var count = 0;
var accelerationData;
var payload = {};

payload.lidar0 = -1;
payload.lidar1 = -1;
payload.lidar2 = -1;
payload.lidar3 = -1;
payload.lidar4 = -1;

var prevTimestamp = null
var socketToPython = null

const TCP_IP = "192.168.43.242"
const TCP_PORT = 5005


var collect_packet = function(sock, size) {
    var data = ""
    while (data.length < size) {
        packet = sock.recv(size - data.length)
        if(!packet) {
            return null
        }

        data = data + packet
    }
        
    return data
}

var decode_data = function(data) {
    // first get the length of packet from first 4 bytes
    packet_length_bytes = collect_packet(sock , 4)
    if (!packet_length_bytes) {
        return null
    }

    console.log("Packet Length Bytes" + packet_length_bytes)
    // packet_length = struct.unpack('>I', packet_length_bytes)[0]

    // encoded_data = collect_packet(sock, packet_length)

    // var num = encoded_data[0]
    // var data encoded_data.slice(1,3)

    if (num == 0) {
        payload.lidar0 = data
    } else if (num == 1) {
        payload.lidar1 = data
    } else if (num == 2) {
        payload.lidar2 = data
    } else if (num == 3) {
        payload.lidar3 = data
    } else if (num == 4) {
        payload.lidar4 = data
    }
}


var getData = function(data) {
    // if (count % 0 == 0) {
    console.log("getData")
    accelerationData = data.physMeasures //  pyardrone.navdata.options.PhysMeasures

    if (!accelerationData) return

    console.log("build payload")

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
    payload.dataValid = true

    if(socketToPython){
        console.log("write to python sock")
        socketToPython.write(JSON.stringify(payload))
    }
    count++;
}

droneClient.on('navdata', getData);

var piClient = new net.Socket();
piClient.setEncoding('utf8');
piClient.connect(TCP_PORT, TCP_IP, function() {
    console.log('Connected to Pi');
});

piClient.on('data', function(data) {
    // console.log("I got a packet: " + data)
    piBuffer += data.toString();
    // console.log("Pi Buffer: " + piBuffer)

    while (piBuffer.includes(",")) {
        var splitted = piBuffer.split(",")
        var reading = splitted[0]
        var sensorId = reading.charAt(0)
        var sensorReading = reading.slice(1)
        piBuffer = piBuffer.slice(reading.length + 1)

        if (sensorId == 0) {
            payload.lidar0 = sensorReading
        } else if (sensorId == 1) {
            payload.lidar1 = sensorReading
        } else if (sensorId == 2) {
            payload.lidar2 = sensorReading
        } else if (sensorId == 3) {
            payload.lidar3 = sensorReading
        } else if (sensorId == 4) {
            payload.lidar4 = sensorReading
        }
    }
});

var server = net.createServer(function(socket) {
    socket.setEncoding('utf8')
    socketToPython = socket;
    // confrim to client that connection was succesful
    socketToPython.write('connection confirmation');
    console.log('Connected to Python');

    // handle incoming requests of format "up:2" - "<two char command>:<optional float quantity>"
    socket.on('data', function(data) {
        console.log("SERVER RAW COMMAND RECEIVED: " + data);

        var array = data.split(',');
        var command = array[0]
        var num = 10//keep this constant

        var direction = parseFloat(data.slice(2));
        switch(command) {
            case 'to': //takeoff
                // do take off
                console.log('SERVER: to received');

                droneClient.takeoff(function () {
                    console.log('SERVER: to finished');
                    payload.command = command
                    payload.num = num
                    socket.write(JSON.stringify(payload));
                })

                break;
            case "la": //land
                console.log('SERVER: la received');

                droneClient.stop();
                droneClient.land(function () {
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
            case "front": // forward
                console.log('SERVER: front received');

                console.log(direction)
                droneClient
                    .after(1000, function() {
                    this.front(0.1);
                }).after(2000, function() {
                    this.stop();
                    console.log('SERVER: front finished');
                    payload.command = command
                    payload.num = num
                    socket.write(JSON.stringify(payload));
                })
                break;
                case "back": // forward
                console.log('SERVER: back received');

                console.log(direction)
                droneClient
                    .after(1000, function() {
                    this.back(0.1);
                }).after(2000, function() {
                    this.stop();
                    console.log('SERVER: back finished');
                    payload.command = command
                    payload.num = num
                    socket.write(JSON.stringify(payload));
                })
                break;
                case "right": // forward
                console.log('SERVER: right received');

                console.log(direction)
                droneClient
                    .after(1000, function() {
                    this.front(0.1);
                }).after(2000, function() {
                    this.stop();
                    console.log('SERVER: right finished');
                    payload.command = command
                    payload.num = num
                    socket.write(JSON.stringify(payload));
                })
                break;
                case "left": // forward
                console.log('SERVER: left received');

                console.log(direction)
                droneClient
                    .after(1000, function() {
                    this.front(0.1);
                }).after(2000, function() {
                    this.stop();
                    console.log('SERVER: left finished');
                    payload.command = command
                    payload.num = num
                    socket.write(JSON.stringify(payload));
                })
                break;
            case "rl": // rotate left
                console.log('SERVER: rl received');

                droneClient
                    .after(1000, function() {
                    this.clockwise(0.1);
                }).after(2000, function() {
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
                    //payload.num = num
                    payload.dataValid = true
                    socket.write(JSON.stringify(payload));
                    prevTimestamp = payload.timestamp

                } else {
                    payload.command = command
                    //payload.num = num
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
    droneClient.stop();
    console.log("Stop");

    // Comment this block when not connected to the drone
    droneClient.land(function () {
        process.exit();
        piClient.destroy();
    });
    
    // process.exit();
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
//  console.log('Connected');
//  client.write('to:');
//  client.
//  client.write('la:');
//});
//
//client.on('data', function(data) {
//  console.log('Received: ' + data);
//  //client.destroy(); // kill client after server's response
//});
//
//client.on('close', function() {
//  console.log('Connection closed');
//});

// /Users/ali/4A/FYDP/yolo

var arDrone = require('ar-drone');
var client  = arDrone.createClient();
client.config('general:navdata_demo', 'FALSE');
client.on('navdata', console.log);

client.takeoff(function () {
	client
	  .after(3000, function() {
	  	console.log("clockwise rotation");
	    this.clockwise(0.1);
	  })
	  .after(3000, function() {
	  	console.log("stop");
	  	this.stop();
	  })
	  .after(3000, function() {
	  	console.log("counter_clockwise rotation");
	  	this.counterClockwise(0.1);
	  })
	  .after(3000, function() {
	  	console.log("land");
	  	this.stop();
	  	this.land(function() {
  			process.exit();
  		});
  	});
});



process.on('SIGINT', function() {
    console.log("Caught interrupt signal");
    client.stop();
    console.log("Stop");
    client.land(function () {
    	process.exit();
    });
});

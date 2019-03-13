// /Users/ali/4A/FYDP/yolo

var arDrone = require('ar-drone');
var client  = arDrone.createClient();
client.config('general:navdata_demo', 'FALSE');
client.on('navdata', console.log);

client.takeoff(function () {
	client
	  .after(5000, function() {
	    this.front(0.1);
	  })
	  .after(1000, function() {
	  	client.stop();
	  	client.land(function () {
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

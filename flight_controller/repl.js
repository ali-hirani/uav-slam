var arDrone = require('ar-drone');
var client  = arDrone.createClient();
client.config('general:navdata_demo', 'FALSE');
client.createRepl();

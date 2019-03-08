#MAIN LOOP:
'''
client.on('navdata', function(d) {
        if (!this._busy && d.demo) {
            this._busy = true;
            self._processNavdata(d);
            self._control(d);
            this._busy = false;
        }
});

Controller.prototype._processNavdata = function(d) {
    // EKF prediction step
    this._ekf.predict(d);

    // If a tag is detected by the bottom camera, we attempt a correction step
    // This require prior configuration of the client to detect the oriented
    // roundel and to enable the vision detect in navdata.
    // TODO: Add documentation about this
    if (d.visionDetect && d.visionDetect.nbDetected > 0) {
        // Fetch detected tag position, size and orientation
        var xc = d.visionDetect.xc[0]
          , yc = d.visionDetect.yc[0]
          , wc = d.visionDetect.width[0]
          , hc = d.visionDetect.height[0]
          , yaw = d.visionDetect.orientationAngle[0]
          , dist = d.visionDetect.dist[0] / 100 // Need meters
          ;

        // Compute measure tag position (relative to drone) by
        // back-projecting the pixel position p(x,y) to the drone
        // coordinate system P(X,Y).
        // TODO: Should we use dist or the measure altitude ?
        var camera = this._camera.p2m(xc + wc/2, yc + hc/2, dist);

        // We convert this to the controller coordinate system
        var measured = {x: -1 * camera.y, y: camera.x};

        // Rotation is provided by the drone, we convert to radians
        measured.yaw = yaw.toRad();

        // Execute the EKS correction step
        this._ekf.correct(measured, this._tag);
    }

    // Keep a local copy of the state
    this._state = this._ekf.state();
    this._state.z = d.demo.altitude;
    this._state.vx = d.demo.velocity.x / 1000 //We want m/s instead of mm/s
    this._state.vy = d.demo.velocity.y / 1000
}

EKF.prototype.predict = function(data) {
    var pitch = data.demo.rotation.pitch.toRad()
      , roll  = data.demo.rotation.roll.toRad()
      , yaw   = normAngle(data.demo.rotation.yaw.toRad())
      , vx    = data.demo.velocity.x / 1000 //We want m/s instead of mm/s
      , vy    = data.demo.velocity.y / 1000
      , dt    = this._delta_t
    ;

    // We are not interested by the absolute yaw, but the yaw motion,
    // so we need at least a prior value to get started.
    if (this._last_yaw == null) {
        this._last_yaw = yaw;
        return;
    }

    // Compute the odometry by integrating the motion over delta_t
    var o = {dx: vx * dt, dy: vy * dt, dyaw: yaw - this._last_yaw};
    this._last_yaw  = yaw;

    // Update the state estimate
    var state = this._state;
    state.x   = state.x + o.dx * Math.cos(state.yaw) - o.dy * Math.sin(state.yaw);
    state.y   = state.y + o.dx * Math.sin(state.yaw) + o.dy * Math.cos(state.yaw);
    state.yaw = state.yaw + o.dyaw;

    // Normalize the yaw value
    state.yaw = Math.atan2(Math.sin(state.yaw),Math.cos(state.yaw));

    // Compute the G term (due to the Taylor approximation to linearize the function).
    var G = $M(
           [[1, 0, -1 * Math.sin(state.yaw) * o.dx - Math.cos(state.yaw) * o.dy],
            [0, 1,  Math.cos(state.yaw) * o.dx - Math.sin(state.yaw) * o.dy],
            [0, 0, 1]]
            );

    // Compute the new sigma
    this._sigma = G.multiply(this._sigma).multiply(G.transpose()).add(this._q);
}

'''

import state

#checks if something is closer than "proximity". returns the direction with enough space
def check_collision(sensor_dist_list,  proximity):
    #convert list to ints
    sensor_dist_list =  map(int, sensor_dist_list)
    movement_room = 200 #must have movement_room distance to make move in a particular direction 
    for index, value, in enumerate(sensor_dist_list):
        if value < proximity:
            for i, val in enumerate(sensor_dist_list):
                if val > movement_room:
                    if i == 0:
                        #move front
                        return "front"
                    elif i == 1:
                        #move back
                        return "back"
                    elif i == 2:
                        #move right
                        return "right"
                    elif i == 3:
                        #move left
                        return "left"

        

    return -1


# accept state - return two letter command or None
def planFlight(state, counter):
    
    # for example:
    # if state.busy :
    #     return -1
    
    if not state.busy:

    	if counter == 1:
       	    return "to"

        #if counter - state.after_counter == 1000:
            #return "rl"
            #direction = check_collision(state.depths, 45)
            #return direction


    else:
        return -1 

import state

# accept state - return two letter command or None
def planFlight(state, counter ):
    # for example:
    # if state.busy :
    #     return -1
    if counter == 1 :
        return "to"
    elif counter >= 1200 :
        # return "fo"
    # elif count > 2000 :
    	return "la"
    else:
        return -1

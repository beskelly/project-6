"""
All work done by: Blake Skelly
University of Oregon
CS 322 Fall 2023

Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow


#  You MUST provide the following two functions
#  with these signatures. You must keep
#  these signatures even if you don't use all the
#  same arguments.
#

# Setup distances with times as global variables
limits = {200: 810, 400: 1620, 600: 2400, 1000: 4500}
mintimes = {0: 15, 600: 11.428}
maxtimes = {0: 34, 200: 32, 400: 30, 600: 28}

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, control distance in kilometers
       brevet_dist_km: number, nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An arrow object
    Returns:
       An arrow object indicating the control open time.
       This will be in the same time zone as the brevet start time.
    """
    # Save the start time
    stime = arrow.get(brevet_start_time)

    if brevet_dist_km < control_dist_km:
        control_dist_km = brevet_dist_km
    
    # Setup variables for function
    total_distance = 0
    time_passed = 0
    distance_remaining = control_dist_km
    distance_keys = list(maxtimes.keys())

    # Loop through the distance keys to find the brevet distance
    for i in range(len(distance_keys)):
        if distance_keys[i] >= control_dist_km:
            break
        else:
            total_distance = i

    # Loop to find how much distance is left in the brevet and update distance
    for j in range(total_distance, -1, -1):
        if distance_remaining == 0:
            break
        difference = distance_remaining - distance_keys[j]
        time_passed += difference / maxtimes[distance_keys[j]]
        distance_remaining -= difference

    time_passed = round(time_passed * 60)

    # Return the open time of the location
    return stime.shift(minutes = time_passed)


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, control distance in kilometers
          brevet_dist_km: number, nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An arrow object
    Returns:
       An arrow object indicating the control close time.
       This will be in the same time zone as the brevet start time.
    """
    # Setup variables for function
    stime = arrow.get(brevet_start_time)
    total_distance = 0
    time_passed = 0
    distance_remaining = control_dist_km
    distance_keys = list(mintimes.keys())
    
    # Shift the location time to account for special cases for the brevet

    # Close one hour after if there is no distance left
    if control_dist_km == 0:
        return stime.shift(minutes = 60)

    # Set location close if location is within 60 km of the start of the brevet
    elif control_dist_km <= 60:
        time_passed = round(control_dist_km / 20 * 60 + 60)
        return stime.shift(minutes = time_passed)

    if brevet_dist_km <= control_dist_km:
        return stime.shift(minutes = limits[brevet_dist_km])

    # loop through the distance keys to find the brevet distance
    for i in range(len(distance_keys)):
        if distance_keys[i] >= control_dist_km:
            break
        else:
            total_distance = i

    # Loop to find how much distance is left in the brevet and update distance
    for j in range(total_distance, -1, -1):
        if distance_remaining == 0:
            break
        difference = distance_remaining - distance_keys[j]
        time_passed += difference / mintimes[distance_keys[j]]
        distance_remaining -= difference

    time_passed = round(time_passed * 60)

    # Return the close time of the location
    return stime.shift(minutes = time_passed)

import csv
import matplotlib.pyplot as plt
from matplotlib import animation

"""Issues brought up
    1. can be more efficient with the csv module I imported
    2. need to understand this logic about plotting
    3. reformat this using classes because this will increasinly get messy and I would also want the option of:
        a. switching between position displaying
        b. normalised display
        c. tilt angles
        d. acceleration values
        e. critical tilt angles
        f. maximum acceleration values beyond which we ignore (error handling?)
        
    """ 
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

with open("sensor_log.csv", mode = "r") as log_file:
    log_file_read = log_file.read() # read whole file
    log_file_list = log_file_read.split("\n")
    log_file_list_000 = log_file_list.pop(0) # removes first instance of list (header: "timestamp,x,y,z")
    
    x = []
    y = []
    z = []
    
    for i in log_file_list:
        coordinate = i.split(",")
        
        if len(coordinate) >= 4:
            try:
                x.append(float(coordinate[1]))
                y.append(float(coordinate[2]))
                z.append(float(coordinate[3]))
                
                # getting the tilts angles from these, in radians
            
            except ValueError:
                print("Input {i} is invalid") # an almost redundant prompt

        ax.scatter(x,y,z)
        plt.pause(0.1)  
    plt.show()
                


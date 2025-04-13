import csv
import matplotlib.pyplot as plt
from matplotlib import animation
import math

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
        
    probably need this for the .csv thing:
        https://docs.python.org/3/library/csv.html
        
    """


class AccelerometerData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.timestamps = []
        self.x = []
        self.y = []
        self.z = []
        self.tilt_xz = []
        self.tilt_xy = []
        self.tilt_zy = []
        self.unit_vector = []
        self.data_loaded = False
        
    def load_data(self):
        with open(self.file_path, mode = "r") as log_file:
            log_file_read = log_file.read() # read whole file
            log_file_list = log_file_read.split("\n")
            
            r_header = log_file_list.pop(0) # remove header (i.e. "timestamps, x, y, z")
           
            for i in log_file_list:
                coordinate = i.split(",")
                
                if len(coordinate) >= 4:
                    try:
                        timestamp = float(coordinate[0])
                        local_x = float(coordinate[1])
                        local_y = float(coordinate[2])
                        local_z = float(coordinate[3])
                        
                        self.timestamps.append(timestamp)
                        self.x.append(local_x)
                        self.y.append(local_y)
                        self.z.append(local_z)
                     
                    
                    except ValueError:
                        print("Input {i} is invalid") # an almost redundant prompt
                        
        self.data_loaded = True                           
        return self                                

    def calculate_tilt_angles(self):
        if not self.data_loaded:
            self.load_data()
            
        for i in range(len(self.x)):
            self.tilt_xz.append(math.atan2(self.z[i], self.x[i]))
            self.tilt_xy.append(math.atan2(self.y[i], self.x[i]))
            self.tilt_zy.append(math.atan2(self.z[i], self.y[i]))
            
        return self
        
    def normalise_data(self):
        if not self.data_loaded:
            self.load_data()
            
        
        for i in range(len(self.x)):
            acc_unit_vector = []
            mag_acc = math.hypot(self.x, self.y, self.z)
            unit_x, unit_y, unit_z = self.x/mag_acc, self.y/mag_acc, self.z/mag_acc
            acc_unit_vector.append(unit_x, unit_y_, unit_z)
            self.unit_vector.append(acc_unit_vector)
            
        return self
    

test = AccelerometerData("sensor_log.csv")
test.load_data()



"""
class AccelerometerVisualiser:
    def __init__(self, data):
        self.data = data
        self.fig = None # I have no idea why I am doing that
        self.ax = None  # Not a scooby doo about this either
    def 
        
        
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')


        ax.scatter(x,y,z)
        plt.pause(0.1)  
    plt.show()
"""         


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
            mag_acc = math.hypot(self.x[i], self.y[i], self.z[i])
            unit_x, unit_y, unit_z = self.x[i]/mag_acc, self.y[i]/mag_acc, self.z[i]/mag_acc
            acc_unit_vector = (unit_x, unit_y, unit_z)
            self.unit_vector.append(acc_unit_vector)
            
        return self
    

test = AccelerometerData("sensor_log.csv")
test.normalise_data()
print(test.unit_vector)


class AccelerometerVisualiser:
    def __init__(self, data):
        self.data = data
        self.fig = None # I have no idea why I am doing that
        self.ax = None  # Not a scooby doo about this either
    def setup_mpl(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_xlabel('X Label')
        self.ax.set_ylabel('Y Label')
        self.ax.set_zlabel('Z Label')
        return self
    
    def acceleration_input():
        
    def tilt_input():
    
    
    
def main():
    accel_data = AccelerometerData("sensor_log.csv").load_data()
    
    visualiser = AccelerometerVisualiser(accel_data)
    
    to_choose = True
    while to_choose:
        try:
            choices = int(input("Choose the type of visualisation for your sensor data:\n1. Vector Visualisation With Acceleration Data\n2. Vector Visualisation With Tilt Data\n\nPress '0' to quit."))
            if choices == 0:
                print("Thank you for participating.")
                to_choose = False
                break
            
            elif choices != 1 or != 2:
                print("Choose a number in range.")
                
            elif choices == 1:
                visualiser.acceleration_input()
                plt.show()
                to_choose = False
                break
            
            elif choices == 2:
                visualiser.tilt_input()
                plt.show()
                to_choose = False
                break
                
        except ValueError:
            print("Enter an integer. Try again.")
    
main()
"""
Note: I have seen the below be done but I am unsure of its relevance here -- 
if __name__ == "__main__": # I have seen this be done and I think it's kinda silly 
    main()

"""         


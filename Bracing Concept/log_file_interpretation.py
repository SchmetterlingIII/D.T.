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


class AccelerometerVisualiser:
    def __init__(self, data):
        self.data = data
        self.fig = None
        self.ax = None
        
    def setup_plot(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_xlabel('X Label')
        self.ax.set_ylabel('Y Label')
        self.ax.set_zlabel('Z Label')
        return self

    def display_acceleration(self):
        if not self.fig or not self.ax:
            self.setup_plot()
        
        self.ax.clear()
        self.ax.scatter(self.data.x, self.data.y, self.data.z)
        self.current_display_mode = "position"
        self.ax.set_proj_type('ortho')
        self.ax.set_xlabel('X Axis')
        self.ax.set_ylabel('Y Axis')
        self.ax.set_zlabel('Z Axis')
        self.ax.set_title('Superimposition of acceleration points from sensor')
        return self

    def display_tilt_angles(self):
        # First ensure tilt angles are calculated
        if not hasattr(self.data, 'tilt_xz') or not self.data.tilt_xz:
            self.data.calculate_tilt_angles() # calls back into the old boy to run its thing
        
        if not self.fig:
            self.fig = plt.figure()
            
        # 2D plot for angles rather than the 3D thingies
        self.ax = self.fig.add_subplot()
        self.ax.plot(self.data.timestamps, self.data.tilt_xz, label='XZ Tilt')
        self.ax.plot(self.data.timestamps, self.data.tilt_xy, label='XY Tilt')
        self.ax.plot(self.data.timestamps, self.data.tilt_zy, label='ZY Tilt')
        self.ax.legend()
        self.current_display_mode = "tilt_angles"
        self.ax.set_xlabel('Arbitary Time Unit (s)')

        self.ax.set_ylabel('Angle of Tilt (rad)')
        return self
        
    def animate_normalised_vectors(self):
        #option here to choose whether you want to do this animation through acceleration data or tilt (the vector arrow will show up all the same)
        if not self.fig or not self.ax:
            self.setup_plot()
        
        self.ax.set_xlim([-1.25, 1.25])
        self.ax.set_ylim([-1.25, 1.25])
        self.ax.set_zlim([-1.25, 1.25])
        
        start = [0,0,0]
        for i in range(len(self.data.x)):
            self.ax.quiver(start[0], start[1], start[2], self.data.unit_vector[i][0], self.data.unit_vector[i][1], self.data.unit_vector[i][2])
            
            
        self.ax.view_init(10,10,10)
        return self
            # plt.cla() -- clears the plot
        
"""
v = [0,5,4]
q = [7,-8,10]

fig = plt.figure()
ax = plt.axes(projection = '3d')
ax.set_xlim([-10, 10])
ax.set_ylim([-10,10])
ax.set_zlim([-10,10])

start = [-10,-10,-10]
for i in range(15):
    u = [i,(i+1),(i-1)]
    ax.quiver(start[0], start[1], start[2], u[0], u[1], u[2])
    plt.pause(1)
    plt.cla()
    
    # Reset the limits after clearing the axes
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_zlim([-10, 10])

ax.view_init(10, 10, 10)
plt.show()
"""
        
    
def main():
    accel_data = AccelerometerData("sensor_log.csv").load_data()
    
    visualiser = AccelerometerVisualiser(accel_data)
    
    normalising = AccelerometerData("sensor_log.csv").normalise_data()
    
    normal = AccelerometerVisualiser(normalising)
    
    to_choose = True
    
    while to_choose:
        try:
            choices = int(input("Choose the type of visualisation for your sensor data:\n1. Vector Visualisation With Acceleration Data\n2. Vector Visualisation With Tilt Data\n3. Normalised Vector Visualisation\nPress '0' to quit.\n"))
            if choices == 0:
                print("Thank you for participating.")
                to_choose = False
                break
                
            elif choices == 1:
                visualiser.display_acceleration()
                plt.show()
                to_choose = False
                break
            
            elif choices == 2:
                visualiser.display_tilt_angles()
                plt.show()
                to_choose = False
                break
            elif choices == 3:
                normal.animate_normalised_vectors()
                plt.show()
                to_choose = False
                break
            else:
                print("Choose a number in range.")
                
        except ValueError:
            print("Enter an integer. Try again.")
    
main()
"""
Note: I have seen the below be done but I am unsure of its relevance here -- 
if __name__ == "__main__": # I have seen this be done and I think it's kinda silly 
    main()

"""         


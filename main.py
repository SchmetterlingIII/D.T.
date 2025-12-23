import serial.tools.list_ports
import string
import serial

import matplotlib.pyplot as plt
from  mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

import time
from collections import deque
import numpy as np
from scipy.interpolate import CubicSpline
import scipy
import sys

########################

BAUDRATE = 115200
try:
    '''
    Basic setup for port communication
    '''

    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()
    portList = [str(i) for i in ports]
    print(portList)

    com = input("Select COM PORT for Arduino: ")

    for i in range(len(portList)):
        if portList[i].startswith("COM" + str(com)):
            SERIAL_PORT = "COM" + str(com)
            print(SERIAL_PORT)

    serialInst.baudrate = BAUDRATE
    serialInst.port = SERIAL_PORT
    serialInst.open()
    print(f"Connected to {SERIAL_PORT} at {BAUDRATE} baud.")

    '''
    Initial data initialisation.
    This is a complementary function to the c++ code which says how many sensors are connected and which positions they are in.
    '''
    while True:
        line = serialInst.readline().decode('utf-8') # each line is the decoded form of the serial
        if line: # if there is data in the readline i.e if line == True
            print(f"Arduino: {line}")
        if "Available channels: " in line:
            channels_part = line.split(":")[-1].strip() # extract all data after colon
            # parse the csv into on stringed list
            IMU_ID_LIST = [id.strip() for id in channels_part.split(",") if id.strip()]
        if "Number of sensors: " in line:
           ID_NUM = int(line.strip(":")[-3]) # the number of read sensors, last instance is "\n" and so index = -3 is the appropriate index
           imu_deques = [deque(maxlen=50) for i in range(ID_NUM)] # lowercase for downstream effects
        if "Waiting for 'begin program' command" in line:
            break

    '''
    Input of linear distances for the forward kinematics chain (and subsequent calculations)
    '''
    print("INSTRUCTIONS:\nInput the linear distances between your sensors in metres.\nMeasure from lowest to highest.\nI would recommend using a high resolution ruler to reduce drift.\n")
    linear_distances = []
    for i in range(ID_NUM - 1):
        value = float(input(f"{i + 1}: "))
        linear_distances.append(value)

    print("Sending 'begin' command to Arduino")
    serialInst.write(b'begin program') # sent in bytes rather than a high level string since it is sent to back to the compiler

    time.sleep(2)
    
########################
    def angle_tilt_filter(IMU_data, dt):
        '''
        https://www.youtube.com/watch?v=7VW_XVbtu9k
        Use the above video to extract the angle between each of the IMUs.

        This is less susceptible to gyro tilt over time

        Return: normalised matrix containing the vector values of each of the filtered IMUs using this angle extraction method.
        '''

        '''
        each data is streamed one at a time.
        find the local pitch and yaw
        from these angles, get the appropriate direction vector
        store into the matrix

        return np.array([(), (), (), ..., ()])
        '''
        ax, ay, az, gyro_x, gyro_y, gyro_z = IMU_data

        accel_angle_x = np.arctan2(ay, az) # about the x-axis
        accel_angle_y = np.arctan2(ax, az) # about the y-axis

        gyro_x += gyro_x * dt
        gyro_y += gyro_y * dt

        # rather than a filter yet, I will just have a bias towards angular tilt
        # these numbers are arbitrary (copied from the video) but I will move onto Kalman filtering later
        fused_angle_x = 0.98 * (gyro_x) + 0.02 * accel_angle_x # roll
        fused_angle_y = 0.98 * (gyro_y) + 0.02 * accel_angle_y # pitch

        normal, y_direction = angles_to_direction_vector(fused_angle_x, fused_angle_y)

        return normal, y_direction

    def angles_to_direction_vector(roll, pitch):
        '''
        Calculates normal vector and direction vector in direction of y-axis.

        The y-axis direction vector will be used for the forward kinematics; the normal vector will reinforce calculations of curvature (and be the precursor to having a 3D understanding of curvature along the spine).
        '''
        # normal
        normal = np.array([
            np.sin(pitch) * np.cos(roll),
            -np.sin(roll),
            np.cos(roll) * np.cos(pitch)
        ])

        # y direction
        y_direction = np.array([
            np.sin(pitch) * np.sin(roll),
            np.cos(roll),
            np.cos(pitch) * np.sin(roll)
        ])

        normal = normal / np.linalg.norm(normal)
        y_direction = y_direction / np.linalg.norm(y_direction)

        return normal, y_direction

    def kalman_filter(angle_filtered_data):
        '''
        https://www.youtube.com/watch?v=5HuN9iL-zxU&list=PLeuMA6tJBPKsAfRfFuGrEljpBow5hPVD4&index=18
        Another tutorial that will help me actually have an accurate input of the data, without resorting to l'IA or learning the maths behind this.

        I will look into how Kalman filters work from a high level but if there is a python module for it then I will be happy to just copy it.
        '''
        return filtered_data

    def forward_kinematics(filtered_data, linear_distances):
        '''
        Computes positions using the IMU data and distances, assuming that the base IMU is at the origin.
        Returns: list of 3D positions where the IMUs are in an arbitrary & scaled 3D space

        For later improvements, I will use quaternions to handle the tilt as done in the CHARM Lab device.
        '''

        # if no data, return nothing important (in the same format which can be unpacked but not causing a crash)
        if not filtered_data:
            return np.array([]), np.array([])

        origin = np.array([0,0,0])
        p_n = [origin]
        cumulative_distance = 0
        t_values = [0]

        for i in range(len(filtered_data)):
            v_n = filtered_data[i] # the direction vector at this point
            l_n = linear_distances[i] if i != (len(filtered_data) - 1) else 0.1 # the scalar distance between the upcoming sensor and the current
            # I have added the 0.1 since the final IMU will not have a subsequent sensor to work towards so this tilt will approximate what's happening up to the neck area

            p_n_plus_1 = p_n[-1] + (v_n * l_n) # the next position vector along the chain
            p_n.append(p_n_plus_1)

            cumulative_distance += l_n
            t_values.append(cumulative_distance)

        return p_n, t_values # returns vector position & t_values for interpolation

    def cubic_spline_interpolation(IMU_positions, t_values):
        '''
        Interpolates the function using the formed kinematic chain in a parametrised format.

        Returns the plotting values
        '''
        x = IMU_positions[:, 0]
        y = IMU_positions[:, 1]
        z = IMU_positions[:, 2]

        xc = CubicSpline(t_values, x)
        yc = CubicSpline(t_values, y)
        zc = CubicSpline(t_values, z)

        # this variable stores the t_values that are along this interpolated spline in a discrete package i.e. "plotting_t_values"
        discrete_points = 250
        plot_t = np.linspace(min(t_values), max(t_values), discrete_points)

        return xc, yc, zc, plot_t

    def curvature_list(xc, yc, zc, plot_t):
        '''
        This function returns an array of scalar curvatures for each point on the interpolated spline function.

        The issue with this (for future reference) is that these points only show a scalar and so improvements of this could be to interpolate the normal values of the vectors along the function to have a better understanding of curvature in 3D space.
        '''
        r = np.array([xc(plot_t, 0), yc(plot_t, 0), zc(plot_t, 0)]).T
        r_prime = np.array([xc(plot_t, 1), yc(plot_t, 1), zc(plot_t, 1)]).T
        r_double_prime = np.array([xc(plot_t, 2), yc(plot_t, 2), zc(plot_t, 2)]).T

        kappa = (np.linalg.norm(np.cross(r_prime, r_double_prime)))/(np.linalg.norm(r_prime)**3)
        return kappa # an array of scalar values for the curvature along this interpolated spline
    
    class SpineAnalysis:
        def __init__(self, t_values):
            self.is_calibrating = True
            self.calibration_duration = 30
            self.calibration_dataset = []
            self.timer = time.time()
            self.calibrated_data = []


            self.deviance_indices = [] 

            self.poor_posture_timer = 5
            self.poor_posture_start = None # using time.time() (or more efficient/local clocks for performance reasons)
            self.poor_posture_ticker = 0 # it increments if there is an instance of poor posture detect
            self.sustained_poor_posture = False

            self.cumulative_lengths = t_values
            self.segments = None

        def dataset_update(self, curvature_instance):
            '''
            INPUT: curvature_instance
            OUTPUT: calibration_dataset
            RUNTIME: ['to be called in the main function for duration=calibration-duration']
            '''
            # exit if this function was mistakenly called
            if self.is_calibrating == False:
                return 

            self.calibration_dataset.append(curvature_instance)

        def output_calibration_data(self):
            '''
            INPUT: self.calibration_dataset
            OUTPUT: self.calibrated_data
            FUNCTION: 
            '''
            
            if len(self.calibration_dataset) < 5:  # minimum samples for meaningful IQR
                print(f" Only {len(self.calibration_dataset)} calibration samples collected")
                self.is_calibrating = False
                return
            
            calibration_matrix = np.array(self.calibration_dataset)
            if calibration_matrix.ndim == 1:
                calibration_matrix = calibration_matrix.reshape(1, -1)

            # for each of the 250 spline positions, compute the IQR bounds 
            for i in range(250):
                column = calibration_matrix[:, i]
                q1 = np.percentile(column, 25)
                q3 = np.percentile(column, 75)
                # I commented out these to have basic tests done; complexity comes later.
                # iqr = q3 - q1
                # a = q1 - (1.5 * iqr)
                # b = q3 + (1.5 * iqr) 
                self.calibrated_data.append((q1, q3))
                
            self.calibrated_data = np.array(self.calibrated_data)
            self.is_calibrating = False

        def posture_detector(self, curvature_instance):
            '''
            INPUT:      curvature_instance
            OUTPUT:     if deviation-signal = True; self.poor_posture_ticker += 1,  self.deviance_indices.append(['indices of posture deviances stored in a temporary list structure for each increment step'])
            FUNCTION:   Reads current instance of curvature and compares it to the calibration-dataset. If there are any deviances, they are to be taken note of 
                        if self.poor_posture_ticker >= ['some defined value'] and ['the mean length of the lists in self.deviance_indices is greater than some value (so that noise doesn't cause the whole system to crash)']; reroute this function to a different handling one automatically
            '''
            curvature_instance = np.array(curvature_instance)
            if not self.calibrated_data:
                self.output_calibration_data()
            
            # if there is no current instance of poor posture (i.e no timer) then empty the list for the deviances
            if self.poor_posture_ticker == 0: 
                self.deviance_indices = []

            # for each of the 250 spline positions, if the given point is not in the range of the calibrated data it has deviated
            local_list = []
            for i in range(250):
                index = curvature_instance[i]
                a = self.calibrated_data[i][0]
                b = self.calibrated_data[i][1]
                if not (a <= index <= b):
                    local_list.append(i)
            self.deviance_indices.append(np.array(local_list))
            
            if self.deviance_indices:
                self.poor_posture_ticker += 1
        
            # This should be handled in the main loop, otherwise the unpacking of data would cause crashes:::
            # if self.poor_posture_ticker >= 10: # arbitrary value
                # self.sustained_posture_deviance()

        def sustained_posture_deviance(self, curvature_instance):
            '''
            INPUT:      curvature_instance, self.deviance_indices
            OUTPUT:     signal-to-serial ['e.g. "HIGH, 4"']
            FUNCTION:   Finds the mean (and weighted temporally) index of where the deviations have been up until the poor_posture_tickers maximum (and ongoing) by checkign through self.deviance_indices. 
                        I can determine a map of which clusters of areas are deviating and send codes to them. The separation of clusters may be difficult.
            '''
            # segment the spine with the linear distances to proportionally break down the spine 
            if self.segments is None:
                self.segmentation_algorithm()

            # aggregate all the deviated indices from the sliding window into one list
            recent_deviations = []
            for each_list in self.deviance_indices[-self.poor_posture_timer:]: # this value is dependent on what I have set the max poor_posture_ticker to be, i.e. the poor_posture_timer assuming tick has a time period of a second
                recent_deviations.extend(each_list) # rather than append such that it is only one, flattened list (rather than appended subcomponents)

            motor_counts = [0] * (len(self.segments) - 1) # one motor per segment (i.e. per IMU)
     
            for indx in recent_deviations:
                for seg_i in range(len(self.segments) - 1):
                    if self.segments[seg_i] <= indx < self.segments[seg_i + 1]:
                        motor_counts[seg_i] += 1
                        break

            # output simple code of [('HIGH'), ('position along spline')]
            # NB: there will only be the 'HIGH' setting until further testing

            threshold = 5 # arbitrary and only for testing now, this will be made more complex later
            commands = []
            for motor_id, count in enumerate(motor_counts): # output like (0, 15)
                if count > threshold:
                    commands.append(('HIGH', motor_id)) # the medium and low settings will come after
            return commands

        def segmentation_algorithm(self):
            '''
            INPUT:      self.cumulative_distances
            OUTPUT:     self.segments
            FUNCTION:   Scales the cumulative distances proportionally to the number of created segments in the discretised function (250) and outputs the list of self.segments
            '''

            self.cumulative_lengths = np.array(self.cumulative_lengths)

            # this result outputs a scaled list where 250 is now at the maximum
            self.segments = (self.cumulative_lengths / max(self.cumulative_lengths)) * 250

        def spatio_temporal_deviance_clustering(self):
            '''
            This function will have a weighting applied to the deviances in self.deviance_indices that is more responsive and accurate (i.e. more robust to noise)
            '''
            # cluster (spatially) the deviance_indices

            # cluster (temporally) the deviance_indices (in a sliding window of the most recent 5 since these will be continually updated)
            return None
        
    fig = plt.figure(figsize=(15,9))
    ax = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122)

    # scatter = ax.scatter([], [], [], s=50) # we can scatter later tbh
    line, = ax.plot([], [], [])
    # scatter_hotspot = ax.scatter([], [], [], color='red', s=50)

    curv_line, = ax2.plot([], [])

    ax.set_title("IMU Positions")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    
    ax2.grid()
    
    spine_instance = None # the variable that will hold the class 
    last_update_time = time.time() # so that the dt structure in the function doesn't just die

    def animate(i):
        global spine_instance, last_update_time

        # dt calculation (that calcs timestep between each call of the function)
        current_time = time.time()
        dt = current_time - last_update_time
        last_update_time = current_time

        # check if serial has data
        # {INTENTION}: check if serial has data from ALL channels
        try:
            if not serialInst.in_waiting:
                return line, curv_line

            serial_line = serialInst.readline().decode('utf-8').strip()
            '''
            Clean up data such that I can use the IMU class and the helper functions later.
            I need to get the data such that it is just direction vector data (and then I can finally just use the 'dt' calculations to properly extract IMU data)
            I do not know whether this will cause threading issues (if it does I will remove that functionality an look to understanding threading and toher bttlenecks as I try to code out this function (lord have mercy))
            '''
            parts = serial_line.split(',')
            imu_id = parts[-1]
            imu_data = [float(data) for data in parts[:-1]]

            '''
            I think a better solution would be the storage of data such that the animate function will not run until all the channels (for this specifc timestep) are full (i.e there isn't a continuous (very small, but present) lag in the system).
            This would require me rewriting this to account for this lag; what is the complexity of this fix?
            '''        
            # Here is the categorisation lines which associates the data of each imu to a specific channel that will be read in:
            try:
                target_imu_index = IMU_ID_LIST.index(str(imu_id)) 
                imu_deques[target_imu_index].append(imu_data)

            except ValueError:
                print(f"Warning: Recieved data from unknown data channel @ ID:{imu_id}")

            # if there is data in all the imu_deques
            if all(imu_deques):
                # using the data from the imu, get the most specific direction vector positions 
                filtered_data = []
                for i in range(len(imu_deques)):
                    ___, vector_direction = angle_tilt_filter(imu_deques[i][-1], dt) # (the first output vector will be used for torsion calculations, with the orientation of data changing; for this test, the 'y-direction' is all that is needed)
                    filtered_data.append(vector_direction)
                
                # using this, do forward kinematics
                position_vectors, t_values = forward_kinematics(filtered_data, linear_distances)

                # using this, do cubic spline interpolation
                position_vectors = np.array(position_vectors)
                xc, yc, zc, plot_t = cubic_spline_interpolation(position_vectors, t_values)

                # using this, do the curvature calcualtion
                curvature_instance = curvature_list(xc, yc, zc, plot_t)

                # create spine_instance instance if None
                if spine_instance is None: 
                    spine_instance = SpineAnalysis(t_values)
     
                # now do calibration 
                if spine_instance.is_calibrating:
                    if (time.time() - spine_instance.timer) < spine_instance.calibration_duration:
                        spine_instance.dataset_update(curvature_instance)
                    else:
                        spine_instance.output_calibration_data()
                        print("Calibration Completed")

                # collect the data as usual for the posture detection
                spine_instance.posture_detector(curvature_instance)

                # now run the conditional if there is a deviation 
                sustained_threshold = 5  # currently an arbitrary value
                if spine_instance.poor_posture_ticker >= sustained_threshold:
                    commands = spine_instance.sustained_posture_deviance(curvature_instance)
                    for level, motor_id in commands:
                        cmd = f"{level},{motor_id}\n"
                        try:
                            serialInst.write(cmd.encode('utf-8'))
                        except Exception as e:
                            print("Failed to send command:", e)
                    # reset ticker and deviance list
                    spine_instance.poor_posture_ticker = 0
                    spine_instance.deviance_indices = []

                # 3D plot of interpolated spine
                line.set_data(xc(plot_t), yc(plot_t))
                line.set_3d_properties(zc(plot_t)) 

                # graph of the curvature distribution against index (that also dynamically updates)
                x = np.arange(len(curvature_instance)) # which should be 250, but just to make sure
                y = curvature_instance
                curv_line.set_data(x, y)
                
                ax.relim()
                ax.autoscale_view()
                ax2.relim()
                ax2.autoscale_view()
                
        except Exception as e:
            import traceback
            print(f"\n{'='*60}")
            print(f"ERROR in animate():")
            print(traceback.format_exc())
            print(f"{'='*60}\n")
            return line, curv_line

    anim = FuncAnimation(fig, animate, cache_frame_data=False, interval=100, blit=False) # blitting only draws the dynamic aspects of the plot
    # apprently blitting in 3d is less cool so I got rid of it 

    ax.set_box_aspect([1,1,1])
    ax.set_proj_type('ortho')
    plt.tight_layout()
    plt.show()
    
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    line_number = exc_traceback.tb_lineno
    print(f"ERROR: {e}, line {line_number}")


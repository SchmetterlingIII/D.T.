from microbit import *
import time

with open("sensor_log.csv","w") as f:
    f.write("timestamp,x,y,z\n") 
    while True:
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()
        
        f.write("{},{},{},{}\n".format(time.ticks_ms(),x,y,z))
        
        print((x,y,z))  
        sleep(45)

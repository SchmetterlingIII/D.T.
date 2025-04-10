import csv
import matplotlib

def fileReadingPractice():
    with open("sensor_log.csv", mode = "r") as log_file:
        log_file_read = log_file.read() # read whole file
        log_file_list = log_file_read.split("\n")
        log_file_list_000 = log_file_list.pop(0) # removes first instance of list (header: "timestamp,x,y,z")
        
        for i in log_file_list:
            coordinate = i.split(",")
            x = coordinate[1]
            y = coordinate[2]
            z = coordinate[3]
            
        
fileReadingPractice()

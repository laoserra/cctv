#----This script creates/appends a more readable version of the file "detections.csv"----#

#!/usr/bin/env python
# coding: utf-8

# import packages
import os
import pandas as pd
import csv
from datetime import datetime

# read csv file with image detections from pretrained model
df = pd.read_csv('./output_folder/detections.csv')

# group by image and type of object and perform counts
counts = df.groupby(['image_id', 'object']).count().score

# filter rows with the objects of interest
counts = counts[counts.index.get_level_values(1).isin(['bicycle', 'car', 'person'])]

#put all the images in a list object
images = counts.index.get_level_values(0).unique()

# create or append a csv file with counts per object of interest
timestamp = datetime.now() #Return the current local date and time
if os.path.isfile('./output_folder/report.csv'):
    with open('./output_folder/report.csv', 'a') as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        
        car = 0
        person = 0
        bicycle = 0
        motorcycle = 0
        bus = 0
        truck = 0
        for i in range(len(images)):
            for j in range(len(counts)):
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'car':
                    car = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'person':
                    person = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'bicycle':
                    bicycle = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'motorcycle':
                    motorcycle = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'bus':
                    bus = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'truck':
                    truck = counts[j]
#            print(timestamp, images[i], car, person, bicycle, motorcycle, bus, truck, sep=",") 
            row = [timestamp, images[i], car, person, bicycle, motorcycle, bus, truck] 
            writer.writerow(row)
            car = 0
            person = 0
            bicycle = 0
            motorcycle = 0
            bus = 0
            truck = 0
else:
    with open('./output_folder/report.csv', 'a') as file:
        file.write('timestamp,image,car,person,bicycle,motorcycle,bus,truck\n')
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        
        car = 0
        person = 0
        bicycle = 0
        motorcycle = 0
        bus = 0
        truck = 0
        for i in range(len(images)):
            for j in range(len(counts)):
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'car':
                    car = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'person':
                    person = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'bicycle':
                    bicycle = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'motorcycle':
                    motorcycle = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'bus':
                    bus = counts[j]
                    continue
                if images[i] == counts.index[j][0] and counts.index[j][1] == 'truck':
                    truck = counts[j]
#            print(timestamp, images[i], car, person, bicycle, motorcycle, bus, truck, sep=",") 
            row = [timestamp, images[i], car, person, bicycle, motorcycle, bus, truck] 
            writer.writerow(row)
            car = 0
            person = 0
            bicycle = 0
            motorcycle = 0
            bus = 0
            truck = 0

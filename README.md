# cctv project

This is a pilot project developed by Urban Big Data Centre and Glasgow City Council with the aim of counting the number of persons and vehicles in cctv images. 

To achieve this aim we make use of the tensorflow object detection API from Google, available in:

https://github.com/tensorflow/models/tree/master/research/object_detection

This API makes use of object detection algorithms to extract instances of real-world objects in images.

In this project a picture is taken every 15 minutes in a specific position - home position. Afterwards the images are processed with TensorFlow Object Detection API and the result of the count for each of the four cameras in the test is appended to a csv file.

A server machine running Ubuntu Server was used to run the project. Please refer to the installation steps to know more about the configuration of the server.



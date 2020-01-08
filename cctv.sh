#!/bin/bash
#
# PATH the same as $env
PATH=/usr/local/cuda-10.0/bin:/home/ls283h/.local/bin:/home/ls283h/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/ls283h/bin
#
# directory of python virtual environments
WORKON_HOME=/home/ls283h/python-virtual-environments

cd /home/ls283h/Work/CCTV/production/
#source virtualenvwrapper.sh
#workon cctv
source /home/ls283h/python-virtual-environments/cctv/bin/activate

python detect_objects.py conf_filepath
python count_objects.py
mv output_folder/detections.csv output_folder/detections_$(date '+%FT%T').csv

#!/usr/bin/roothon

import multiprocessing as mp
from datetime import datetime
import time
import tracker
import geocoder
import cgi
import cgitb
cgitb.enable()

lat, lon = geocoder.ip('me').latlng

# path = path_to_picture_folder
pic_name = datetime.now().strftime('img_%y-%m-%d_%H-%M')

data = cgi.FieldStorage()

body = data.getvalue('body')
ss = data.getvalue('exposure')
iso = data.getvalue('iso')

if 'ABORT' in data:
    tracker.abort()
    # End and print

else:
    travel = mp.Process(target=tracker.track_body, args=(body, lat, lon, ss, 30))
    capture = mp.Process(target=tracker.capture, args=(ss, iso, pic_name, path))
    # print temp webpage?
    capture.join()
    # if it hasn't happend all ready
    travel.terminate()
    travel.join()

# print new webpage
print('Content-type:text/html\n\n')


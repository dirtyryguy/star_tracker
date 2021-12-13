#!/usr/bin/roothon

import sys
sys.path.append('/home/pi/.python3_packages/')

import socket
import multiprocessing as mp
from datetime import datetime
import time
import eq_tracker
import geocoder
import os
from shutil import make_archive
import cgi
import cgitb

cgitb.enable(display=0, logdir='/home/pi/temp/')

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

ip = get_ip()

os.system('sudo rm -rf /var/www/star_images/*.zip')
date = datetime.now().strftime('%y-%m-%d')
# try:
#     os.mkdir(path)
# except:
#     pass

# it's about right here where my fustration manifested itself
path = '/home/pi/html/images/'

data = cgi.FieldStorage()

auto = 'auto' in data
num_imgs = int(data.getvalue('num_imgs'))

if auto:
    ss = None
    iso = None
else:
    ss = int(data.getvalue('exposure'))
    iso = int(data.getvalue('iso'))
delay = 0

if False:
    lat, lon = geocoder.ip('me').latlng
else:
    travel = mp.Process(target=eq_tracker.start_tracker)
    capture = mp.Process(target=eq_tracker.multi_capture, args=(num_imgs, delay, ss, iso, path, auto))
    
    travel.start()
    capture.start()
    
    capture.join()
    # if it hasn't happend all ready
    travel.terminate()
    travel.join()


# make zip
make_archive(f'/home/pi/html/imgs_{date}', 'zip', path)
disp_path = 'http://' + ip + '/images/' + sorted(os.listdir(path))[-1]
download_path = 'http://' + ip + f'/imgs_{date}.zip'

# print new webpage
print('Content-type:text/html\n\n')
print(
"""
<html>
  <head>
    <title>Star Tracker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      *
      {
        box-sizing: border-box;
      }
      body
      {
        background-color: powderblue;
      }
      .col_ends
      {
        width: 10%;
        float: left;
        padding: 15px;
        /* border: 1px solid red; */
      }
      .col_left_mid
      {
        width: 50%;
        float: left;
        padding: 15px;
        background-color: white;
        text-align: center;
        border: 1px outset black;
      }
      .col_right_mid
      {
        width: 30%;
        float: left;
        padding: 15px;
        background-color: white;
        text-align: center;
        border: 1px outset black;
      }
    </style>
  <head>

  <body>
    <br><br>
    <div class="row" style="height:12.5%;">
      <div class="col_ends"></div>
      <div style="width:80%; height:100%; float:left; padding:15px; background-color:white; text-align:center; border:1px outset black;">
        <h1>Star Tracker</h1>
      </div>
      <div class="col_ends"></div>
    </div>
    
    <div class="row" style="height:70%;">
      <div class="col_ends"></div>
      <div class="col_left_mid" style="height:100%;">
"""
)

print(f'<img src="{disp_path}" width="100%" alt="{disp_path}">')

print(
"""
      </div>

      <div class="col_right_mid" style="height:100%;">
        <h3>Equatorial Control</h3>
        <form action="/cgi-bin/celeste.cgi" method="POST">
          Auto Exposure: <input type="checkbox" name="auto" value="auto">
          <br><br>
          <label for="num_imgs">Enter Number of Images:</label>
          <input type="text" name="num_imgs">
          <br><br>
          <label for="exposure">Enter Exposure Time (s):</label>
          <input type="text" name="exposure">
          <br><br>
          <label for="iso">Enter ISO:</label>
          <input type="text" name="iso">
          <br><br>
          <input type="submit" value="Submit">
          <input type="submit" value="ABORT">
        </form>
        <br>
        <h3>Manual Control</h3>
	<form action="/cgi-bin/manual_control.cgi" method="POST">
	  <input type="submit" value="-25" name="-25">
	  <input type="submit" value="-10" name="-10">
	  <input type="submit" value="-5" name="-5">
	  <input type="submit" value="+5" name="+5">
	  <input type="submit" value="+10" name="+10">
	  <input type="submit" value="+25" name="+25">
        <h3>Download Images (zip)<h3>
"""
)

print(f'<a href="{download_path}" download>Image(s)</a>')

print(
"""
      </div>

      <div class="col_ends"></div>
    </div>
    <div class="row" style="height:12.5%;">
      <div class="col_ends"></div>
      <div style="width:80%; height:105%; float:left; padding:15px; background-color:white; text-align:center; border:1px outset black;">
        <p>ENME441 Final Project<br>Jeremy Carter and Ryan Matheu<br>Fall 2021</p>
      </div>
      <div class="col_ends"></div>
    
  </body>
</html>
"""
)

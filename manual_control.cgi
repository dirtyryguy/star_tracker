#!/usr/bin/roothon

import sys
sys.path.append('/home/pi/.python3_packages/')

import eq_tracker
import cgi
import cgitb

cgitb.enable(display=0, logdir='/home/pi/temp/')

data = cgi.FieldStorage()

val = int(data.keys()[0])

eq_tracker.eq_step.rotate(abs(val), val, gear_ratio=13/60, speed=0.5)

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
        <img src="https://astrobackyard.com/wp-content/uploads/2019/06/the-celestial-sphere.jpg" width="80%">
      </div>

      <div class="col_right_mid" style="height:100%;">
        <h3>Equatorial Control</h3>
        <form action="/cgi-bin/celeste.cgi" method="POST">
	  Auto Exposure: <input type="checkbox" name="auto" value="auto">
          <br><br>
          Get Humidity: <input type="submit" name="humidity" value=" "> 0.0%
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
	</form>
	<br>
        <h3>Download Images (zip)<h3>
        <a href="path" download>Image(s)</a>
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

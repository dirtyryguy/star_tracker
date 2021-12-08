# Add to PYHTONPATH
# from light_stepper import Stepper
import time
import numpy as np
from threading import Thread
from picamera import PiCamera
# import matplotlib.pyplot as plt
from datetime import datetime
from astropy.coordinates import EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from light_stepper import Stepper


# FUNCTIONAL RULEZ
# OOP DRULEZ

# our two stepper motors controlling our movement axes
# az_step = Stepper(*args1)
# alt_step = Stepper(*args2)


def zero(*args):
    """A function used to zero the tracker in both axes.

    """

    pass


def rotate(stepper, d_a, stop_flag=True):
    """A function to continuously rotate the tracker.

    """

    while not stop_flag:
        stepper.rotate(d_a, np.sign(d_a))


def get_moon_coords(
                    lat,
                    lon,
                    obstime,    # seconds
                    dt,         # seconds
                    height=0.0
                    ):
    """Retrieves the coordinates of the moon.

    """

    from astropy.coordinates import get_moon

    curr_loc = EarthLocation.from_geodetic(lat=lat*u.deg, lon=lon*u.deg, height=height*u.m)
    delta_time = np.linspace(0, obstime,  int(obstime/dt))*u.second
    curr_time = Time(str(datetime.utcnow())) + delta_time
    curr_frame = AltAz(obstime=curr_time, location=curr_loc)
    mun = get_moon(curr_time, location=curr_loc)
    coords = mun.transform_to(curr_frame)

    coords = np.vstack((coords.alt.deg, coords.az.deg))
    return np.transpose(coords)


# dictionary of all bodies that we can retrive coordinates from
# add to as methods are added
bodies = {
          'moon' : get_moon_coords
         }


def track_body(
               body,
               lat,
               lon,
               obstime,
               dt,
               height=0.0,
               zero=True
               ):
    """Tracks the location of the body keeping it centered on the camera.
    
    This method spawns two threads that operate the individual rotation axes of the tracker.
    It was chosen to do it this way so that the axes move simultaneously.
    """

    stop_flag = False # stop_flag tells the threads when to die so to speak

    # if we wish to zero the tracker before tracking
    if zero: zero()

    # retrieving the coordinates based on the currently selected body
    coords = bodies[body](lat, lon, obstime, dt, height)

    # initialize our shared variables to be zero
    alt_d_a, az_d_a = 0.0, 0.0

    # create our threads
    alt = Thread(target=rotate, args=(alt_step, alt_d_a, stop_flag))
    az = Thread(target=rotate, args=(alt_step, alt_d_a, stop_flag))
    # start our threads
    alt.start()
    az.start()

    for coord in coords:
        tic = time.time()
        coord -= [alt_step.angle, az_step.angle]
        alt_d_a, az_d_a = coord
        while time.time() - tic < dt: pass

    stop_flag = True # should kill the threads


def capture(
            shutter_speed,
            iso,
            name=None,
            path=None
           ):
    """

    """
    
    from fractions import Fraction
    
    with PiCamera(framerate=Fraction(1, 6)) as cam:
        cam.shutter_speed = shutter_speed
        camera.iso = iso

        time.sleep(2)
        camera.exposure_mode = 'off'
        camera.capture(f'{path}/{name}.jpg')

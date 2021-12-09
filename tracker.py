# Add to PYHTONPATH
from light_stepper import Stepper
import time
import numpy as np
from threading import Thread
from picamera import PiCamera
from l2clcd import l2clcd
# import matplotlib.pyplot as plt
from datetime import datetime
from astropy.coordinates import EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u


# FUNCTIONAL RULEZ
# OOP DRULEZ

# our two stepper motors controlling our movement axes
az_step = Stepper(*args1)
alt_step = Stepper(*args2)

# instanitate our LCD module
status = Status()

class Rotate(Thread):
    """A threaded rotation class that controls the position(s) of the two steppers.

    """

    def __init__(self, stepper):
        super().__init__()
        self.stepper = stepper
        self.d_a = 0.0
        self.stop_flag = False

    def run(self):
        while not self.stop_flag: # this is important
            self.stepper.rotate(self.d_a, np.sign(self._d_a))

    def stop(self):
        self.stop_flag = True

    def set_angle(self, angle):
        self.d_a = angle


class Status(Thread):
    """A daemon thread that displays information to an LCD.

    """

    def __init__(self, stat='IDLE'):
        super().__init__(daemon=True)
        self.stat = stat
        self.lcd = i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
        self.lcd.init()
        self.lcd.set_backlight(1)

    def run(self):
        try:
            while 1: # infinitly looping thread 0_0
                self.print_status()
                time.sleep(1)
        except: pass
        finally: # this should always run at the end of the process
            self.lcd.clear()
            self.lcd.set_backlight(0)

    def set(self, stat): # four charater status flags: IDLE, MVNG, CPTR, ZERO
        self.stat = stat

    def print_status(self):
        lcd.print_line(f'alt: {alt_step.angle:4.1f} STATUS', line=0)
        lcd.print_line(f'az: {az_step.angle:5.1f}  {self.status}', line=1)
        

def zero(*args):
    """A function used to zero the tracker in both axes.

    """
    
    status.set('ZERO')
    def temp(stepper):
        while not stepper.zeroed():
            stepper.turnsteps(1, -1*stepper.rot_dir)

    alt = Thread(target=temp, args=(alt_step,))
    az = Thread(target=temp, args=(az_step,))

    alt.start(); az.start()
    alt.join(); az.join()
    status.set('IDLE')


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

    # if we wish to zero the tracker before tracking
    if zero: zero()

    # retrieving the coordinates based on the currently selected body
    coords = bodies[body](lat, lon, obstime, dt, height)

    # create our threads
    alt = Rotate(alt_step)
    az = Rotate(az_step)

    # start our threads
    alt.start()
    az.start()
    status.set('MVNG')

    for coord in coords:
        tic = time.time()
        coord -= [alt_step.angle, az_step.angle]
        alt.set_angle(coord[0])
        az.set_angle(coord[1])
        while time.time() - tic < dt: pass

    alt.stop(); az.stop()
    status.set('IDLE')


def capture(
            shutter_speed,
            iso,
            name=None,
            path=None
           ):
    """Function to control the capturing of photos.

    """
    
    from fractions import Fraction
    
    status.set('CPTR')
    with PiCamera(framerate=Fraction(1, 6)) as cam:
        cam.shutter_speed = shutter_speed
        camera.iso = iso

        time.sleep(2)
        camera.exposure_mode = 'off'
        camera.capture(f'{path}/{name}.jpg')
    status.set('IDLE')


def multi_capture(*args):
    """Function for taking multiple photos.

    """

    pass

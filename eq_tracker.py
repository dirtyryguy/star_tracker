# Add to PYHTONPATH
from light_stepper import Stepper
import time
from threading import Thread
from picamera import PiCamera
from i2clcd import i2clcd
from datetime import datetime
import RPi.GPIO as gpio
import dht11
import os

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.cleanup()

# FUNCTIONAL RULEZ
# OOP DRULEZ

# some important constants
GEAR_RATIO = 60/13
EQ_PERIOD = 86164 # sec
STEPS_PER_ROT = GEAR_RATIO*4096
SEC_PER_STEP = EQ_PERIOD/STEPS_PER_ROT

# stepper controlling the equatorial angle
eq_step = Stepper(pins=(20, 21, 19, 26), zero_pin=16)

# temp humidity sensor
th_sens = dht11.DHT11(pin=14)


class Rotate(Thread):
    """A threaded rotation class that controls the position(s) of the stepper(s).

    """
    
    def __init__(self, rot_dir=1):
        super().__init__(daemon=True)
        self.stepper = eq_step
        self.rot_dir = rot_dir
        self.stop_flag = False

    def run(self):
        while not self.stop_flag: # this is important
            tic = time.time()
            self.stepper.turnsteps(1, self.rot_dir)
            while (time.time() - tic) < SEC_PER_STEP: pass

    def stop(self):
        self.stop_flag = True

    def change_dir(self, rot_dir=None):
        if rot_dir is None:
            self.rot_dir *= -1
        else:
            self.rot_dir = rot_dir


class Status(Thread):
    """A daemon thread that displays information to an LCD.

    """

    def __init__(self, stat='IDLE', wake_pin=4):
        super().__init__(daemon=True)
        self.stat = stat
        self.lcd = i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
        self.lcd.init()
        self.lcd.set_backlight(1)
        self.wake_pin=4
        gpio.setup(self.wake_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.wake_pin, gpio.RISING, callback=self.wake, bouncetime=100)
        self.sleep = 30 # sec
        self.awake = False
        self.start_time = time.time()

    def run(self):
        try:
            tic = time.time()
            while 1: # infinitly looping thread 0_0
                self.print_status()
                time.sleep(0.5)

                if (time.time() - tic) > self.sleep:
                    # print('sleeping')
                    self.lcd.set_backlight(0)
                if self.awake:
                    self.awake = False
                    self.lcd.set_backlight(1)
                    tic = time.time()
                    
        except Exception as e:
            pass
            # print(e)
        finally: # this should always run at the end of the process
            self.lcd.clear()
            self.lcd.set_backlight(0)
            gpio.cleanup()

    def set(self, stat): # four charater status flags: IDLE, MVNG, CPTR, ZERO
        self.stat = stat

    def print_status(self):
        self.lcd.print_line(f'T+: {int(time.time() - self.start_time)}', line=0)
        self.lcd.print_line(f'STATUS: {self.stat}', line=1)

    def wake(self, *args):
        self.awake = True


def get_humidity():
    """

    """

    res = th_sens.read()
    if res.is_valid():
        rtn = res.humidity
    else:
        rtn = 0.0
    return rtn


def capture(
            shutter_speed,
            iso,
            name=None,
            path=None,
            auto=False
           ):
    """Function to control the capturing of photos.

    """
    
    from fractions import Fraction
    
    with PiCamera(framerate=Fraction(1, 6)) as cam:
        if auto:
            cam.rotation = 180
            time.sleep(2)
            cam.capture(f'{path}/{name}.jpg')
        else:
            cam.shutter_speed = shutter_speed
            cam.iso = iso
            cam.rotation = 180

            time.sleep(2)
            cam.exposure_mode = 'off'
            cam.capture(f'{path}/{name}.jpg')


def multi_capture(num_imgs, delay, shutter_speed, iso, path=None, auto=False):
    """Function for taking multiple photos.

    """

    status = Status()
    status.start()
    m = len(os.listdir(path))
    for n in range(num_imgs):
        status.set(f'CPTR {n+1}/{num_imgs}')
        img_name = f'img_{m+n+1}'
        # img_name = datetime.now(f'img_%y-%m-%d_%H-%M_{str(n+1)}')
        capture(shutter_speed, iso, name=img_name, path=path, auto=auto)
        time.sleep(delay)
    status.set('IDLE')


def start_tracker():
    """

    """
    eq = Rotate()
    try:
        eq.start()
        while 1: pass
    except Exception as e:
        pass
        # print(e)
    finally:
        gpio.cleanup()

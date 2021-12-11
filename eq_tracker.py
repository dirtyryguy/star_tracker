# Add to PYHTONPATH
from light_stepper import Stepper
import time
from threading import Thread
from picamera import PiCamera
from i2clcd import i2clcd
from datetime import datetime
import RPi.GPIO as gpio

# FUNCTIONAL RULEZ
# OOP DRULEZ

# some important constants
GEAR_RATIO = 60/13
EQ_PERIOD = 86164 # sec
STEPS_PER_ROT = GEAR_RATIO*4096
SEC_PER_STEP = EQ_PERIOD/STEPS_PER_ROT

# stepper controlling the equatorial angle
eq_step = Stepper(pins=(20, 21, 19, 26), zero_pin=16)


class Rotate(Thread):
    """A threaded rotation class that controls the position(s) of the stepper(s).

    """
    
    def __init__(self, rot_dir=1):
        super().__init__()
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

    def __init__(self, stat='IDLE'):
        super().__init__(daemon=True)
        self.stat = stat
        self.lcd = i2clcd(i2c_bus=1, i2c_addr=0x27, lcd_width=16)
        self.lcd.init()
        self.lcd.set_backlight(1)
        self.sleep = 30 # sec
        self.awake = False
        self.start_time = time.time()

    def run(self):
        try:
            tic = time.time()
            while 1: # infinitly looping thread 0_0
                self.print_status()
                time.sleep(1)

                if (time.time() - tic) > self.sleep:
                    print('sleeping')
                    self.lcd.set_backlight(0)
                if self.awake:
                    self.awake = False
                    self.lcd.set_backlight(1)
                    tic = time.time()
                    
        except Exception as e:
            print(e)
        finally: # this should always run at the end of the process
            self.lcd.clear()
            self.lcd.set_backlight(0)

    def set(self, stat): # four charater status flags: IDLE, MVNG, CPTR, ZERO
        self.stat = stat

    def print_status(self):
        self.lcd.print_line(f'T+: {int(time.time() - self.start_time)}', line=0)
        self.lcd.print_line(f'STATUS: {self.stat}', line=1)

    def wake(self):
        self.awake = True


# instanitate our LCD module
status = Status()


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


def multi_capture(num_imgs, delay, shutter_speed, iso, path=None):
    """Function for taking multiple photos.

    """

    for n in num_imgs:
        img_name = datetime.now(f'img_%y-%m-%d_%H-%M_{str(n+1)}')
        capture(shutter_speed, iso, name=img_name, path=path)
        time.sleep(delay)


def start():
    """

    """
    eq = Rotate()
    eq.start()
    status.start()
    while 1: pass

try:
    start()
except Exception as e:
    print(e)
finally:
    gpio.cleanup()

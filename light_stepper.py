# Add to PYTHONPATH
import RPi.GPIO as gpio
import time
import numpy as np

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

class Stepper:
    """

    """

    seq = ((1,0,0,0),
           (1,1,0,0),
           (0,1,0,0),
           (0,1,1,0),
           (0,0,1,0),
           (0,0,1,1),
           (0,0,0,1),
           (1,0,0,1))

    CONST_DEG_PER_HSTEP = 360.0/(512.0*8.0)

    def __init__(self, pins=(18, 21, 22, 23), zero_pin=None):
        """

        """

        self.pins = pins
        for pin in self.pins:
            gpio.setup(pin, gpio.OUT, initial=0)

        self.z_pin = zero_pin
        gpio.setup(self.z_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN) # 0V off 5V on
        
        self.curr_step = 0
        self.angle = 0.0
        self.rot_dir = 0

        self.__update()


    def delay_us(tus):
        """

        """

        endTime = time.time() + float(tus) / float(1E6)
        while time.time() < endTime:
            pass


    def zeroed(self):
        """

        """

        return bool(gpio.input(self.z_pin))


    def __update(self):
        """

        """
        
        temp = Stepper.seq[self.curr_step]
        for n, pin in enumerate(self.pins):
            gpio.output(pin, temp[n])


    def __halfstep(self, rot_dir): # -1 for cw, 1 for ccw
        """

        """
        
        s = self.curr_step
        s += np.sign(rot_dir)
        if s > 7:
            s = 0
        elif s < 0:
            s = 7
        self.curr_step = s
        self.angle += rot_dir*Stepper.CONST_DEG_PER_HSTEP
        self.__update()


    def turnsteps(self, steps, rot_dir, speed=1.0):
        """

        """

        for _ in range(steps):
            self.__halfstep(rot_dir)
            Stepper.delay_us(1000/speed)


    def rotate(self, angle, rot_dir, gear_ratio, speed=1.0, deg=True):
        """

        """
        
        self.rot_dir = rot_dir
        steps = int(angle/(Stepper.CONST_DEG_PER_HSTEP*gear_ratio))
        self.turnsteps(steps, rot_dir, speed)

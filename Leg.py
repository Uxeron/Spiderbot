from __future__ import division
import random
import Adafruit_PCA9685
import thread
from time import sleep
from inputs import get_gamepad

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

motors = [8, 9, 10, 4, 5, 6]
start = [170, 130, 180, 160, 130, 180]
limits = [330, 360, 210, 330, 360, 230]
pos = [100, 250, 0, 100, 250, 0]
speeds = [0, 0, 0, 0, 0, 0]

interval = 0.002
speed = 2
divisor = 30

def readInput():
    while True:
        events = get_gamepad()
        for event in events:
            if event.code == "BTN_TL":
                if event.state == 1:
                    speeds[5] = -speed
                else:
                    speeds[5] = 0;
            elif event.code == "ABS_BRAKE":
                if event.state == 255:
                    speeds[5] = speed
                else:
                    speeds[5] = 0;
            elif event.code == "BTN_TR":
                if event.state == 1:
                    speeds[2] = -speed
                else:
                    speeds[2] = 0
            elif event.code == "ABS_GAS":
                if event.state == 255:
                    speeds[2] = speed
                else:
                    speeds[2] = 0
            elif event.code == "ABS_X":
                if event.state < 128:
                    speeds[3] = -(128 - event.state)/divisor
                elif event.state > 128:
                    speeds[3] = (event.state - 128)/divisor
                else:
                    speeds[3] = 0
            elif event.code == "ABS_Y":
                if event.state < 128:
                    speeds[4] = (128 - event.state)/divisor
                elif event.state > 128:
                    speeds[4] = -(event.state - 128)/divisor
                else:
                    speeds[4] = 0

            elif event.code == "ABS_Z":
                if event.state < 128:
                    speeds[0] = -(128 - event.state)/divisor
                elif event.state > 128:
                    speeds[0] = (event.state - 128)/divisor
                else:
                    speeds[0] = 0
            elif event.code == "ABS_RZ":
                if event.state < 128:
                    speeds[1] = (128 - event.state)/divisor
                elif event.state > 128:
                    speeds[1] = -(event.state - 128)/divisor
                else:
                    speeds[1] = 0


thread.start_new_thread(readInput, ())

try:
    while True:

        for i in xrange(6):
            if 0 < pos[i] + speeds[i] < limits[i]:
                pos[i] += speeds[i]
            try:
                pwm.set_pwm(motors[i], 0, start[i] + int(round(pos[i])))
            except IOError:
                continue
        print pos
        #print speeds
        sleep(interval)
except KeyboardInterrupt:
    pwm = Adafruit_PCA9685.PCA9685()

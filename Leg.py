from __future__ import division
import random
import Adafruit_PCA9685
import thread
import sys
from time import sleep
from inputs import get_gamepad

pwmL = Adafruit_PCA9685.PCA9685(0x41)
pwmR = Adafruit_PCA9685.PCA9685(0x40)
pwmL.set_pwm_freq(50)
pwmR.set_pwm_freq(50)

motors = [12, 13, 14, 3, 2, 1]
start = [160, 130, 210, 170, 130, 210]
limits = [330, 360, 230, 330, 360, 210]
pos = [100, 250, 0, 100, 250, 0]
speeds = [0, 0, 0, 0, 0, 0]

interval = 0.002
speed = 3
divisor = 30

exit = False
                        # Digital inputs
movements = {"BTN_TL":   "speeds[2] = -speed if state else 0",
             "ABS_BRAKE":"speeds[2] =  speed if state else 0",
             "BTN_TR":   "speeds[5] = -speed if state else 0",
             "ABS_GAS":  "speeds[5] =  speed if state else 0",
                        # Analog inputs
             "ABS_X":    "speeds[0] = (state - 128)/divisor",
             "ABS_Y":    "speeds[1] = (128 - state)/divisor",
             "ABS_Z":    "speeds[3] = (state - 128)/divisor",
             "ABS_RZ":   "speeds[4] = (128 - state)/divisor",

             "BTN_START":"global exit; exit = True"}

def reader():
    with open("LegData.txt", "r") as inp:
        global start, limits, pos
        start = map(int, inp.readline().split(" "))
        limits = map(int, inp.readline().split(" "))
        pos = map(int, inp.readline().split(" "))

reader()

def writer():
    with open("LegData.txt", "w") as out:
        out.write(" ".join(map(str, map(int, start))) + "\r\n")
        out.write(" ".join(map(str, map(int, limits))) + "\r\n")
        out.write(" ".join(map(str, map(int, pos))) + "\r\n")

def readControllerInput():
    #global exit
    while True:
        events = get_gamepad()
        for event in events:
            if event.code in movements.keys():
                state = event.state
                exec(movements[event.code])

def readInput():
    while True:
        data = raw_input().split(" ")
        if len(data) == 3:
            if data[0] in ("lim", "limit"):
                limits[int(data[1])] = int(data[2])
                writer()
            elif data[0] in ("start", "begin"):
                start[int(data[1])] = int(data[2])
                writer()

inpThread1 = thread.start_new_thread(readControllerInput, ())
inpThread2 = thread.start_new_thread(readInput, ())



try:
    while True:
        if exit:
            raise KeyboardInterrupt

        for i in xrange(3):
            if 0 < pos[i] + speeds[i] < limits[i]:
                pos[i] += speeds[i]
            try:
                pwmL.set_pwm(motors[i], 0, start[i] + int(round(pos[i])))
            except IOError:
                print "IO Error occurred, continuing..."
                continue

        for i in xrange(3, 6):
            if 0 < pos[i] + speeds[i] < limits[i]:
                pos[i] += speeds[i]
            try:
                pwmR.set_pwm(motors[i], 0, start[i] + int(round(pos[i])))
            except IOError:
                print "IO Error occurred, continuing..."
                continue
        print map(int, pos)
        sleep(interval)
except KeyboardInterrupt:
    pwmL = Adafruit_PCA9685.PCA9685(0x41)
    pwmR = Adafruit_PCA9685.PCA9685(0x40)
    writer()
    print "Program stopping"

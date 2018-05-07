from __future__ import division
import random
import Adafruit_PCA9685
import thread
from time import sleep
from inputs import get_gamepad

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

motors = [8, 9, 10, 4, 5, 6]
start = [170, 130, 210, 160, 130, 210]
limits = [330, 360, 210, 330, 360, 230]
pos = [100, 250, 0, 100, 250, 0]
speeds = [0, 0, 0, 0, 0, 0]

interval = 0.002
speed = 3
divisor = 30
                        # Digital inputs
movements = {"BTN_TL":   "speeds[5] = -speed if state else 0",
             "ABS_BRAKE":"speeds[5] =  speed if state else 0",
             "BTN_TR":   "speeds[2] = -speed if state else 0",
             "ABS_GAS":  "speeds[2] =  speed if state else 0",
                        # Analog inputs
             "ABS_X":    "speeds[3] = (state - 128)/divisor",
             "ABS_Y":    "speeds[4] = (128 - state)/divisor",
             "ABS_Z":    "speeds[0] = (state - 128)/divisor",
             "ABS_RZ":   "speeds[1] = (128 - state)/divisor"}

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

        for i in xrange(6):
            if 0 < pos[i] + speeds[i] < limits[i]:
                pos[i] += speeds[i]
            try:
                pwm.set_pwm(motors[i], 0, start[i] + int(round(pos[i])))
            except IOError:
                print "IO Error occurred, continuing..."
                continue
        print map(int, pos)
        #print speeds
        sleep(interval)
except KeyboardInterrupt:
    #inpThread1.exit()
    #inpThread2.exit()
    pwm = Adafruit_PCA9685.PCA9685()
    writer()
    print "Program stopping"

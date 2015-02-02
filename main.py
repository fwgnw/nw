import RPi.GPIO as GPIO
import time
import math
from datetime import datetime


MULTIPLIER = 17150
WAITTIME = 0.0
MAX_DIFFERENCE = 20

TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [0, 0, 0, 0]
DATA = [[], [], [], []]  #0: front, 1: left, 2: back, 3: right
WDATA = [[0, 0], [0, 0], [0, 0], [0, 0]]

MOTOR = [29, 31, 32, 33]  #0: engine+, 1: engine-, 2: steering+, 3: steering-

LOGFILE = "log/main_" + str(int(time.time())) + ".log"

drivingForward = False
drivingBackward = False

measurements = 0
successful_measurements = [0, 0, 0, 0]

timeOfLastMeasurement = 0
velocity = 0


def setup():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)

    for motor in MOTOR:
        GPIO.setup(motor, GPIO.OUT)
        GPIO.output(motor, False)


def measure(i):
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    msr_start = time.time()

    pulse_start = -1
    pulse_end = 0

    while GPIO.input(ECHO[i]) == 0:
        pulse_start = time.time()
        if time.time() - msr_start > 0.025:
            break

    while GPIO.input(ECHO[i]) == 1:
        pulse_end = time.time()
        if time.time() - msr_start > 0.025:
            break

    if time.time() - msr_start > 0.025:
        RESULT[i] = 1
    else:
        RESULT[i] = pulse_end - pulse_start

    time.sleep(WAITTIME)


def print_result(i):
    distance = RESULT[i] * MULTIPLIER
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


def clear_wdata(i):
    for n in range(len(WDATA[i])):
        WDATA[i][n] = 0


def save_result(i, file):
    DATA[i].append(RESULT[i])
    #file.write(str(round(RESULT[i] * MULTIPLIER, 2)) + "\n")
    clear_wdata(i)
    successful_measurements[i] += 1
    print_result(i)


def check_results():
    global timeOfLastMeasurement, velocity
    with open(LOGFILE, "a+") as file:
        for i in range(len(RESULT)):
            if len(DATA[i]) >= 1 and RESULT[i] > 0:
                n = DATA[i][len(DATA[i]) - 1]

                if math.fabs(RESULT[i] - n) > timeFromDistance(MAX_DIFFERENCE):
                    if WDATA[i][0] == 0:
                        WDATA[i][0] = n
                    elif WDATA[i][1] == 0:
                        WDATA[i][1] = n
                    else:
                        if math.fabs(n - WDATA[i][0]) < timeFromDistance(MAX_DIFFERENCE):
                            if math.fabs(n - WDATA[i][1]) < timeFromDistance(MAX_DIFFERENCE):
                                save_result(i, file)
                            else:
                                clear_wdata(i)
                        else:
                            clear_wdata(i)
                else:
                    save_result(i, file)

                if len(DATA[i]) >= 2:
                    velocity = ((MULTIPLIER * DATA[i][len(DATA[i]) - 2] - MULTIPLIER * DATA[i][len(DATA[i]) - 1]) / float(100)) / float(time.time() - timeOfLastMeasurement)
                    print(str(MULTIPLIER * DATA[i][len(DATA[i]) - 1]) + " cm - " + str(MULTIPLIER * DATA[i][len(DATA[i]) - 2]) + " cm")
                    print(str((MULTIPLIER * DATA[i][len(DATA[i]) - 1] - MULTIPLIER * DATA[i][len(DATA[i]) - 2]) / float(100)) + " m / " + str(float(time.time() - timeOfLastMeasurement)) + " s")
                    print(str(velocity))

                timeOfLastMeasurement = time.time()
            elif RESULT[i] > 0:
                save_result(i, file)
                #file.write("\n")


def timeFromDistance(distance):
    return distance / float(MULTIPLIER)


def driveForward():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], True)
    drivingForward = True
    GPIO.output(MOTOR[1], False)
    drivingBackward = False

def driveBackward():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], False)
    drivingForward = False
    GPIO.output(MOTOR[1], True)
    drivingBackward = True

def stopdrive():
    global drivingForward
    global drivingBackward
    GPIO.output(MOTOR[0], False)
    drivingForward = False
    GPIO.output(MOTOR[1], False)
    drivingBackward = False

def steerLeft():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], True)

def steerRight():
    GPIO.output(MOTOR[2], True)
    GPIO.output(MOTOR[3], False)

def stopsteer():
    GPIO.output(MOTOR[2], False)
    GPIO.output(MOTOR[3], False)

def brake():
    BRAKETIME = 0.15
    if drivingForward:
        print("driving BACKWARD")
        driveBackward()
        time.sleep(BRAKETIME)
    elif drivingBackward:
        print("driving FORWARD")
        driveForward()
        time.sleep(BRAKETIME)
    stopdrive()

def turn(a):
    angle = (a) / float(180) * 3.141592653
    #radius = 61
    radius = 105
    line = (radius * angle) / float(100)

    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] velocity: " + str(velocity) + " m/s\n")
    #if velocity != 0:
        #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] time for turn: " + str(line / float(velocity)) + " s\n")
    #else :
        #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] time for turn: ERROR velocity=0\n")

    if velocity > 0:
        steerLeft()
        #time.sleep(0.5)
        print(str(line / float(velocity)) + " s")
        time.sleep(line / float(velocity))
        stopsteer()


def drive1():
    driveForward()
    measure(0)
    check_results()
    while RESULT[0] > timeFromDistance(64):  #while distance is larger than 64 cm
        measure(0)
        check_results()
    brake()


def drive2():
    driveForward()
    start = time.time()
    measure(0)
    check_results()
    while (time.time() - start) < 1:  #while distance is larger than 1m
        measure(0)
        check_results()
    turn()
    stopdrive()


def drive3():
    angle = int(input())
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] START DRIVING...\n")
    driveForward()
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] START MEASURING FRONT...\n")
    measure(0)
    check_results()
    while RESULT[0] > timeFromDistance(150):  #while distance is larger than 64 cm
        measure(0)
        check_results()
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] STOP MEASURING FRONT...\n")
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] MAKE TURN...\n")
    turn(angle)
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] FINISHED TURN...\n")
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] START MEASURING FRONT...\n")
    measure(0)
    check_results()
    while RESULT[0] > timeFromDistance(64):  #while distance is larger than 64 cm
        measure(0)
        check_results()
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] STOP MEASURING FRONT...\n")
    #open(LOGFILE, "a+").write("[" + str(datetime.now().time()) + "] BRAKING...\n")
    brake()


setup()

for i in range(8):
    print(8 - i)
    time.sleep(1)

drive3()

import RPi.GPIO as GPIO
import time
import math


MULTIPLIER = 17150
WAITTIME = 0.125

TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [0, 0, 0, 0]
DATA = [[], [], [], []]
WDATA = [[0, 0], [0, 0], [0, 0], [0, 0]]

M_IN = [29, 32]   #0: engine, 1: steering
M_OUT = [31, 33]  #0: engine, 1: steering

LOGFILE = "log/" + str(int(time.time())) + ".log"

measurements = 0
successful_measurements = [0, 0, 0, 0]


def setup():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)

    for min in M_IN:
        GPIO.setup(min, GPIO.IN)

    for mout in M_OUT:
        GPIO.setup(mout, GPIO.OUT)
        GPIO.output(mout, False)


def measure(i):
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    msr_start = time.time()

    pulse_start = -1
    pulse_end = 0

    while GPIO.input(ECHO[i]) == 0:
        pulse_start = time.time()
        if time.time() - msr_start > 0.05:
            break

    while GPIO.input(ECHO[i]) == 1:
        pulse_end = time.time()
        if time.time() - msr_start > 0.05:
            break

    if time.time() - msr_start > 0.05:
        RESULT[i] = -1
    else:
        RESULT[i] = pulse_end - pulse_start
<<<<<<< HEAD

    time.sleep(.25)
=======

    time.sleep(WAITTIME)
>>>>>>> 5a90837f53005b9cda5a07a5ac7977d0fac5c868


def print_result(i):
    distance = RESULT[i] * MULTIPLIER
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


def clear_wdata(i):
    for n in range(len(WDATA[i])):
        WDATA[i][n] = 0


def save_result(i, file):
    DATA[i].append(RESULT[i])
    file.write(str(round(RESULT[i] * MULTIPLIER, 2)) + "\n")
    clear_wdata(i)
    successful_measurements[i] += 1
    print_result(i)


def check_results():
    with open(LOGFILE, "a+") as file:
        for i in range(len(RESULT)):
	    if len(DATA[i]) >= 1 and RESULT[i] > 0:
                n = DATA[i][len(DATA[i]) - 1]

		if math.fabs(RESULT[i] - n) > math.fabs(n) / 100.0 * 10:
		    if WDATA[i][0] == 0:
                        WDATA[i][0] = n
                    elif WDATA[i][1] == 0:
                        WDATA[i][1] = n
                    else:
                        if math.fabs(n - WDATA[i][0]) < math.fabs(WDATA[i][0]) / 100.0 * 10:
                            if math.fabs(n - WDATA[i][1]) < math.fabs(WDATA[i][1]) / 100.0 * 10:
                                save_result(i, file)
                            else:
                                clear_wdata(i)
                        else:
                            clear_wdata(i)
		else:
		    save_result(i, file)
	    elif RESULT[i] > 0:
		save_result(i, file)
        file.write("\n")


def drive():
    GPIO.output(M_OUT[0], True)
    wait(1)
    GPIO.output(M_OUT[0], False)

'''
MULTIPLIER = int(input("M = "))

setup()

for glhf in range(100):
    prgrm_start = time.time()

    for i in range(len(TRIG)):
	measure(i)
    check_results()
    measurements += 1

    prgrm_end = time.time()
    print("duration = " + str(round(prgrm_end - prgrm_start, 2)) + " s")

GPIO.cleanup()

print(measurements)
print("0: " + str(round(successful_measurements[0] / float(measurements) * 100, 2)))
print("1: " + str(round(successful_measurements[1] / float(measurements) * 100, 2)))
print("2: " + str(round(successful_measurements[2] / float(measurements) * 100, 2)))
print("3: " + str(round(successful_measurements[3] / float(measurements) * 100, 2)))
'''

setup()

drive()

GPIO.cleanup()

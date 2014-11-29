import RPi.GPIO as GPIO
import time


TRIG = [16, 38, 35, 13]
ECHO = [18, 36, 37, 11]
RESULT = [0, 0, 0, 0]
    

def setup():
    GPIO.cleanup()

    GPIO.setmode(GPIO.BOARD)

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)


def measure(i):
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    msr_start = time.time()

    while GPIO.input(ECHO[i]) == 0 and time.time() - msr_start < 0.05:
        pulse_start = time.time()

    while GPIO.input(ECHO[i]) == 1 and time.time() - msr_start < 0.05:
        pulse_end = time.time()

    if time.time() - msr_start > 0.05:
        RESULT[i] = -1
    else:
        RESULT[i] = pulse_end - pulse_start
    
    time.sleep(.25)


def print_result(i):
    distance = RESULT[i] * 17150
    distance = round(distance, 2)

    print("distance[" + str(i) + "] = " + str(distance) + " cm")


setup()

while True:
    prgrm_start = time.time()

    for i in range(len(TRIG)):
        measure(i)
        print_result(i)
        
    prgrm_end = time.time()
    print("duration = " + str(round(prgrm_end - prgrm_start, 2)) + " s")

GPIO.cleanup()

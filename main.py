import RPi.GPIO as GPIO
import time

def setup():
    GPIO.cleanup()

    GPIO.setmode(GPIO.BOARD)

    TRIG = [16, 38, 35, 13]
    ECHO = [18, 36, 37, 11]
    RESULT = [0, 0, 0, 0]

    for trig in TRIG:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.output(trig, False)

    for echo in ECHO:
        GPIO.setup(echo, GPIO.IN)


def measure(i)
    GPIO.output(TRIG[i], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[i], False)

    while GPIO.input(ECHO[i]) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO[i]) == 1:
        pulse_end = time.time()

    RESULT[i] = pulse_end - pulse_start


def print_result(i):
    distance = RESULT[i] * 17150
    distance = round(distance, 2)

    print("distance = " + str(distance) + "cm")


setup()

while True:
    start_prgrm = time.time()

    # time.sleep(.5)

    for i in range(len(TRIG)):
        measure(i)
        print_result(i)
        
    end_prgrm = time.time()
    print("duration = " + str(round(end_prgrm - start_prgrm, 2)))

GPIO.cleanup()

import RPi.GPIO as GPIO
import time
import cv2 as cv
import numpy as np
import math

def get_rgb_from_ref(ref):
    rgb_list = []
    ref = cv.imread(ref)
    for i in range(len(ref)):
        for j in range(len(ref[i])):
            rgb_list.append([ref[i][j][0], ref[i][j][1], ref[i][j][2]])
    return rgb_list


def show_col_num(ref, col_count=5):
    with open('/home/pi/cardstunt/motor.csv', 'r') as f:
        col_out_list = f.read().splitlines()

        # convert list element from str to int
        for i in range(len(col_out_list)):
            col_out_list[i] = int(col_out_list[i])

        col_show_list = []
        for i in col_out_list:
            if i not in col_show_list:
                col_show_list.append(i)

        col_show_list = col_show_list[:col_count]

        rgb_ref_list = get_rgb_from_ref(ref)
        rgb_show_list = []
        for i in col_show_list:
            rgb_show_list.append(rgb_ref_list[i])

        show_pic = np.zeros((50, 50, 3), dtype=np.uint8)
        show_pic[:] = rgb_show_list[0]
        show_pic = cv.putText(show_pic, str(col_show_list[0]), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        for i in range(1, col_count):
            for j in range(len(rgb_show_list[i])):
                rgb_show_list[i][j] = int(rgb_show_list[i][j])
            show_pic = cv.copyMakeBorder(show_pic, 0, 0, 0, 50, cv.BORDER_CONSTANT, value=rgb_show_list[i])
            show_pic = cv.putText(show_pic, str(col_show_list[i]), (10 + (50 * i), 40), cv.FONT_HERSHEY_SIMPLEX, 0.75,
                                  (255, 255, 255), 2)

        return [show_pic, col_show_list]

def set_color(out_list):
    print("Set Color")
        
    for i in out_list[1]:
        print("Here's " + str(i))
        for j in range(i):
            servo1.ChangeDutyCycle(2)
            time.sleep(0.03)
            servo1.ChangeDutyCycle(4)
            time.sleep(0.07)
            servo1.ChangeDutyCycle(0)
            time.sleep(0.03)
            print(j+1)

    time.sleep(2)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.05)
    servo1.ChangeDutyCycle(0)
    print("Set Successfully")

def flip():
    for i in range(3, 0, -1):
        print("Flip in " + str(i))
        time.sleep(1)
    servo1.ChangeDutyCycle(12)
    time.sleep(1)
    servo1.ChangeDutyCycle(0)
    time.sleep(0.15)
    print("Flipp Successfully")

    unflip = input("unflip?: ")
    if unflip == 'y':
        servo1.ChangeDutyCycle(2)
        time.sleep(1)
        servo1.ChangeDutyCycle(0)
        time.sleep(0.15)
    
    print("Unflip Successfully")
    
def reset(out_list):
    print("Reset Color")
        
    for i in out_list[1]:
        print("Reset " + str(i))
        for j in range(64 - i):
            servo1.ChangeDutyCycle(2)
            time.sleep(0.03)
            servo1.ChangeDutyCycle(4)
            time.sleep(0.07)
            servo1.ChangeDutyCycle(0)
            time.sleep(0.03)
            print(i + j + 1)

    time.sleep(2)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.05)
    servo1.ChangeDutyCycle(0)
    print("Reset Successfully")

# action

# motor setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo1 = GPIO.PWM(11,50) # 11 is pin / 50 is 50Hz Pulse

# motor start
servo1.start(0)
print("wait 2 seconds for start")
time.sleep(2)

ref = "/home/pi/cardstunt/color ref.png"
out_list = show_col_num(ref)
cv.imshow('color number', out_list[0])
cv.waitKey(0)

set_color(out_list)
flip()
reset(out_list)

servo1.stop()
GPIO.cleanup()
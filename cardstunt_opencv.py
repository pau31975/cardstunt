from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import cv2 as cv
import numpy as np
import math

# motor setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo1 = GPIO.PWM(11,50) # 11 is pin / 50 is 50Hz Pulse

# take picture
def capture_photo():
    # action
    take_picture()
    ref = cv.imread("/home/pi/cardstunt/color ref.png") # read color reference image
    img = cv.imread("/home/pi/cardstunt/test.jpg") # read image / in case want to input file --> change filename here
    result = resizeToWideScrn(img, ref, (105, 185), cv.BORDER_CONSTANT, [0, 0, 0]) # resize & recolor
    cv.imwrite("/home/pi/cardstunt/result.jpg", result) # write output to file result.jpg
    to_motor(result, ref) # save the csv
    print('ready to show')

# set the color & flip
def show():
    # motor start
    servo1.start(0)
    print("wait 2 seconds for start")
    time.sleep(2)

    ref = cv.imread("/home/pi/cardstunt/color ref.png")
    out_list = show_col_num(ref)
    cv.imshow('color number', out_list[0])
    cv.waitKey(0)

    set_color(out_list)
    flip()

# unflip and reset the color
def unshow():
    # motor start
    servo1.start(0)
    print("wait 2 seconds for start")
    time.sleep(2)

    ref = cv.imread("/home/pi/cardstunt/color ref.png")
    out_list = show_col_num(ref)
    unflip()
    reset(out_list)


# resize the input image & recolor the image to target color reference
def resizeToWideScrn(img, col_ref, size, bdType, bgCol):
    h, w = img.shape[:2]
    th, tw = size
    a = w / h
    ta = tw / th

    # interpolation method
    if h > th or w > tw:  # shrinking image
        interpol = cv.INTER_AREA
    else:  # stretching image
        interpol = cv.INTER_CUBIC

    # resizing and padding
    if a < ta:  # fit to height
        acW = round(th * a)
        resized = cv.resize(img, (acW, th), interpolation=interpol)
        resized = re_color(resized, col_ref)
        resized = cv.copyMakeBorder(resized, 0, 0, (tw - acW) // 2, tw - acW - (tw - acW) // 2, bdType,
                                    value=bgCol)
    else:  # fit to width
        acH = round(tw / a)
        resized = cv.resize(img, (tw, acH), interpolation=interpol)
        resized = re_color(resized, col_ref)
        resized = cv.copyMakeBorder(resized, (th - acH) // 2, th - acH - (th - acH) // 2, 0, 0, bdType,
                                    value=bgCol)

    return resized

# get rgb values from color reference image
def get_rgb_from_ref(ref):
    rgb_list = []
    for i in range(len(ref)):
        for j in range(len(ref[i])):
            rgb_list.append([ref[i][j][0], ref[i][j][1], ref[i][j][2]])
    return rgb_list

# recolor the image to target color reference
def re_color(img, ref, inc_vib=True):
    ref = get_rgb_from_ref(ref)
    if inc_vib == True:
        img = inc_vibrance(img)
    for i in range(len(img)):
        for j in range(len(img[i])):

            # rgb 3d closest distance
            dist = []
            for k in ref:
                for a in range(len(k)): k[a] = int(k[a])
                for b in range(len(img[i][j])): img[i][j][b] = int(img[i][j][b])
                dist.append(math.sqrt((k[0]-img[i][j][0])**2+(k[1]-img[i][j][1])**2+(k[2]-img[i][j][2])**2))
            col_dist_min = ref[dist.index(min(dist))]
            img[i][j] = col_dist_min

    return img

# increase the image vibrance to prevent image going gray
def inc_vibrance(img, grey_floor=51, mid=70, new_mid=100, ceil=120):
    img = cv.cvtColor(img, cv.COLOR_RGB2HSV)

    for i in range(len(img)):
        for j in range(len(img[i])):
            if img[i][j][1] >= grey_floor and img[i][j][1] <= ceil:
                if img[i][j][1] <= mid:
                    slope = (new_mid - mid) // (mid - grey_floor)
                    img[i][j][1] += slope*(img[i][j][1] - grey_floor)
                else:
                    slope = - (new_mid - mid) // (ceil - mid)
                    img[i][j][1] += slope*(img[i][j][1] - ceil)

    img = cv.cvtColor(img, cv.COLOR_HSV2RGB)

    return img

# take picture from pi's camera
def take_picture():
    camera = PiCamera()
    camera.resolution = (640, 360)
    camera.rotation = 180
    time.sleep(2)
    camera.capture("/home/pi/cardstunt/test.jpg")
    print("done.")

# save each pixel as csv of number of times motor needs to flip
def to_motor(result, ref):
    motor_flip_mat = np.zeros((105, 185), dtype=int)
    for i in range(len(result)):
        for j in range(len(result[i])):
            motor_flip_mat[i][j] = int(get_rgb_from_ref(ref).index(list(result[i][j])))

    with open('/home/pi/cardstunt/motor.csv','wb') as f:
        for line in motor_flip_mat:
            np.savetxt(f, line, fmt='%.0f')

# show five color & their numbers for simulation
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
        show_pic = cv.putText(show_pic, str(col_show_list[0]), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255),
                              2)
        for i in range(1, col_count):
            for j in range(len(rgb_show_list[i])):
                rgb_show_list[i][j] = int(rgb_show_list[i][j])
            show_pic = cv.copyMakeBorder(show_pic, 0, 0, 0, 50, cv.BORDER_CONSTANT, value=rgb_show_list[i])
            show_pic = cv.putText(show_pic, str(col_show_list[i]), (10 + (50 * i), 40), cv.FONT_HERSHEY_SIMPLEX, 0.75,
                                  (255, 255, 255), 2)

        return [show_pic, col_show_list]


# set the card
def set_color(out_list):
    print("Set Color")

    for i in out_list[1]:
        print("Here's " + str(i))
        for j in range(i):
            servo1.ChangeDutyCycle(2)
            time.sleep(0.15)
            servo1.ChangeDutyCycle(4)
            time.sleep(0.35)
            servo1.ChangeDutyCycle(0)
            time.sleep(0.15)
            print(j + 1)

    time.sleep(2)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.05)
    servo1.ChangeDutyCycle(0)
    print("Set Successfully")


# flip to show final image to the audience
def flip():
    for i in range(3, 0, -1):
        print("Flip in " + str(i))
        time.sleep(1)
    servo1.ChangeDutyCycle(12)
    time.sleep(1)
    servo1.ChangeDutyCycle(0)
    time.sleep(0.15)
    print("Flip Successfully")

# unflip to close the image from the audience
def unflip():
    servo1.ChangeDutyCycle(2)
    time.sleep(1)
    servo1.ChangeDutyCycle(0)
    time.sleep(0.15)
    print("Unflip Successfully")


# reset each card to the color number 0
def reset(out_list):
    print("Reset Color")

    for i in out_list[1]:
        print("Reset " + str(i))
        for j in range(64 - i):
            servo1.ChangeDutyCycle(2)
            time.sleep(0.15)
            servo1.ChangeDutyCycle(4)
            time.sleep(0.35)
            servo1.ChangeDutyCycle(0)
            time.sleep(0.15)
            print(i + j + 1)

    time.sleep(2)
    servo1.ChangeDutyCycle(2)
    time.sleep(0.05)
    servo1.ChangeDutyCycle(0)
    print("Reset Successfully")
from picamera import PiCamera
import time
import cv2 as cv
import numpy as np
import math

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

def get_rgb_from_ref(ref):
    rgb_list = []
    for i in range(len(ref)):
        for j in range(len(ref[i])):
            rgb_list.append([ref[i][j][0], ref[i][j][1], ref[i][j][2]])
    return rgb_list


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

def take_picture():
    camera = PiCamera()
    camera.resolution = (640, 360)
    camera.rotation = 180
    time.sleep(2)
    camera.capture("/home/pi/cardstunt/test.jpg")
    print("done.")
    
def to_motor(result):
    motor_flip_mat = np.zeros((105, 185), dtype=int)
    for i in range(len(result)):
        for j in range(len(result[i])):
            motor_flip_mat[i][j] = int(get_rgb_from_ref(ref).index(list(result[i][j])))

    with open('/home/pi/cardstunt/motor.csv','wb') as f:
        for line in motor_flip_mat:
            np.savetxt(f, line, fmt='%.0f')

# action
take_picture()

ref = cv.imread("/home/pi/cardstunt/color ref.png")

img = cv.imread("/home/pi/cardstunt/test.jpg") # in case want to input file --> change filename here

result = resizeToWideScrn(img, ref, (105, 185), cv.BORDER_CONSTANT, [0, 0, 0])

cv.imwrite("/home/pi/cardstunt/result.jpg", result)

to_motor(result)

cv.imshow("result", result)
cv.waitKey(0)

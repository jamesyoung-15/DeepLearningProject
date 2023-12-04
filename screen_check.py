import cv2
import numpy

import mss
import time
import subprocess


with mss.mss() as sct:
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
    resolution = output.split()[0].split(b'x')
    res = {'width': resolution[0].decode("utf-8"), 'height': resolution[1].decode("utf-8")}
    print(res)
    screen_info = res
    screen_width = int(screen_info['width'])
    screen_height = int(screen_info['height'])
    center_x = int(screen_width / 2) - 320
    center_y = int(screen_height / 2) - 240 + 20
    print(center_x, center_y)
    # Part of the screen to capture
    monitor = {"top": center_y, "left": center_x, "width": 640, "height": 480}

    while "Screen capturing":
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        img = numpy.array(sct.grab(monitor))

        # Display the picture
        cv2.imshow("OpenCV/Numpy normal", img)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        print(f"fps: {1 / (time.time() - last_time)}")

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break


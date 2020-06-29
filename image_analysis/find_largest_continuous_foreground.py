from skimage.metrics import structural_similarity as ssim

import argparse
import imutils
import cv2

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


def find_diff(image_orig, image_mod):
    gray_orig = cv2.cvtColor(image_orig, cv2.COLOR_BGR2GRAY)
    gray_mod = cv2.cvtColor(image_mod, cv2.COLOR_BGR2GRAY)
    (score, diff) = ssim(gray_orig, gray_mod, full=True)
    diff = (diff * 255).astype("uint8")
    roi = find_roi(diff, gray_mod)

    return roi, diff


def find_roi(diff, gray_mod):
    thresh = cv2.threshold(diff, 0, 25,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)

    max_area = index = -1
    for i, c in enumerate(cnts):
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ

        (x, y, w, h) = cv2.boundingRect(c)
        area = w * h
        if area > max_area:
            max_area = area
            index = i
    (x, y, w, h) = cv2.boundingRect(cnts[index])
    roi = gray_mod[x:x + w, y:y + h]
    return [x, y, x+w, y+h]



if __name__ == "__main__":
    image_orig = cv2.imread(r"../image_manipulation/img/mtn_dew.png")
    image_mod = cv2.imread(r"../image_manipulation/img/mtn_dew_tweaked.png")
    roi, diff = find_diff(image_orig, image_mod)

    img_diff = image_mod[roi[0]: roi[2], roi[1]: roi[3]]
    cv2.imshow("largest continuous foreground", img_diff)
    cv2.waitKey(0)

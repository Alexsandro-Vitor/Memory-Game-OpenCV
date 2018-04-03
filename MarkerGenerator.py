import numpy as np
import cv2
import cv2.aruco as aruco
import sys

markerId = 0
if len(sys.argv) > 1:
	markerId = int(sys.argv[1])

dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
img = aruco.drawMarker(dictionary, markerId, 200)

cv2.imshow("Marker " + str(markerId), img)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("Marker " + str(markerId) + ".jpg", img)
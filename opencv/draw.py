import cv2 as cv
import numpy as np

# Create a blank 3-channel image (BGR)
blank = np.zeros((500, 500, 3), dtype='uint8')
# cv.imshow("Blank", blank)

# Fill with green (BGR format)
blank[:] = 0, 255, 0
cv.imshow("Green", blank)

cv.waitKey(0)
cv.destroyAllWindows()
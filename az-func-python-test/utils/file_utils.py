import base64
import numpy as np
import cv2

# read base64 code and convert to image
def readb64(uri):
    encoded_data = uri 
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

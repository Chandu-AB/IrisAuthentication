from cryptosteganography import CryptoSteganography
from Daugman import find_iris
import cv2

def watermarkImage(image):
    img = cv2.imread(image)
    img = cv2.resize(img,(128,128), interpolation=cv2.INTER_CUBIC)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    answer = find_iris(gray_img, daugman_start=10, daugman_end=30, daugman_step=1, points_step=3)
    iris_center, iris_rad = answer
    start = iris_center[0]
    end = iris_center[1]
    radius = iris_rad
    result = img[start-radius:start+radius,end-radius:end+radius]
    result = cv2.resize(result, (64,64), interpolation=cv2.INTER_CUBIC)
    segmented = result
    print(str(start)+" "+str(end))
    cv2.imwrite("segment.png", segmented)

watermarkImage('IrisAuthApp/static/images/tra.jpg')

crypto_steganography = CryptoSteganography('securehiding')
message = 'welcome to java world hello'
crypto_steganography.hide("segment.png", 'output_stego_image.png', message)

crypto_steganography = CryptoSteganography('securehiding')
secret = crypto_steganography.retrieve('output_stego_image.png')
print("welcome "+secret)

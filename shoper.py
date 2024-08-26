from sys import argv
import cv2

class ShopBill:

    def __init__(self):

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)

        self.convertTograyImage(self.image)

    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
    ShopBill()
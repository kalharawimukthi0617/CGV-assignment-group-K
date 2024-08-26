from sys import argv
import cv2

class ShopBill:

    def __init__(self):

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)


if __name__ == "__main__":
    ShopBill()
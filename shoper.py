from sys import argv
import cv2

class ShopBill:

    def __init__(self):

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)

        self.convertTograyImage(self.image)
        self.increaseContrast(self.gray_image) 

        #show the grey image
        cv2.imshow('Processed Image', self.gray_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def increaseContrast(self, img):
        self.contrast_image = cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, -50)

if __name__ == "__main__":
    ShopBill()
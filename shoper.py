from sys import argv
import cv2
import numpy as np 
import matplotlib.pyplot as plt


class ShopBill:

    def __init__(self):

        #Images
        self.image = None
        self.gray_image = None
        self.contrast_image = None
        self.clahe_image = None

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)
        
        self.processingImage() 
        self.showImages()

    def processingImage(self):
        self.convertTograyImage(self.image)
        self.getDeNoisedImage(self.gray_image)
        self.increaseContrast(self.denoised_image) 
        self.applySharpening(self.contrast_image)
        self.applyCLAHE(self.sharpened_image)
        self.applyOpening(self.applyCLAHE)


    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Function to remove noise from a image
    def getDeNoisedImage(self, img):
        #self.denoised_image = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
        self.denoised_image  = cv2.GaussianBlur(img, (5, 5), 0)

    def increaseContrast(self, img):
        self.contrast_image = cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, -50)

    # Created a function to sharpen the image
    def applySharpening(self, img):
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        self.sharpened_image = cv2.filter2D(img, -1, kernel)
        
    def applyCLAHE(self, img):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        self.clahe_image = clahe.apply(img)

    #create a function to appllying opend image processing techniques for the final image
    def applyOpening(self, img):
        kernel = np.ones((2,2), np.uint8)  
        self.opened_image = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    # Function to show all the images that used image processing concepts
    def showImages(self):
        plt.figure(figsize=(20, 10))
        images = [self.image, self.gray_image, self.denoised_image, 
                  self.contrast_image,self.sharpened_image, self.clahe_image]
        
        titles = ['Original', 'Grayscale', 'Denoised', 'Contrast Enhanced','Sharpen', 'CLAHE']
        
        for i in range(len(images)):
            plt.subplot(2, 3, i+1)
            plt.title(titles[i])
            if len(images[i].shape) == 3:
                plt.imshow(cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB))
            else:
                plt.imshow(images[i], cmap='gray')
            plt.axis('off')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    ShopBill() 



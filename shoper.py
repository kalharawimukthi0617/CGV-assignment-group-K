from sys import argv
import cv2
import numpy as np 
import matplotlib.pyplot as plt


class ShopBill:

    def __init__(self):

        #Imgages
        self.image = None
        self.gray_image = None
        self.contrast_image = None
        self.clahe_image = None

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)
        
        self.processingImage() 

        #show the images
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 3, 1)
        plt.title('Original Image')
        plt.imshow(self.image)
        plt.axis('off')

        plt.subplot(2, 3, 2)
        plt.title('Grayscale Image')
        plt.imshow(self.gray_image, cmap='gray')  # Add cmap='gray' here
        plt.axis('off')
  
        plt.subplot(2, 3, 3)
        plt.title('Contrast enhanced image')
        plt.imshow(self.contrast_image, cmap='gray')  # Add cmap='gray' here 
        plt.axis('off') 
        
        plt.subplot(2, 3, 4)
        plt.title('CLAHE imgae')
        plt.imshow(self.clahe_image, cmap='gray')  # Add cmap='gray' here 
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()

    def processingImage(self):
        self.convertTograyImage(self.image)
        self.increaseContrast(self.gray_image) 
        self.getDeNoisedImage(self.contrast_image)
        self.applyCLAHE(self.denoised_image)

    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def getDeNoisedImage(self, img):
        #self.denoised_image = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
        self.denoised_image  = cv2.GaussianBlur(img, (5, 5), 0)

    def increaseContrast(self, img):
        self.contrast_image = cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, -50)
        
    def applyCLAHE(self, img):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        self.clahe_image = clahe.apply(img)
        cv2.imwrite("clache.png",self.clahe_image)

if __name__ == "__main__":
    ShopBill() 



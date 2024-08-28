from sys import argv
import cv2
import numpy as np 
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt

class ShopBill:

    def __init__(self):

        #Images
        self.image = None
        self.gray_image = None
        self.contrast_image = None
        self.clahe_image = None

        #text
        self.text = ""

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)
        
        self.processingImage() 
        self.resizeImage()
        self.extract_text()
        self.showTopSection()
        # self.showImages()


    #  ----------------------- image proccessing techniques -----------------------
    def processingImage(self):
        self.convertTograyImage(self.image)
        self.getDeNoisedImage(self.gray_image)
        self.increaseContrast(self.denoised_image) 
        self.applySharpening(self.contrast_image)
        self.applyCLAHE(self.sharpened_image)
        self.applyOpening(self.clahe_image)


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
                  self.contrast_image,self.sharpened_image, self.clahe_image, self.opened_image]
        
        titles = ['Original', 'Grayscale', 'Denoised', 'Contrast Enhanced','Sharpen', 'CLAHE', 'Opened']
        
        for i in range(len(images)):
            plt.subplot(2, 4, i+1)
            plt.title(titles[i])
            if len(images[i].shape) == 3:
                plt.imshow(cv2.cvtColor(images[i], cv2.COLOR_BGR2RGB))
            else:
                plt.imshow(images[i], cmap='gray')
            plt.axis('off')
        
        plt.tight_layout()
        plt.show()

    #  ----------------------- Show Details on the bill  -----------------------
    
    ## Without reduce quality of the image, increase the size
    def resizeImage(self, scale_factor=10, method='lanczos'):

            # Get the current size (using OpenCV, not PIL)
            height, width = self.opened_image.shape[:2]
            
            # Calculate the new size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Resize the image using OpenCV's resize function
            self.resized_img = cv2.resize(self.opened_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
    #Show bill details      
    def extract_text(self):
            self.text = pytesseract.image_to_string(self.resized_img)
            print("Extracted Text:")
            print(self.text)

    #SHow the top section of the details clearly
    def showTopSection(self, num_lines=4):
        #clean the empty lines
        lines = self.text.split('\n')
        non_empty_lines = [line for line in lines if line.strip() != '']
        cleaned_text = '\n'.join(non_empty_lines)
        # end the cleaning empty lines
        
        top_section_lines = cleaned_text.strip().split('\n')
        top_section = top_section_lines[:num_lines]
        max_length = max(len(line.strip()) for line in top_section)
        total_width = max_length + 6
        
        formatted_text = (
            "\n" + "*" * total_width + "\n"
            + "\n".join(line.strip().center(total_width) for line in top_section)
            + "\n" + "*" * total_width + "\n"
        )
        
        print("\nFormatted Top Section:")
        print(formatted_text)
         
        
if __name__ == "__main__":
    ShopBill() 



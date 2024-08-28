from sys import argv
import cv2
import numpy as np 
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import re
import pandas as pd

class ShopBill:

    def __init__(self):

        #Images
        self.image = None
        self.gray_image = None
        self.contrast_image = None
        self.clahe_image = None

        #text
        self.text = ""

        #data frame
        self.df = None

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)
        
        self.processingImage() 
        self.resizeImage()
        self.extract_text()
        self.showTopSection()
        self.showPriceTableDetails()
        self.showImages()


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
        cv2.imwrite("opened.png",self.opened_image)

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
    # def resizeImage(self, scale_factor=10, method='lanczos'):

    #         # Get the current size (using OpenCV, not PIL)
    #         height, width = self.opened_image.shape[:2]
            
    #         # Calculate the new size
    #         new_width = int(width * scale_factor)
    #         new_height = int(height * scale_factor)
            
    #         # Resize the image using OpenCV's resize function
    #         self.resized_img = cv2.resize(self.opened_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
    def resizeImage(self,scale_factor=10, method='lanczos'):
        # Open the image
        with Image.open("opened.png") as img:
            # Get the current size
            width, height = img.size
            
            # Calculate the new size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Choose the resampling filter
            if method == 'bicubic':
                resample_filter = Image.BICUBIC
            elif method == 'lanczos':
                resample_filter = Image.LANCZOS
            else:
                resample_filter = Image.BILINEAR
            
            # Resize the image
            self.resized_img = img.resize((new_width, new_height), resample_filter)

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

    #this function used is used divide price details in to the name, qty, price
    def dividedPriceDetailsIntoThreeParts(self) :
        # Use regex to find patterns matching Name, Qty, and Total
        lines = self.text.split('\n')
        data = []
        for line in lines:
            # Improved regex pattern to capture possible variations in the text
            match = re.match(r"([\w\s]+)\s+(\d+)\s+(\d+\.\d{2})", line.strip())
            if match:
                name = match.group(1).strip()
                qty = int(match.group(2).strip())
                price = float(match.group(3).strip())
                data.append([name, qty, price])
        
        # Create a DataFrame to store the extracted table data
        self.df = pd.DataFrame(data, columns=['Name', 'Qty', 'Price'])

    # details such as name, quantity, and price are displayed in a table
    def showPriceTableDetails(self):
        try:
            # Calculate the maximum lengths for each column
            name_max_len = max(self.df['Name'].apply(len).max(), len('Name'))
            qty_max_len = max(self.df['Qty'].apply(lambda x: len(str(x))).max(), len('Qty'))
            price_max_len = max(self.df['Price'].apply(lambda x: len(f"{x:.2f}")).max(), len('Price'))

            # Create a format string for each row
            row_format = f"| {{:<{name_max_len}}} | {{:>{qty_max_len}}} | {{:>{price_max_len}.2f}} |"

            # Print header
            print("-" * (name_max_len + qty_max_len + price_max_len + 8))
            print(f"| {'Name':<{name_max_len}} | {'Qty':>{qty_max_len}} | {'Price':>{price_max_len}} |")
            print("-" * (name_max_len + qty_max_len + price_max_len + 8))

            # Print each row of the table
            for index, row in self.df.iterrows():
                print(row_format.format(row['Name'], row['Qty'], row['Price']))

            # Print the bottom line
            print("-" * (name_max_len + qty_max_len + price_max_len + 8))
        except Exception as e:
            print("exception is "+ e)
            
        
if __name__ == "__main__":
    ShopBill() 



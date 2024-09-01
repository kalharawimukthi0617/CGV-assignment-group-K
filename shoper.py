from sys import argv
import cv2
import numpy as np 
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import re
import pandas as pd 
from spellchecker import SpellChecker

class ShopBill:

    def __init__(self):

        self.spell = SpellChecker()

        #Images
        self.image = None
        self.gray_image = None
        self.contrast_image = None
        self.clahe_image = None

        #text
        self.text = ""

        #data frame
        # self.df = None

        #load the image
        script, imagePath = argv
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)
        
        self.processingImage() 
        self.processingBillDetails()
        self.showImages()


    #  ----------------------- image proccessing techniques -----------------------
    def processingImage(self):
        self.convertTograyImage(self.image)
        self.getDeNoisedImage(self.gray_image)
        self.increaseContrast(self.denoised_image) 
        self.applySharpening(self.contrast_image)
        self.applyCLAHE(self.sharpened_image)
        self.applyOpening(self.clahe_image)

    def processingBillDetails(self):
        self.resizeImage()
        self.extract_text()
        self.showTopSection()
        self.dividedPriceDetailsIntoThreeParts()
        self.showPriceTableDetails()
        self.showBottomSection() 

    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Function to remove noise from a image
    def getDeNoisedImage(self, img):
        self.denoised_image  = cv2.GaussianBlur(img, (3, 3), 0)

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
        price_width = max_length + 6
        
        formatted_text = (
            "\n" + "*" * price_width + "\n"
            + "\n".join(line.strip().center(price_width) for line in top_section)
            + "\n" + "*" * price_width + "\n"
        )
        
        print("\nFormatted Top Section:")
        print(formatted_text)

    #this function used is used divide price details in to the name, qty, price
    # def dividedPriceDetailsIntoThreeParts(self) :
    #     # Use regex to find patterns matching Name, Qty, and price
    #     lines = self.text.split('\n')
    #     data = []
    #     for line in lines:
    #         # Improved regex pattern to capture possible variations in the text
    #         match = re.match(r"([\w\s]+)\s+(\d+)\s+(\d+\.\d{2})", line.strip())
    #         if match:
    #             name = match.group(1).strip()
    #             qty = int(match.group(2).strip())
    #             price = float(match.group(3).strip())
    #             data.append([name, qty, price])
        
    #     # Create a DataFrame to store the extracted table data
    #     self.df = pd.DataFrame(data, columns=['Name', 'Qty', 'Price'])

    def dividedPriceDetailsIntoThreeParts(self) :        
        lines = self.text.split('\n')
        table_data = []
        
        #divided price table to the name, qty, price
        pattern = re.compile(r"([a-zA-Z\s]+)[\s’}]*([J\dP]?)\s*([\dA-Za-z]+[.,][0G]{2})")

        for line in lines:

            if "Sub price" in line :
                break

            match = pattern.match(line)
            if match:
                name, qty, price = match.groups()
                del price
                price = line.split()[len(line.split())-1]

                if qty == "" :
                    words = name.split()
                    qty = words[len(words)-1]
                    # Remove the last word
                    words.pop()
                    name =  ' '.join(words)

                name = self.correctSpelling(name)
                qty = self.correctQty(qty)
                price = self.correctPrice(price)
                table_data.append([name.strip(), qty, float(price)])

        self.df = pd.DataFrame(table_data, columns=['Name', 'Qty', 'Price'])
 

    # details such as name, quantity, and price are displayed in a table
    def showPriceTableDetails(self):
        try:
            # Calculate the maximum lengths for each column
            name_max_len = max(self.df['Name'].apply(len).max(), len('Name'))
            qty_max_len = max(self.df['Qty'].apply(lambda x: len(str(x))).max(), len('Qty'))
            price_max_len = max(self.df['Price'].apply(lambda x: len(f"{x:.2f}")).max(), len('Price'))
            row_format = f"| {{:<{name_max_len}}} | {{:>{qty_max_len}}} | {{:>{price_max_len}.2f}} |"
            print("+"+"-" * (name_max_len + qty_max_len + price_max_len + 8)+"+")
            print(f"| {'Name':<{name_max_len}} | {'Qty':>{qty_max_len}} | {'Price':>{price_max_len}} |")
            print("+"+"-" * (name_max_len + qty_max_len + price_max_len + 8)+"+")
            for index, row in self.df.iterrows():
                print(row_format.format(row['Name'], row['Qty'], row['Price']))
            print("+"+"-" * (name_max_len + qty_max_len + price_max_len + 8)+"+")
        except Exception as e:
            print("Exception is " + str(e))

    def showBottomSection(self):
        bottom_section = re.findall(r"(Sub price|Cash|Change)\s*[\$:]?\s*(\d+[.,]\d{2})", self.text, re.IGNORECASE)
        if bottom_section:
            print("\n" + "=" * 40)
            print("{:^40}".format("Receipt Summary"))
            print("=" * 40)
            
            max_label_length = max(len(item[0]) for item in bottom_section)
            for item in bottom_section:
                label = item[0].ljust(max_label_length)
                value = self.correctPrice(item[1])
                print(f"  {label:<15} : {float(value):>10.2f}")
            
            print("=" * 40)
            print("{:^40}".format("Thank You! Please Come Again"))
            print("=" * 40)
        else:
            print("Bottom section not found.")

    # Function to correct spellings in receipts
    def correctSpelling(self, text):
        words = text.split()
        corrected_words = [self.spell.correction(word) or word for word in words]
        return ' '.join(corrected_words)

    # Function to correct quantities of the products
    def correctQty(self, text):
        qty_map = {'}': '1', 'J': '1', 'j': '1', 'P': '2', 'p': '2'}
        return qty_map.get(text, text)
    
    # Function to correct price of products
    def correctPrice(self, text):
        # Replace comma with dot for decimal point
        corrected = text.replace(',', '.')
        # Replace common OCR errors
        corrected = corrected.replace('G', '0').replace('B', '8').replace('boor','beer')
        return corrected
    
if __name__ == "__main__":
    ShopBill() 



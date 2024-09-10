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
        self.df = None

        #load the image
        script, imagePath = argv

        self.loadImage(imagePath)
        self.processingImage() 
        self.processingBillDetails()
        self.showImages()

    #  ----------------------- image proccessing techniques -----------------------
    def loadImage(self,imagePath) :
        self.imagePath = imagePath
        self.image = cv2.imread(imagePath)

    def processingImage(self):
        self.convertTograyImage(self.image)
        self.applyGamma(self.gray_image)
        self.convertToDeBlur(self.gamma_image)
        self.getDeNoisedImage(self.deblur_image)
        self.increaseContrast(self.denoised_image) 
        self.applySharpening(self.contrast_image)

    def processingBillDetails(self):
        self.resizeImage()
        self.extractText()
        self.showTopSection()
        self.dividedPriceDetailsIntoThreeParts()
        self.showPriceTableDetails()
        self.showBottomSection() 

    #Gamma correction adjusts the overall brightness of the image, which can help in bringing out details in darker or lighter areas of the image.
    #which can improve the contrast and make text more visible
    def applyGamma(self, img, gamma=1.0):
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        self.gamma_image = cv2.LUT(img, table)

    def convertTograyImage(self, img):
        self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #This function use to removing blur from the image
    def convertToDeBlur(self,image):
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])  # kernel for the deblurring
        K = 0.0005  # Noise-to-signal ratio

        kernel = kernel.astype(np.float64)  # Convert kernel to float64
        kernel /= np.sum(kernel)
        dummy = np.copy(image)
        dummy = np.fft.fft2(dummy)
        kernel = np.fft.fft2(kernel, s=image.shape)
        kernel = np.conj(kernel) / (np.abs(kernel) ** 2 + K)
        self.deblur_image = dummy * kernel
        self.deblur_image = np.abs(np.fft.ifft2(dummy))

    # Function to remove noise from a image
    def getDeNoisedImage(self, img):

        self.denoised_image  = cv2.GaussianBlur(img, (3, 3), 1)
    
    # Create a function to adjusts the contrast of the image 
    def increaseContrast(self, img):
        self.contrast_image = cv2.addWeighted(img, 1.5, np.zeros(img.shape, img.dtype), 0, -50)

    # Created a function to sharpen the image
    def applySharpening(self, img):
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        self.sharpened_image = cv2.filter2D(img, -1, kernel)
        cv2.imwrite("receipt.png", self.sharpened_image)

    # Function to show all the images that used image processing concepts
    def showImages(self):
        plt.figure(figsize=(20, 10))
        images = [self.image, self.gray_image,self.gamma_image,self.deblur_image, self.denoised_image, 
                  self.contrast_image,self.sharpened_image]
        
        titles = ['Original', 'Grayscale','Gamma', 'Deblur' , 'Denoised', 'Contrast Enhanced','Sharpen']
        
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
      
    def resizeImage(self,scale_factor=9, method='lanczos'):
        # Open the image
        with Image.open("receipt.png") as img:
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
    def extractText(self):
            
            self.text = pytesseract.image_to_string(self.resized_img).replace('|','1').replace(',','.').replace(']','1').replace('}','1').replace('»','1').replace('>1','3').replace('£','8').replace('00','.00').replace('.O0','.00').replace('OO','.00').replace('°0','.00').replace('S.00','5.00').replace('Boor','Beer').replace('Cath','Cash').replace('Chango','Change').replace('CO','6.00').replace('WO','10.00').replace('4co','4.00').replace('a)','').replace('a2? ','').replace('>','').replace('<','').replace('Cav','Cash').replace('Chucoe','Change').replace('..','.')
            print("Extracted Text:")
            print(self.text)

    #Show the top section of the details clearly
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

    def dividedPriceDetailsIntoThreeParts(self) :        
        lines = self.text.split('\n')
        table_data = []
        
        #divided price table to the name, qty, price and also filter the price details from the text
        pattern = re.compile(r"([a-zA-Z\s]+)[\s’}]*([J\dP]?)\s*([\dA-Za-z]+[.,][0G]{2})")

        for line in lines:

            if "Sub Total" in line :
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

    # Show the bottom section of the details 
    def showBottomSection(self):
        bottom_section = re.findall(r"(Sub Total|Cash|Change)\s*[\$:]?\s*(\d+[.,]\d{2})", self.text, re.IGNORECASE)
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
        qty_map = {'}': '1', 'J': '1', 'j': '1', 'P': '2', 'p': '2', 'z':'2'}
        return qty_map.get(text, text)
    
    # Function to correct price of products
    def correctPrice(self, text):
        # Replace comma with dot for decimal point
        corrected = text.replace(',', '.')
        # Replace common OCR errors
        corrected = corrected.replace('G', '0').replace('B', '8')
        return corrected
    
if __name__ == "__main__":
    ShopBill() 


import pytesseract
from PIL import Image
from spellchecker import SpellChecker
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Infovis:
    def __init__(self):
        self.spell = SpellChecker()
        self.text = ""
        self.resized_img = None
        self.df = pd.DataFrame()
        self.all_receipts = []
        self.receipt_names = []

    def resizeImage(self, image_path, scale_factor=7, method='lanczos'):
        with Image.open(image_path) as img:
            width, height = img.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resample_filter = Image.LANCZOS if method == 'lanczos' else Image.BICUBIC if method == 'bicubic' else Image.BILINEAR
            self.resized_img = img.resize((new_width, new_height), resample_filter)

    def extractText(self):
        self.text = pytesseract.image_to_string(self.resized_img).replace('|','1').replace(',','.')
        print("\n")
        print(self.text)


    def dividedPriceDetailsIntoThreeParts(self):
        lines = self.text.split('\n')
        table_data = []
        pattern = re.compile(r"([a-zA-Z\s]+)[\s'}]*([J\dP]?)\s*([\dA-Za-z]+[.,][0G]{2})")
        for line in lines:
            if "Sub Total" in line:
                break
            match = pattern.match(line)
            if match:
                name, qty, price = match.groups()
                price = line.split()[-1]
                if qty == "":
                    words = name.split()
                    qty = words[-1]
                    name = ' '.join(words[:-1])
                name = self.correctSpelling(name)
                qty = self.correctQty(qty)
                price = self.correctPrice(price)
                table_data.append([name.strip(), int(qty), float(price)])
        self.df = pd.DataFrame(table_data, columns=['Name', 'Qty', 'Price'])

    def correctSpelling(self, text):
        words = text.split()
        corrected_words = [self.spell.correction(word) or word for word in words]
        return ' '.join(corrected_words)

    def correctQty(self, text):
        qty_map = {'}': '1', '|': '1', 'J': '1', 'j': '1', 'P': '2', 'p': '2'}
        return qty_map.get(text, text)

    def correctPrice(self, text):
        corrected = text.replace(',', '.').replace('G', '0').replace('B', '8')
        return corrected

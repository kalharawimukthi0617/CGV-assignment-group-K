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
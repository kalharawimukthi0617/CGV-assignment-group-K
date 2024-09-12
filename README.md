
# Shop Bill Processing and Data Visualization

A brief description of what this project does and who it's for


## Overview

This repository contains two Python scripts:
- shoper.py: A script for processing and extracting details from shop bills using image processing techniques and OCR (Optical Character Recognition).
- infovis.py: A script for visualizing data extracted from shop bills, providing insights into product trends, sales performance, and receipt comparisons.

## Features
### Shop Bill Processing (shoper.py)
- Image processing techniques to enhance bill images
- Text extraction using pytesseract OCR.
- Automatic correction of common OCR errors in quantities and prices.
- Extraction of product details such as names, quantities, and prices.
- Visualization of intermediate processed images for better clarity.

### Data Visualization (infovis.py)
- Reads multiple processed receipts and extracts information into a DataFrame.
- Visualizes various sales-related metrics:

## Installation

1. Clone the repository:
```bash
  git clone https://github.com/kalharawimukthi0617/CGV-assignment-group-K.git
```
 2. Install dependencies: 
    ### Dependencies include :
    - OpenCV
    - pytesseract
    - Pillow
    - SpellChecker
    - pandas
    - matplotlib
    - plotly
  
     ```bash
      pip install opencv-python pytesseract Pillow pyspellchecker pandas matplotlib plotly
    ```
  3. Install Tesseract OCR:
     Tesseract is required for OCR (Optical Character Recognition).
     - For Windows,
     Download the installer from [Tesseract OCR Windows](https://github.com/UB-Mannheim/tesseract/wiki).
     - For Ubuntu:
       ```bash
          sudo apt install tesseract-ocr
        ```
     - For macOS using Homebrew:
       ```bash
          brew install tesseract
       ```

      

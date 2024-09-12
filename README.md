
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

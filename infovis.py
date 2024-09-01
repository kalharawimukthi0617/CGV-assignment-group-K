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

    def process_receipt(self, image_path):
        self.resizeImage(image_path)
        self.extractText()
        self.dividedPriceDetailsIntoThreeParts()
        self.all_receipts.append(self.df)
        self.receipt_names.append(image_path.split('/')[-1].split('.')[0])  # Store receipt name without extension


    def resizeImage(self, image_path, scale_factor=7, method='lanczos'):
        with Image.open(image_path) as img:
            width, height = img.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resample_filter = Image.LANCZOS if method == 'lanczos' else Image.BICUBIC if method == 'bicubic' else Image.BILINEAR
            self.resized_img = img.resize((new_width, new_height), resample_filter)

    def extractText(self):
        self.text = pytesseract.image_to_string(self.resized_img).replace('|','1').replace(',','.').replace('}','1')
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
        qty_map = {'}': '1', 'J': '1', 'j': '1', 'P': '2', 'p': '2', 'z':'2'}
        return qty_map.get(text, text)

    def correctPrice(self, text):
        corrected = text.replace(',', '.').replace('G', '0').replace('B', '8')
        return corrected

    #visual all the data in dash board
    def visualizeAllData(self):
        all_data = pd.concat(self.all_receipts, keys=self.receipt_names, names=['Receipt', 'Index']).reset_index()
        all_data['Total'] = all_data['Qty'] * all_data['Price']

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Top Products by Sales", "Sales Distribution by Receipt", 
                            "Product Quantity Across Receipts", "Price vs Quantity"),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )

        # 1. Top Products by Sales (Horizontal Bar Chart)
        top_products = all_data.groupby('Name')['Total'].sum().nlargest(10).sort_values(ascending=True)
        fig.add_trace(
            go.Bar(y=top_products.index, x=top_products.values, orientation='h', name="Top Products"),
            row=1, col=1
        )

        # 2. Sales Distribution by Receipt (Pie Chart)
        sales_by_receipt = all_data.groupby('Receipt')['Total'].sum()
        fig.add_trace(
            go.Pie(labels=sales_by_receipt.index, values=sales_by_receipt.values, name="Sales by Receipt"),
            row=1, col=2
        )

        # 3. Product Quantity  (Stacked Bar Chart)
        qty_by_product_receipt = all_data.pivot_table(values='Qty', index='Name', columns='Receipt', aggfunc='sum').fillna(0)
        for receipt in qty_by_product_receipt.columns:
            fig.add_trace(
                go.Bar(x=qty_by_product_receipt.index, y=qty_by_product_receipt[receipt], name=receipt),
                row=2, col=1
            )

        # 4. Price vs Quantity (Scatter Plot)
        fig.add_trace(
            go.Scatter(x=all_data['Price'], y=all_data['Qty'], mode='markers', 
                       text=all_data['Name'], hoverinfo='text+x+y', name="Products"),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=900, width=1200, title_text="Sales Data Overview", showlegend=True)
        fig.update_xaxes(title_text="Total Sales ($)", row=1, col=1)
        fig.update_xaxes(title_text="Quantity", row=2, col=1)
        fig.update_xaxes(title_text="Price ($)", row=2, col=2)
        fig.update_yaxes(title_text="Product", row=2, col=1)
        fig.update_yaxes(title_text="Quantity", row=2, col=2)

        fig.show()

    #this is show visualize of the prducts
    def visualizeProductTrends(self):
        all_data = pd.concat(self.all_receipts, keys=self.receipt_names, names=['Receipt', 'Index']).reset_index()
        all_data['Total'] = all_data['Qty'] * all_data['Price']

        # Get top 5 products by total sales
        top_products = all_data.groupby('Name')['Total'].sum().nlargest(5).index.tolist()

        fig = go.Figure()

        for product in top_products:
            product_data = all_data[all_data['Name'] == product]
            fig.add_trace(go.Scatter(
                x=product_data['Receipt'],
                y=product_data['Total'],
                mode='lines+markers',
                name=product
            ))

        fig.update_layout(
            title="Top 5 Products: Sales Trends Across Receipts",
            xaxis_title="Receipt",
            yaxis_title="Total Sales ($)",
            legend_title="Products",
            height=600,
            width=1000
        )

        fig.show()

    #visualize the catogery performance
    def visualizeCategoryPerformance(self):
        all_data = pd.concat(self.all_receipts, keys=self.receipt_names, names=['Receipt', 'Index']).reset_index()
        all_data['Total'] = all_data['Qty'] * all_data['Price']
        
        if 'Category' not in all_data.columns:
            all_data['Category'] = all_data['Name'].apply(lambda x: 'Category ' + x[0])  # Simplistic categorization

        category_performance = all_data.groupby('Category').agg({
            'Total': 'sum',
            'Qty': 'sum',
            'Name': 'nunique'
        }).reset_index()
        category_performance['AvgPricePerItem'] = category_performance['Total'] / category_performance['Qty']

        fig = px.scatter(category_performance, x='Total', y='Qty', size='Name', color='AvgPricePerItem',
                         hover_name='Category', size_max=60,
                         labels={'Total': 'Total Sales ($)', 'Qty': 'Total Quantity Sold',
                                 'Name': 'Number of Unique Products', 'AvgPricePerItem': 'Avg Price per Item ($)'},
                         title='Category Performance Overview')

        fig.update_layout(height=600, width=1000)
        fig.show()

if __name__ == "__main__":
    infovis = Infovis()
    
    # Process multiple receipts
    receipt_images = ["shapen1.png", "shapen2.png"]  # Add more receipt image paths as needed
    for image_path in receipt_images:
        infovis.process_receipt(image_path)
    
    
    infovis.visualizeAllData()
    infovis.visualizeProductTrends()
    infovis.visualizeCategoryPerformance()
    
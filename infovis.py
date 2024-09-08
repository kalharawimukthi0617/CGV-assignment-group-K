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

    def visualizeData(self) :
        self.visualizeAllData()
        self.visualizeReceiptDetails()
        self.visualizeProductTrends()
        self.visualizeReceiptComparison()
        self.visualizeTopProductsSummary()
        self.visualizeSalesPerformance() 


    def resizeImage(self, image_path, scale_factor=7, method='lanczos'):
        with Image.open(image_path) as img:
            width, height = img.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resample_filter = Image.LANCZOS if method == 'lanczos' else Image.BICUBIC if method == 'bicubic' else Image.BILINEAR
            self.resized_img = img.resize((new_width, new_height), resample_filter)

    def extractText(self):
        self.text = pytesseract.image_to_string(self.resized_img).replace('|','1').replace(',','.').replace(']','1').replace('}','1').replace('Boor','Beer')
        print("Extracted Text:")
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
        fig.update_xaxes(title_text="Total Sales (Rs)", row=1, col=1)
        fig.update_xaxes(title_text="Quantity", row=2, col=1)
        fig.update_xaxes(title_text="Price (Rs)", row=2, col=2)
        fig.update_yaxes(title_text="Product", row=2, col=1)
        fig.update_yaxes(title_text="Quantity", row=2, col=2)

        fig.show()

    # Visualize all the receipt details
    def visualizeReceiptDetails(self):
        for i, df in enumerate(self.all_receipts):
            df['Total'] = df['Qty'] * df['Price']
            
            fig = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "pie"}]],
                                subplot_titles=("Product Sales", "Quantity Distribution"))

            # Bar chart for product sales
            fig.add_trace(
                go.Bar(x=df['Name'], y=df['Total'], name="Total Sales"),
                row=1, col=1
            )

            # Pie chart for quantity distribution
            fig.add_trace(
                go.Pie(labels=df['Name'], values=df['Qty'], name="Quantity"),
                row=1, col=2
            )

            fig.update_layout(height=500, width=1000, 
                              title_text=f"Receipt Details: {self.receipt_names[i]}")
            fig.update_xaxes(title_text="Product", row=1, col=1)
            fig.update_yaxes(title_text="Total Sales (Rs)", row=1, col=1)

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
            yaxis_title="Total Sales (Rs)",
            legend_title="Products",
            height=600,
            width=1000
        )

        fig.show()

    #this method show the comparison between the receipts
    def visualizeReceiptComparison(self):
        receipt_summaries = []
        for receipt, df in zip(self.receipt_names, self.all_receipts):
            summary = df.agg({
                'Qty': 'sum',
                'Price': 'mean',
                'Name': 'nunique'
            }).add_prefix('Total_')
            summary['Receipt'] = receipt
            summary['Total_Sales'] = (df['Qty'] * df['Price']).sum()
            receipt_summaries.append(summary)
        
        comparison_df = pd.DataFrame(receipt_summaries)
        
        fig = make_subplots(rows=2, cols=2, 
                            subplot_titles=("Total Sales", "Total Quantity", 
                                            "Average Price", "Unique Products"))
        
        fig.add_trace(go.Bar(x=comparison_df['Receipt'], y=comparison_df['Total_Sales'], name='Total Sales'),
                      row=1, col=1)
        fig.add_trace(go.Bar(x=comparison_df['Receipt'], y=comparison_df['Total_Qty'], name='Total Quantity'),
                      row=1, col=2)
        fig.add_trace(go.Bar(x=comparison_df['Receipt'], y=comparison_df['Total_Price'], name='Average Price'),
                      row=2, col=1)
        fig.add_trace(go.Bar(x=comparison_df['Receipt'], y=comparison_df['Total_Name'], name='Unique Products'),
                      row=2, col=2)
        
        fig.update_layout(height=800, width=1000, title_text="Receipt Comparison")
        fig.show()


    #visualize the top products summary
    def visualizeTopProductsSummary(self):
        all_data = pd.concat(self.all_receipts, keys=self.receipt_names, names=['Receipt', 'Index']).reset_index()
        all_data['Total'] = all_data['Qty'] * all_data['Price']

        # Get top 5 products by total sales
        top_products = all_data.groupby('Name')['Total'].sum().nlargest(5)
        
        fig = go.Figure()

        # Add bar chart for total sales
        fig.add_trace(go.Bar(
            x=top_products.index,
            y=top_products.values,
            name='Total Sales',
            marker_color='lightblue'
        ))

        # Add information about quantity sold and average price
        for product in top_products.index:
            product_data = all_data[all_data['Name'] == product]
            qty_sold = product_data['Qty'].sum()
            avg_price = product_data['Price'].mean()
            
            fig.add_annotation(
                x=product,
                y=top_products[product],
                text=f"Qty: {qty_sold}<br>Avg Price: Rs{avg_price:.2f}",
                showarrow=True,
                arrowhead=4,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#636363",
                ax=0,
                ay=-40
            )

        fig.update_layout(
            title='Top 5 Products Summary',
            xaxis_title='Product Name',
            yaxis_title='Total Sales (Rs)',
            height=600,
            width=1000,
            showlegend=False
        )

        fig.show()

    #visualize the sales performance
    def visualizeSalesPerformance(self):
        all_data = pd.concat(self.all_receipts, keys=self.receipt_names, names=['Receipt', 'Index']).reset_index()
        all_data['Total'] = all_data['Qty'] * all_data['Price']

        total_sales = all_data['Total'].sum()
        avg_sales_per_receipt = total_sales / len(self.receipt_names)
        max_sales_receipt = all_data.groupby('Receipt')['Total'].sum().max()

        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=avg_sales_per_receipt,
            title={'text': "Average Sales per Receipt"},
            delta={'reference': max_sales_receipt, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, max_sales_receipt]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, max_sales_receipt/2], 'color': "lightgray"},
                    {'range': [max_sales_receipt/2, max_sales_receipt], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_sales_receipt
                }
            }
        ))

        fig.update_layout(
            title='Sales Performance Gauge',
            height=500,
            width=800
        )

        # Add annotations with additional information
        fig.add_annotation(
            x=0.5, y=-0.1,
            text=f"Total Sales: Rs{total_sales:.2f}<br>Number of Receipts: {len(self.receipt_names)}<br>Highest Sales in a Receipt: Rs{max_sales_receipt:.2f}",
            showarrow=False,
            xref='paper', yref='paper',
            align='center'
        )

        fig.show()

if __name__ == "__main__":
    infovis = Infovis()
    
    # Process multiple receipts
    receipt_images = ["receipt1.png", "receipt2.png"]  # Add more receipt image paths as needed
    for image_path in receipt_images:
        infovis.process_receipt(image_path)
    
    #Show all the 6 data visualizations
    infovis.visualizeData()
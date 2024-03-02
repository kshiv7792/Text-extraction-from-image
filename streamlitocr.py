import streamlit as st
import paddleocr
import re
import pandas as pd
from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
ocr = PaddleOCR(lang='en')
import os

def main():
    st.title("Invoice OCR App")

    # Specify the directory containing the images
    image_dir = ""

    # Create a list to store the results
    results = []

    # Iterate over the images in the directory and call the `process_image` function
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpeg"):
            image_path = os.path.join(image_dir, filename)

            # Read the image using OpenCV
            image = cv2.imread(image_path)

            # Perform OCR on the image using PaddleOCR
            result = ocr.ocr(image)

            # Store the result in the list
            results.append((filename, result))

    # Process the stored results
    text = []
    for filename, result in results:
        st.subheader(f"Text in {filename}:")
        for line in result:
            for word in line:
                st.write(word[1][0])
                text.append(word[1][0])
            st.write()
        st.write()

    # Create a DataFrame to store the extracted information
    df1 = pd.DataFrame(columns=['Bill_Date', 'Bill_No', 'Bill_Product', 'Bill_Quantity', 'Price'])
    bill_no = None
    bill_date = None

    for i in range(len(text)):
        item = text[i]

        # Match bill number
        match_bill_no = re.search(r"\d{9}-\d{1,6}", item)
        if match_bill_no:
            bill_no = match_bill_no.group()
            st.write("Bill Number:", bill_no)

        # Match bill date
        match_bill_date = re.search(r"\d{2}/\d{2}/\d{4}", item)
        if match_bill_date:
            bill_date = match_bill_date.group()
            st.write("Bill Date:", bill_date)

        # Match product name
        match_product = re.search(
            r"[a-zA-Z]+[]\s\d+-[a-zA-Z]+\d[a-z]+|[a-aA-Z]+\s[a-zA-z]+\s+[a-zA-z]+\s\d+[a-zA-z]|[A-Z]+-\d+[a-zA-Z]|[A-z]+\s[A-Z]+-[a-zA-Z]+",
            item)
        if match_product:
            product_name = match_product.group()
            st.write("Product Name:", product_name)

            # Initialize quantity and price
            quantity = None
            price = None

            # Check the next row for quantity (single/double-digit integer)
            if i + 1 < len(text):
                next_item = text[i + 1]
                match_quantity = re.search(r"\b(\d{1,2})\b", next_item)

                if match_quantity:
                    quantity = int(match_quantity.group())

            # Check the next three rows for the price (first float value)
            for j in range(i + 1, i + 4):
                if j < len(text):
                    next_item = text[j]
                    match_price = re.search(r"\b(\d+\.\d+)\b", next_item)

                    if match_price:
                        price = float(match_price.group())
                        break  # Stop searching for price after the first match

            # Set default quantity as 1 if no value is found
            if quantity is None:
                quantity = 1

            # Add the data to the DataFrame
            df1.loc[len(df1)] = [bill_date, bill_no, product_name, quantity, price]

    # Display the extracted information in a table
    st.subheader("Extracted Information:")
    st.write(df1)

if __name__ == "__main__":
    # Load PaddleOCR
    ocr = PaddleOCR(lang='en')

    # Run the Streamlit app
    main()


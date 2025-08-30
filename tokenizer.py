# 3. Import libraries
import os
from transformers import AutoTokenizer
from PyPDF2 import PdfReader

# Load a tokenizer (we can swap model later)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

import os
import pdfplumber
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from transformers import AutoTokenizer

# Initialize tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def extract_text_from_pdf(pdf_path):
    text = ""
    # Try pdfplumber (works if PDF has selectable text)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    # If still empty, fallback to OCR
    if not text.strip():
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    return text.strip()

def process_pdfs(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                text = extract_text_from_pdf(pdf_path)
                if text:
                    tokens = tokenizer.tokenize(text)
                    output_file = os.path.join(output_folder, file.replace(".pdf", ".txt"))
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(" ".join(tokens))
                else:
                    print(f"No text found in {pdf_path}")

# Example run
input_path = "D:/NCRT_class10_dataset/"
output_path = "D:/NCRT_class10_dataset/tokenized_texts_retake/"
process_pdfs(input_path, output_path)

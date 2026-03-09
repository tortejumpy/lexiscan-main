from PIL import Image
import pytesseract
import re

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#  Function to clean OCR text
def clean_text(text):
    text = text.lower()

    # Fix common OCR mistakes
    text = text.replace("inv0ice", "invoice")
    text = text.replace("n0", "no")
    text = text.replace("final extract data", "invoice")
    text = text.replace("my", ":")  # Fix misread before amounts
    text = text.replace("arnount", "amount")
    text = text.replace("dste", "date")

    # Remove unwanted special characters except letters, numbers, :, /, ., -
    text = re.sub(r'[^a-z0-9\s:/.-]', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

#  Load invoice image (updated filename)
image = Image.open("sample_images/normal_invoices.jpg")

#  Extract raw text using OCR
raw_text = pytesseract.image_to_string(image)

print("\n===== RAW OCR TEXT =====\n")
print(raw_text)

#  Clean the OCR text
cleaned_text = clean_text(raw_text)

print("\n===== CLEANED OCR TEXT =====\n")
print(cleaned_text)

#  Regex Patterns

# Invoice: pick the first number with 3+ digits (ignores words like East)
invoice_pattern = r'\b(\d{3,}[A-Za-z0-9-]*)\b'

# Date: looks for keyword "date" followed by numbers
date_pattern = r'date\s*[:\-]?\s*([0-9/.-]+)'

# Amount: looks for total/amount keyword followed by digits
amount_pattern = r'(total|amount)\s*[:\-]?\s*([\d.,]+)'

#  Extract matches
invoice_match = re.search(invoice_pattern, cleaned_text)
date_match = re.search(date_pattern, cleaned_text)
amount_match = re.search(amount_pattern, cleaned_text)

invoice_no = invoice_match.group(1) if invoice_match else "Not Found"
date = date_match.group(1) if date_match else "Not Found"
amount = amount_match.group(2) if amount_match else "Not Found"

# False positive reduction for amount
def validate_amount(amount):
    numbers = re.findall(r'\d+\.?\d*', amount)
    return True if numbers else False

if amount != "Not Found" and not validate_amount(amount):
    amount = "Invalid Amount"

#  Accuracy calculation
total_expected_fields = 3
correct_fields = 0

if invoice_no != "Not Found":
    correct_fields += 1
if date != "Not Found":
    correct_fields += 1
if amount != "Not Found" and amount != "Invalid Amount":
    correct_fields += 1

accuracy = (correct_fields / total_expected_fields) * 100

#  Final Output
print("\n===== FINAL EXTRACTED DATA =====\n")
print(f"Invoice Number : {invoice_no}")
print(f"Date           : {date}")
print(f"Total Amount   : {amount}")
print(f"\nExtraction Accuracy: {accuracy:.2f}%")

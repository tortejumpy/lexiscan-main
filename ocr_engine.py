from PIL import Image, ImageFilter
import pytesseract

def extract_text(image_path):
    img = Image.open(image_path)

    # Convert to grayscale
    img = img.convert("L")

    # Sharpen image
    img = img.filter(ImageFilter.SHARPEN)

    text = pytesseract.image_to_string(img)
    return text

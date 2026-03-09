iimport re

def clean_text(text):
    text = re.sub(r'[^A-Za-z0-9\s:/.-]', '', text)
    text = re.sub(r'\s+', ' ', text)

    # Fix common OCR mistakes only inside words
    text = re.sub(r'Inv0ice', 'Invoice', text)
    text = re.sub(r'N0', 'No', text)

    return text.strip()

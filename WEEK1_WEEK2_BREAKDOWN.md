# Week 1 & Week 2 Deliverables - LexiScan Auto

## ✅ Week 1: OCR Pipeline & Data Preparation

### **Goal:** Build robust OCR pipeline for text extraction from noisy or low-quality scanned documents

### **Deliverables:**

#### 1. **Project Structure Setup**
```
lexiscan-auto/
├── src/
│   ├── ocr/              # OCR modules
│   ├── models/           # NER models
│   ├── utils/            # Utilities
│   └── validation/       # Validation (Week 3)
├── data/
│   ├── raw/              # Raw contracts
│   └── annotations/      # Training data
├── configs/              # Configuration
├── tests/                # Test scripts
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

**Files Created:**
- `requirements.txt` - All Python dependencies
- `configs/config.yaml` - System configuration
- `.gitignore` - Version control exclusions
- `.env.example` - Environment variables template
- `README.md` - Project documentation

---

#### 2. **OCR Pipeline Modules**

##### **A. PDF Processor** (`src/ocr/pdf_processor.py`)
**Purpose:** Convert PDF to images and extract metadata

**Key Functions:**
```python
class PDFProcessor:
    def pdf_to_images(pdf_path, dpi=300)
        # Converts PDF pages to images
    
    def extract_pdf_metadata(pdf_path)
        # Gets PDF info (pages, author, etc.)
    
    def is_scanned_pdf(pdf_path)
        # Detects if PDF is scanned or text-based
```

**What it does:**
- Opens PDF files using PyMuPDF
- Converts each page to high-quality images (300 DPI)
- Determines if PDF needs OCR or has extractable text

---

##### **B. OCR Engine** (`src/ocr/ocr_engine.py`)
**Purpose:** Extract text from images using Tesseract OCR

**Key Functions:**
```python
class OCREngine:
    def preprocess_image(image)
        # Enhances image quality
        # - Converts to grayscale
        # - Increases contrast
        # - Removes noise
        # - Sharpens text
    
    def extract_text(image_path)
        # Runs Tesseract OCR
        # Returns extracted text
    
    def extract_text_with_confidence(image_path)
        # Returns text + confidence scores
    
    def get_ocr_quality_metrics(image_path)
        # Calculates OCR accuracy metrics
```

**What it does:**
- Preprocesses images for better OCR accuracy
- Runs Tesseract to extract text
- Provides confidence scores (how sure it is)
- Calculates quality metrics

---

##### **C. Text Cleaner** (`src/ocr/text_cleaner.py`)
**Purpose:** Clean and normalize OCR-extracted text

**Key Functions:**
```python
class TextCleaner:
    def clean_text(text)
        # Removes extra whitespace
        # Fixes common OCR errors
        # Normalizes Unicode characters
    
    def fix_common_ocr_errors(text)
        # Fixes: "0" → "O", "1" → "l", etc.
    
    def remove_page_numbers(text)
        # Removes page footers/headers
    
    def get_text_statistics(text)
        # Returns word count, char count, etc.
```

**What it does:**
- Cleans up messy OCR output
- Fixes common mistakes (0 vs O, 1 vs l)
- Removes page numbers and headers
- Normalizes text format

---

##### **D. OCR Pipeline** (`src/ocr/pipeline.py`)
**Purpose:** Orchestrate complete OCR process

**Key Functions:**
```python
class OCRPipeline:
    def process_document(pdf_path)
        # Complete pipeline:
        # 1. Check if PDF is scanned
        # 2. Convert to images if needed
        # 3. Run OCR on each page
        # 4. Clean extracted text
        # 5. Return OCRResult object
    
    def process_batch(pdf_paths)
        # Process multiple PDFs
```

**What it does:**
- Combines all OCR components
- Handles both scanned and text-based PDFs
- Processes single or multiple documents
- Returns structured results with quality metrics

---

#### 3. **Utility Modules**

##### **A. Helpers** (`src/utils/helpers.py`)
**Purpose:** Common utility functions

**Key Functions:**
```python
def load_config(config_path)
    # Loads YAML configuration

def setup_logging(log_file, log_level)
    # Configures logging system

def ensure_dir(directory)
    # Creates directories if missing

class EntityLabels:
    # Defines entity types:
    # - PARTY, DATE, AMOUNT, JURISDICTION, TERM
```

---

##### **B. Annotator** (`src/utils/annotator.py`)
**Purpose:** Convert CUAD dataset to NER training format

**Key Functions:**
```python
class NERAnnotator:
    def convert_to_iob2(annotations)
        # Converts to IOB2 format
        # B-PARTY, I-PARTY, O, etc.
    
    def convert_to_spacy_format(annotations)
        # Converts to Spacy JSON format
    
    def extract_from_master_clauses(csv_path)
        # Extracts entities from master_clauses.csv
```

**What it does:**
- Processes CUAD dataset annotations
- Converts to training data formats
- Prepares data for NER model training

---

#### 4. **Test Script**

##### **OCR Pipeline Test** (`tests/test_ocr_pipeline.py`)
**Purpose:** Validate OCR pipeline functionality

**What it does:**
- Tests PDF processing
- Tests OCR extraction
- Tests text cleaning
- Logs quality metrics

---

### **Week 1 Demo:**

**Run this to show Week 1 work:**
```powershell
python tests/test_ocr_pipeline.py
```

**Expected Output:**
- Processes sample PDF
- Shows extracted text
- Displays OCR confidence scores
- Shows quality metrics

---

## ✅ Week 2: NER Model Development

### **Goal:** Train contextual understanding models (Spacy NER or deep learning sequence model)

### **Deliverables:**

#### 1. **Baseline NER Model**

##### **A. Regex Extractor** (`src/models/baseline/regex_extractor.py`)
**Purpose:** Rule-based entity extraction using patterns

**Key Features:**
```python
class RegexExtractor:
    # Patterns for:
    date_patterns = [
        r'\b(?:January|February|...|December)\s+\d{1,2},\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        # ... more patterns
    ]
    
    amount_patterns = [
        r'\$[\d,]+(?:\.\d{2})?',
        r'USD\s*[\d,]+',
        # ... more patterns
    ]
    
    jurisdiction_patterns = [
        r'State of [A-Z][a-z]+',
        r'[A-Z][a-z]+(?:,\s*[A-Z]{2})?',
        # ... more patterns
    ]
    
    party_patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|LLC|Corp\.)',
        # ... more patterns
    ]
```

**Key Functions:**
```python
def extract_dates(text)
    # Finds all dates

def extract_amounts(text)
    # Finds all monetary amounts

def extract_jurisdictions(text)
    # Finds all jurisdictions

def extract_parties(text)
    # Finds all party names

def extract_all(text)
    # Extracts all entity types
    # Removes overlaps
    # Returns sorted list
```

**What it does:**
- Uses regex patterns to find entities
- No training required
- Fast and reliable for common patterns
- Good baseline performance

---

##### **B. TF-IDF Classifier** (`src/models/baseline/tfidf_classifier.py`)
**Purpose:** Text classification using TF-IDF features

**Key Features:**
```python
class TFIDFClassifier:
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000)),
        ('classifier', LogisticRegression())
    ])
    
    def train(texts, labels)
        # Trains classifier
        # Returns metrics
    
    def predict(texts)
        # Predicts entity types
    
    def get_feature_importance()
        # Shows important words
```

**What it does:**
- Converts text to numerical features (TF-IDF)
- Trains logistic regression classifier
- Classifies entity types
- Provides feature importance

---

##### **C. Baseline NER Model** (`src/models/baseline/baseline_model.py`)
**Purpose:** Combined baseline approach

**What it does:**
- Combines RegexExtractor + TFIDFClassifier
- Provides complete baseline NER solution
- No deep learning required
- Fast inference

---

#### 2. **Spacy Custom NER**

##### **A. Spacy NER Trainer** (`src/models/spacy_ner/trainer.py`)
**Purpose:** Train custom Spacy NER model

**Key Features:**
```python
class SpacyNERTrainer:
    def __init__(base_model="en_core_web_sm")
        # Loads base Spacy model
        # Adds custom entity labels
    
    def train(training_data, n_iter=30)
        # Training loop:
        # - Shuffles data
        # - Updates model weights
        # - Calculates loss
        # Returns final metrics
    
    def evaluate(test_data)
        # Calculates precision, recall, F1
    
    def save_model(output_dir)
        # Saves trained model
```

**Key Functions:**
```python
def create_synthetic_training_data(contracts_dir, master_clauses_path)
    # Creates training data from:
    # - CUAD dataset
    # - master_clauses.csv
    # - Raw contract files
    # Returns Spacy-compatible format
```

**What it does:**
- Loads pre-trained Spacy model
- Adds custom entity labels (PARTY, DATE, AMOUNT, etc.)
- Trains on annotated data
- Evaluates performance
- Saves trained model

---

##### **B. Spacy NER Predictor** (`src/models/spacy_ner/predictor.py`)
**Purpose:** Use trained Spacy model for inference

**Key Functions:**
```python
class SpacyNERPredictor:
    def load_model(model_path)
        # Loads trained model
    
    def predict(text)
        # Extracts entities from text
    
    def predict_batch(texts)
        # Batch processing
    
    def visualize_entities(text)
        # Creates HTML visualization
```

**What it does:**
- Loads trained Spacy model
- Extracts entities from new contracts
- Supports batch processing
- Provides visualization

---

#### 3. **Bi-LSTM Deep Learning Model**

##### **Bi-LSTM NER** (`src/models/bilstm/model.py`)
**Purpose:** Deep learning sequence model for NER

**Architecture:**
```python
class BiLSTMNER:
    # Model architecture:
    # 1. Embedding layer (100-dim)
    # 2. Bidirectional LSTM (128 units)
    # 3. Bidirectional LSTM (64 units)
    # 4. Time-distributed Dense (softmax)
```

**Key Functions:**
```python
def prepare_data(sentences, tags)
    # Builds vocabularies
    # Converts to indices
    # Pads sequences

def build_model()
    # Creates Bi-LSTM architecture

def train(X_train, y_train, epochs=50)
    # Trains model
    # Early stopping
    # Learning rate scheduling

def predict(X)
    # Predicts entity tags

def evaluate(X_test, y_test)
    # Calculates F1, precision, recall
```

**What it does:**
- Deep learning approach using TensorFlow/Keras
- Bidirectional LSTM for context understanding
- Sequence tagging (IOB2 format)
- State-of-the-art performance

---

#### 4. **Demo Script**

##### **Baseline Demo** (`demo.py`)
**Purpose:** Demonstrate NER extraction

**What it does:**
```python
# 1. Load baseline model
model = BaselineNERModel()

# 2. Find sample contracts
contracts = find_contracts("data/raw/full_contract_txt/")

# 3. Process each contract
for contract in contracts[:3]:
    text = read_file(contract)
    entities = model.extract_entities(text)
    
    # 4. Display results
    print(f"Found {len(entities)} entities")
    print_entity_summary(entities)
    print_first_10_entities(entities)
```

---

### **Week 2 Demo:**

**Run this to show Week 2 work:**
```powershell
python demo.py
```

**Expected Output:**
- Processes 3 sample contracts
- Extracts entities using baseline model
- Shows entity counts by type
- Displays examples

---

## 📊 Summary: Week 1 vs Week 2

### **Week 1 Focus: OCR Pipeline**
**Files to show:**
- `src/ocr/pdf_processor.py`
- `src/ocr/ocr_engine.py`
- `src/ocr/text_cleaner.py`
- `src/ocr/pipeline.py`
- `tests/test_ocr_pipeline.py`

**Demo:** `python tests/test_ocr_pipeline.py`

**Key Achievement:** Robust OCR pipeline that handles scanned PDFs with quality metrics

---

### **Week 2 Focus: NER Models**
**Files to show:**
- `src/models/baseline/regex_extractor.py`
- `src/models/baseline/tfidf_classifier.py`
- `src/models/spacy_ner/trainer.py`
- `src/models/spacy_ner/predictor.py`
- `src/models/bilstm/model.py`
- `demo.py`

**Demo:** `python demo.py`

**Key Achievement:** Three NER approaches (Baseline, Spacy, Bi-LSTM) with increasing sophistication

---

## 🎯 For Your Review Presentation

### **Week 1 Talking Points:**
1. ✅ Built complete OCR pipeline for PDF processing
2. ✅ Handles both scanned and text-based PDFs
3. ✅ Image preprocessing for better accuracy
4. ✅ OCR confidence scoring and quality metrics
5. ✅ Text cleaning and normalization
6. ✅ Data annotation tools for NER training

### **Week 2 Talking Points:**
1. ✅ Implemented 3 NER approaches:
   - Baseline (regex + TF-IDF) - Fast, no training
   - Spacy - Custom NER, moderate training
   - Bi-LSTM - Deep learning, best accuracy
2. ✅ Extracts 5 entity types (PARTY, DATE, AMOUNT, JURISDICTION, TERM)
3. ✅ Training data preparation from CUAD dataset
4. ✅ Model evaluation metrics (F1, precision, recall)
5. ✅ Working demo with real contracts

---

## 📁 Files to Package for Review

### **Week 1 Package:**
```
week1_deliverables/
├── src/ocr/
│   ├── pdf_processor.py
│   ├── ocr_engine.py
│   ├── text_cleaner.py
│   └── pipeline.py
├── src/utils/
│   ├── helpers.py
│   └── annotator.py
├── tests/
│   └── test_ocr_pipeline.py
├── configs/config.yaml
├── requirements.txt
└── README_WEEK1.md
```

### **Week 2 Package:**
```
week2_deliverables/
├── src/models/baseline/
│   ├── regex_extractor.py
│   ├── tfidf_classifier.py
│   └── baseline_model.py
├── src/models/spacy_ner/
│   ├── trainer.py
│   └── predictor.py
├── src/models/bilstm/
│   └── model.py
├── demo.py
├── data/raw/full_contract_txt/ (sample contracts)
└── README_WEEK2.md
```

---

**Would you like me to create separate packages for Week 1 and Week 2 with only the relevant files?**

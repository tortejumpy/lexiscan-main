# Quick Start Guide - LexiScan Auto

## Step-by-Step Setup and Execution

### Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10 or higher
- ✅ pip (Python package manager)
- ✅ Internet connection (for downloading packages)

---

## Option 1: Quick Demo (Recommended for First Run)

This is the fastest way to see the system in action without any external dependencies.

### Step 1: Open Terminal in Project Directory

```powershell
cd d:\Projects\lexiscan-auto
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This will take 2-5 minutes. It installs all necessary packages.

### Step 4: Download Spacy Language Model

```powershell
python -m spacy download en_core_web_sm
```

### Step 5: Run the Demo

```powershell
python demo.py
```

**Expected Output:**
- Processes 3 sample contracts
- Extracts entities (PARTY, DATE, AMOUNT, JURISDICTION, TERM)
- Shows entity counts and examples

**No credentials or API keys required!**

---

## Option 2: Run the REST API Server

If you want to use the API to extract entities from your own documents:

### Step 1-4: Same as Option 1

Complete steps 1-4 from Option 1 above.

### Step 5: Start the API Server

```powershell
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 6: Test the API

Open a new terminal (keep the server running) and test:

```powershell
# Health check
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/docs
```

### Step 7: Extract Entities from a Contract

```powershell
# Using curl (if installed)
curl -X POST "http://localhost:8000/extract?model=baseline" -F "file=@data/raw/full_contract_txt/YourContract.txt"

# Or use the interactive API docs at:
# http://localhost:8000/docs
```

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Option 3: Docker Deployment (Advanced)

If you have Docker installed:

### Step 1: Install Docker Desktop

Download from: https://www.docker.com/products/docker-desktop/

### Step 2: Build and Run

```powershell
cd d:\Projects\lexiscan-auto

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Access API at http://localhost:8000
```

---

## Troubleshooting

### Issue 1: "python not recognized"

**Solution:**
- Install Python from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### Issue 2: "pip not recognized"

**Solution:**
```powershell
python -m ensurepip --upgrade
```

### Issue 3: Virtual environment activation fails

**Solution:**
```powershell
# Enable script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\activate
```

### Issue 4: Import errors or module not found

**Solution:**
```powershell
# Make sure you're in the virtual environment
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue 5: Demo shows no contracts found

**Solution:**
- Ensure you're in the project directory: `d:\Projects\lexiscan-auto`
- Check that `data/raw/full_contract_txt/` contains .txt files

---

## What Each Component Does

### 1. **demo.py**
- Tests the baseline NER model
- Processes sample contracts
- Shows extracted entities
- **No setup required beyond Python packages**

### 2. **API Server**
- Provides REST endpoints
- Accepts file uploads (TXT format)
- Returns structured JSON with entities
- Includes validation and date standardization

### 3. **Models**
- **Baseline**: Regex + TF-IDF (ready to use, no training)
- **Spacy**: Custom NER (requires training)
- **Bi-LSTM**: Deep learning (requires training)

---

## Testing the System

### Test 1: Run Demo
```powershell
python demo.py
```

### Test 2: Test OCR Pipeline
```powershell
python tests/test_ocr_pipeline.py
```

### Test 3: API Health Check
```powershell
# Start API first
python -m uvicorn src.api.main:app --reload

# In another terminal
curl http://localhost:8000/health
```

---

## No Credentials Required!

✅ **No API keys needed**  
✅ **No database setup required**  
✅ **No external services**  
✅ **All processing is local**  

The only thing you need is:
- Python 3.10+
- Internet connection (for initial package installation)

---

## Quick Command Reference

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run demo
python demo.py

# Start API server
python -m uvicorn src.api.main:app --reload

# Install packages
pip install -r requirements.txt

# Download Spacy model
python -m spacy download en_core_web_sm

# Deactivate virtual environment
deactivate
```

---

## Next Steps After Running

1. ✅ **Verify demo works** - Run `python demo.py`
2. ✅ **Test API** - Start server and visit http://localhost:8000/docs
3. ✅ **Process your contracts** - Upload TXT files via API
4. 📊 **Train models** - Use Spacy or Bi-LSTM for better accuracy
5. 🚀 **Deploy** - Use Docker for production

---

## Need Help?

Check the logs:
- Demo logs: Console output
- API logs: `logs/api.log`
- Error logs: Console output

Review documentation:
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Walkthrough](C:\Users\harsh\.gemini\antigravity\brain\4476f314-257c-491e-a5b4-8d92d70c20e6\walkthrough.md)

---

## Summary

**Fastest way to run:**
```powershell
cd d:\Projects\lexiscan-auto
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python demo.py
```

**That's it! No credentials, no API keys, no complex setup!** 🎉

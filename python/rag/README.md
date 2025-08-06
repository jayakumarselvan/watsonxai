
#### 🔧 Setup
Follow these steps to get started:

##### Create a virtual environment
```
python3.12 -m venv .venv
```

##### Activate the virtual environment
```
source .venv/bin/activate
```

##### Install required packages
```
pip install langchain-ibm python-dotenv PyPDF2 chromadb sentence-transformers langchain-huggingface
```

#### 📄 Usage
Make sure your PDF file (e.g., sample.pdf) is in the project directory.

Run the application:
```
python rag_app.py
```
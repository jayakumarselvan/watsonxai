
#### 🔧 Setup

##### Create a virtual environment
```
python3 -m venv .venv
```

##### Activate the virtual environment
```
source .venv/bin/activate
```

##### Install required packages
```
pip install fastapi "uvicorn[standard]" motor pymongo
```

Run the application:
```
uvicorn main:app --reload
```
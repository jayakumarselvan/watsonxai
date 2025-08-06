
# 🎧 Audio Summarizer with IBM Watson & Watsonx

This project is a Python-based **Audio Summarizer** that takes an audio file (e.g., `.mp3`), converts it to text using **IBM Watson Speech to Text**, and then generates a concise **summary** using **Watsonx's LLM (LLaMA 3)**.

---

## 🚀 Features

- 🔊 Convert audio to text using **IBM Watson Speech to Text**
- 🧠 Generate summary using **Watsonx.ai LLaMA 3-70B Instruct model**
- 🪶 Lightweight and easy to run

---

## Create and Activate a Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies
```
pip install -r requirements.txt
```

## .env Configuration
```
WATSONX_APIKEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_S2T_APIKEY=your_speech_to_text_api_key
WATSONX_S2T_URL=your_speech_to_text_api_url
```


## Example Audio
File path: `./2025_IBM_Quantum_Roadmap_update.mp3`

Audio Source from : https://www.youtube.com/watch?v=_y43boNNoVo


## Run the application:
```
python audio_summarizer.py
```
from fastapi import APIRouter, UploadFile, File
import shutil
import uuid
from app.services.speech_to_text_service import SpeechToTextService
from app.services.watsonx_ai import WatsonxService

router = APIRouter()

s2t_service = SpeechToTextService()
watsonx_service = WatsonxService()


@router.post("/summary")
async def summarize_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Convert audio to text
        mime_type = file.content_type
        transcript = s2t_service.transcribe(temp_filename, mime_type)

        # Generate summary
        summary = watsonx_service.generate_summary(transcript)

        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}

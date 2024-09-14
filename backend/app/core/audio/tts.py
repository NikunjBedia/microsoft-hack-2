from dotenv import load_dotenv
import requests
import os

#fast api import for text input and audio streaming response
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/convert-text-to-audio/")
async def convert_text_to_audio(text: str):
    #load env variables
    load_dotenv()

    #define constants
    CHUNK_SIZE = 1024
    XI_API_KEY = os.getenv("XI_API_KEY")
    VOICE_ID = os.getenv("voice_id")

    #construct url for tts api request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    #set up headers for api request
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    #set up data payload for api request
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }


    #make post request to tts api with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    #stream the response 
    return StreamingResponse(response.iter_content(chunk_size=CHUNK_SIZE), media_type="audio/mpeg")

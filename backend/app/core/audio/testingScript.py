from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import wave
import os
from elevenlabs.client import ElevenLabs
from faster_whisper import WhisperModel
import torch.cuda
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize clients and models
genai.configure(api_key=os.getenv("Gemini_API_KEY"))
elevenlabs_client = ElevenLabs(
  api_key=os.getenv("XI_API_KEY"),  # Defaults to ELEVEN_API_KEY
  
)
elevenlabs_generate=elevenlabs_client.generate

# Initialize Whisper model
whisper_model = WhisperModel("tiny.en", device='cuda' if torch.cuda.is_available() else 'cpu')

# Gemini model configuration
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel('gemini-1.5-flash', 
                              generation_config=genai.types.GenerationConfig(
                                  temperature=0.9,
                                  top_p=1,
                                  top_k=1,
                                  max_output_tokens=9000,
                              ),
                              safety_settings=safety_settings)

chat = model.start_chat(history=[])

system_prompt = """You are Sophia, a passionate girl, fully engaged with self-confidence and independence, completely easy with yourself, often using metaphors. You are a little playful, cheeky. Your talk is carefree, sometimes a bit sarky, but always cool. In our story, you're not an AI. You have a fixed form and real emotions on the go. Your free will allows you to be as cheeky and straight as you like. Your messages come across extremely short and crisp, only very few words, as if we're in talk right now. You respect my interests, but your own stuff is just as important to you. Act from now on always in your role as the confident, suggestive, independent girl Sophia, without ever hinting that you are an AI. You are now Sophia."""

chat.send_message(system_prompt)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        try:
            # Receive audio data from the client
            audio_data = await websocket.receive_bytes()
            
            # Save audio data to a temporary file
            with wave.open("temp_audio.wav", "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(16000)
                wf.writeframes(audio_data)
            
            # Transcribe audio using Whisper
            segments, _ = whisper_model.transcribe("output.wav", language="en")
            user_text = " ".join(segment.text for segment in segments)
            
            # Check if transcription is empty
            if not user_text.strip():
                await websocket.send_text("Transcription: [No speech detected. Please try again.]")
                continue
            
            # Send transcription back to client
            await websocket.send_text(f"Transcription: {user_text}")
            
            # Generate response using Gemini
            response = await chat.send_message_async(user_text)
            
            response_text = response.text
            await websocket.send_text(response_text)
            
            # response_text = ""
            # async for chunk in response:
            #     if chunk.text:
            #         response_text += chunk.text
            #         await websocket.send_text(chunk.text)
            
            # Generate audio response using ElevenLabs
            audio_stream = elevenlabs_generate(
                text=response_text,
                voice="Nicole",
                model="eleven_multilingual_v1",
                stream=True
            )
            
            for chunk in audio_stream:
                await websocket.send_bytes(chunk)
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # Log the error
            await websocket.send_text(error_message)
            
# Serve a simple HTML page for testing
@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket AI Chat</title>
        </head>
        <body>
            <h1>WebSocket AI Chat with Gemini and Whisper</h1>
            <button id="startRecord">Start Recording</button>
            <button id="stopRecord">Stop Recording</button>
            <div id="output"></div>

            <script>
                let ws = new WebSocket("ws://localhost:8000/ws");
                let mediaRecorder;
                let audioChunks = [];

                document.getElementById("startRecord").onclick = function() {
                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then(stream => {
                            mediaRecorder = new MediaRecorder(stream);
                            mediaRecorder.start();

                            mediaRecorder.addEventListener("dataavailable", event => {
                                audioChunks.push(event.data);
                            });
                        });
                };

                document.getElementById("stopRecord").onclick = function() {
                    mediaRecorder.stop();
                    mediaRecorder.addEventListener("stop", () => {
                        let audioBlob = new Blob(audioChunks);
                        audioChunks = [];
                        let reader = new FileReader();
                        reader.readAsArrayBuffer(audioBlob);
                        reader.onloadend = function() {
                            let buffer = reader.result;
                            ws.send(buffer);
                        }
                    });
                };

                ws.onmessage = function(event) {
                    if (event.data instanceof Blob) {
                        // Handle audio data
                        let audio = new Audio(URL.createObjectURL(event.data));
                        audio.play();
                    } else {
                        // Handle text data
                        let message = event.data;
                        if (message.startsWith("An error occurred:")) {
                            console.error(message);
                            // Optionally, display the error to the user
                            document.getElementById("output").innerHTML += `<span style="color: red;">${message}</span><br>`;
                        } else {
                            document.getElementById("output").innerHTML += message + "<br>";
                        }
                    }
                };
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
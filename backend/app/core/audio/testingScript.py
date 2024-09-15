from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import uvicorn
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import wave
import os
import io
from elevenlabs.client import ElevenLabs
from faster_whisper import WhisperModel
import torch.cuda
from dotenv import load_dotenv
import ffmpeg

load_dotenv()

app = FastAPI()

# Initialize clients and models
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
            
            # Debug: Check received data size
            print(f"Received audio data size: {len(audio_data)} bytes")
            
            # Save received WebM audio to a temporary file
            with open("temp_audio.webm", "wb") as f:
                f.write(audio_data)
            
            # Debug: Check saved file size
            print(f"Saved WebM file size: {os.path.getsize('temp_audio.webm')} bytes")
            

            
            # Transcribe audio using Whisper
            segments, _ = whisper_model.transcribe("temp_audio.webm", language="en")
            user_text = " ".join(segment.text for segment in segments)
            
            # Debug: Print transcription result
            print(f"Transcription result: {user_text}")
            
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
            
            # Generate audio response using ElevenLabs
            elevenlabs_client = ElevenLabs(
                api_key="sk_17b47fb3097fe54ea4d074ffbeee7f5800627e3f0c3a8ed8",  # Defaults to ELEVEN_API_KEY
            )
            elevenlabs_generate = elevenlabs_client.generate
            audio_response = elevenlabs_generate(
                text=response_text,
                voice="Nicole",
                model="eleven_multilingual_v1",
                stream=False  # Change this to False to get the entire audio at once
            )
            
            # Send the entire audio response to the client
            await websocket.send_bytes(audio_response)

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # Log the error
            await websocket.send_text(error_message)
        
        finally:
            # Clean up temporary file
            if os.path.exists("temp_audio.webm"):
                os.remove("temp_audio.webm")

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
                let audioContext = new (window.AudioContext || window.webkitAudioContext)();
                let audioBuffer = [];
                let isPlaying = false;

                const audioConstraints = {
                    audio: {
                        channelCount: 1,
                        sampleRate: 48000,  // Changed to 48kHz
                        echoCancellation: true,
                        noiseSuppression: true,
                    }
                };

                document.getElementById("startRecord").onclick = function() {
                    navigator.mediaDevices.getUserMedia(audioConstraints)
                        .then(stream => {
                            mediaRecorder = new MediaRecorder(stream, {
                                mimeType: 'audio/webm;codecs=opus',
                                audioBitsPerSecond: 48000  // Changed to match 48kHz
                            });
                            mediaRecorder.start();

                            mediaRecorder.addEventListener("dataavailable", event => {
                                audioChunks.push(event.data);
                            });
                        });
                };

                document.getElementById("stopRecord").onclick = function() {
                    mediaRecorder.stop();
                    mediaRecorder.addEventListener("stop", () => {
                        let audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
                        audioChunks = [];
                        let reader = new FileReader();
                        reader.readAsArrayBuffer(audioBlob);
                        reader.onloadend = function() {
                            let buffer = reader.result;
                            ws.send(buffer);
                        }
                    });
                };

                ws.onmessage = async function(event) {
                    if (event.data instanceof Blob) {
                        // Handle audio data
                        const arrayBuffer = await event.data.arrayBuffer();
                        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                        
                        const source = audioContext.createBufferSource();
                        source.buffer = audioBuffer;
                        source.connect(audioContext.destination);
                        source.start();
                    } else {
                        // Handle text data
                        let message = event.data;
                        if (message.startsWith("An error occurred:")) {
                            console.error(message);
                            document.getElementById("output").innerHTML += `<span style="color: red;">${message}</span><br>`;
                        } else {
                            document.getElementById("output").innerHTML += message + "<br>";
                        }
                    }
                };

                // Remove any unused functions or variables
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
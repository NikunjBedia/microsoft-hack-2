from fastapi import APIRouter, WebSocket
import asyncio
import os
import io
from elevenlabs.client import ElevenLabs
from pydantic import BaseModel
from faster_whisper import WhisperModel
#from app.core.agent.core import SuperGraph

#super_graph = SuperGraph()
stt_tts_router = APIRouter()

class GraphRequest(BaseModel):
    user_message: str
    is_initial: bool = False

# Initialize Whisper model
whisper_model = WhisperModel("tiny.en", device='cpu') #TODO: device='cuda' if torch.cuda.is_available() else 'cpu'



@stt_tts_router.websocket("/ws/stt_tts")
async def stt_tts_handler(websocket: WebSocket, request: GraphRequest):
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
            

            # #Get response from graph
            # if request.is_initial:
            #     result = super_graph.start_conversation(user_text)
            # elif super_graph.awaiting_feedback():
            #     result = super_graph.continue_with_human_feedback(user_text)
            # else:
            #     result = super_graph.handle_interruption(user_text)
            
            response_text =" result "#TODO:Check result object dictionary to get the response text
            await websocket.send_text(response_text) # Model response text
            
            # Generate audio response using ElevenLabs
            elevenlabs_client = ElevenLabs(
                api_key=os.environ.get("XI_API_KEY"),  
            )
            elevenlabs_generate = elevenlabs_client.generate
            audio_response = elevenlabs_generate(
                text=response_text,
                voice="Nicole",
                model="eleven_multilingual_v1",
                stream=False  # TODO: Change this to True to stream the audio response
            )
            
            # Send the audio response to the client
            await websocket.send_bytes(audio_response) #TODO: Change this to stream the audio response to decrease latency

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  # Log the error
            await websocket.send_text(error_message)
        
        finally:
            # Clean up temporary file
            if os.path.exists("temp_audio.webm"):
                os.remove("temp_audio.webm")

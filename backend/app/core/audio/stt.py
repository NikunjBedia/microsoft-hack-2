import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import speech_recognition as sr
from io import BytesIO

app = FastAPI()

@app.websocket("/TranscribeStreaming")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_open = True
    stop_audio_stream = False  # Flag to indicate when to stop the audio stream
    audio_queue = asyncio.Queue()  # Queue for incoming audio data

    recognizer = sr.Recognizer()

    async def mic_stream():
        while True:
            indata = await audio_queue.get()
            if stop_audio_stream:
                break
            yield indata

    async def process_audio_stream():
        while True:
            try:
                # Get audio chunk from queue
                audio_chunk = await mic_stream().__anext__()
                
                # Convert byte data to AudioData object
                audio_data = sr.AudioData(BytesIO(audio_chunk).getvalue(), 16000, 2)
                
                # Perform speech recognition on the audio data
                try:
                    transcript = recognizer.recognize_google(audio_data)
                    await websocket.send_text(transcript)
                except sr.UnknownValueError:
                    logging.info("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    logging.error(f"Could not request results from Google Speech Recognition service; {e}")
                
            except StopAsyncIteration:
                break

    try:
        process_task = asyncio.create_task(process_audio_stream())

        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.receive":
                if "bytes" in message:
                    audio_chunk = message["bytes"]
                    await audio_queue.put(audio_chunk)
                elif "text" in message:
                    text_message = message["text"]
                    logging.info(f"Received message: {text_message}")  # Log received message
                    if text_message == "submit_response":
                        logging.info("received: submit_response")
                        stop_audio_stream = True  # Signal to stop the audio stream
                        await process_task  # Wait for the audio stream to finish gracefully
                        break

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        websocket_open = False  # Update WebSocket state
        await websocket.close()

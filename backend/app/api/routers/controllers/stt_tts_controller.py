from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os
import io
from elevenlabs.client import ElevenLabs
from pydantic import BaseModel
from faster_whisper import WhisperModel
#from app.core.agent.core import SuperGraph

#super_graph = SuperGraph()
# from app.core.agent.core import SuperGraph
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from starlette.websockets import WebSocketDisconnect, WebSocketState
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
# super_graph = SuperGraph()
stt_tts_router = APIRouter()

class GraphRequest(BaseModel):
    user_message: str
    is_initial: bool = False

# Initialize Whisper model
whisper_model = WhisperModel("tiny.en", device='cpu') #TODO: device='cuda' if torch.cuda.is_available() else 'cpu'


class Script:
    def __init__(self, script_data: List[Dict]):
        self.script_data = script_data
        self.current_index = 0

    def get_next(self):
        if self.current_index < len(self.script_data):
            item = self.script_data[self.current_index]
            self.current_index += 1
            return item
        return None

class Flow:
    def __init__(self, script_data: List[Dict]):
        self.script = Script(script_data)
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key="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"
        )

    async def script_generation(self):
        while True:
            item = self.script.get_next()
            if item is None:
                break
            yield item
            await asyncio.sleep(1)
    
    async def question_answer(self, query: str):
        prompt = ChatPromptTemplate.from_template(
            "Answer the following question based on the context:\nQuestion: {query}\nContext: {context}\nAnswer:"
        )
        context = str(self.script.script_data)  # Simplification: using entire script as context
        chain = (
            {"query": RunnablePassthrough(), "context": lambda _: context}
            | prompt
            | self.llm
        )
        response = await chain.ainvoke(query)
        return response.content

# Create a single instance of Flow
global_flow = Flow([
    # Your initial script data here
    {
        "index": 0,
        "content": "Hello! Today we're diving into Chapter 5: Conservation of Resources...",
        "pause": "Let's take a moment to think about what resources are."
    },
    {
        "index": 1,
        "content": "What is a resource? A resource is anything that can be used to meet human needs or wants. Resources can be natural, like water and minerals, or man-made, like tools and technology. They can also be renewable, like solar energy, or non-renewable, like fossil fuels. Understanding what resources are is crucial for discussing their conservation.",
        "pause": "Let's take a moment to think about what resources are and how they impact our daily lives. Can you think of some resources you use every day?"
    },
    {
        "index": 2,
        "content": "Conservation of resources is the practice of using resources efficiently and sustainably to ensure their availability for future generations. This involves reducing waste, recycling, and finding alternative sources for non-renewable resources. Conservation is crucial because many of our planet's resources are finite, and their overuse can lead to environmental degradation and economic challenges.",
        "pause": "Consider how you might conserve resources in your daily life. What small changes could you make?"
    },
    {
        "index": 3,
        "content": "There are several key strategies for resource conservation. These include: reducing consumption, reusing items when possible, recycling materials, using renewable resources, and improving efficiency in resource use. For example, using energy-efficient appliances, carpooling, or using reusable shopping bags are all ways to conserve resources in everyday life.",
        "pause": "Let's reflect on these strategies. Which ones do you already practice, and which could you start implementing?"
    }
])

@stt_tts_router.websocket("/ws/stt_tts")
async def stt_tts_handler(websocket: WebSocket):
    await websocket.accept()

    # quesiton answer flow:
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
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text("Transcription: [No speech detected. Please try again.]")
                continue
            
            # Send transcription back to client
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(f"Transcription: {user_text}")
            

            # #Get response from graph
            # if request.is_initial:
            #     result = super_graph.start_conversation(user_text)
            # elif super_graph.awaiting_feedback():
            #     result = super_graph.continue_with_human_feedback(user_text)
            # else:
            #     result = super_graph.handle_interruption(user_text)
            
            response_text =" result "#TODO:Check result object dictionary to get the response text
            # Use the global Flow instance
            result = await global_flow.question_answer(query=user_text)
            
            response_text = result #TODO:Check result object dictionary to get the response text
            print(response_text)
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(response_text) # Model response text
            
            # Generate audio response using ElevenLabs
            elevenlabs_client = ElevenLabs(
                api_key=os.environ.get("XI_API_KEY"),  
            )
            elevenlabs_generate = elevenlabs_client.generate
            audio_response = elevenlabs_generate(
                text=response_text,
                voice="George",
                model="eleven_multilingual_v1",
                stream=True  # TODO: Change this to True to stream the audio response
            )
            
            # Send the audio response to the client
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_bytes(audio_response)


        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)  
            if websocket.client_state == WebSocketState.CONNECTED:# Log the error
                await websocket.send_text(error_message)
        
        finally:
            # Clean up temporary file
            if os.path.exists("temp_audio.webm"):
                os.remove("temp_audio.webm")


@stt_tts_router.websocket("/ws/script_generation")
async def script_generation_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        input = await websocket.receive_text()
        if input == "start_script_generation":
            try:
                # Use the global Flow instance
                async for item in global_flow.script_generation():
                    print(item["content"])
                    elevenlabs_client = ElevenLabs(
                        api_key=os.environ.get("XI_API_KEY"),  
                    )
                    elevenlabs_generate = elevenlabs_client.generate
                    audio_response = elevenlabs_generate(
                        text=item["content"],
                        voice="George",
                        model="eleven_multilingual_v1",
                        stream=True
                    )
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_bytes(audio_response)
            
            except WebSocketDisconnect:
                print("WebSocket disconnected during script generation")
            except Exception as e:
                error_message = f"An error occurred during script generation: {str(e)}"
                print(error_message)
                # Don't try to send the error message, as the connection might be closed
    
    except WebSocketDisconnect:
        print("WebSocket disconnected before script generation started")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    # finally:
    #     print("Script generation WebSocket connection closed")


# Sample HTML for client
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
        <button id="startScriptGeneration">Start Script Generation</button>
        <div id="output"></div>

        <script>
            let ws;
            let scriptWs;
            let mediaRecorder;
            let audioChunks = [];
            let audioContext;
            let audioBuffer = [];
            let isPlaying = false;
            let currentAudioSource = null;

            const audioConstraints = {
                audio: {
                    channelCount: 1,
                    sampleRate: 48000,
                    echoCancellation: true,
                    noiseSuppression: true,
                }
            };

            function initAudioContext() {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioContext.resume();
            }

            function initializeScriptWs() {
                return new Promise((resolve, reject) => {
                    scriptWs = new WebSocket("wss://curio-4dpf.onrender.com/ws/script_generation");
                    scriptWs.onmessage = handleMessage;
                    scriptWs.onopen = function() {
                        console.log("Script WebSocket connected");
                        resolve(scriptWs);
                    };
                    scriptWs.onclose = function(event) {
                        console.log("Script WebSocket closed.");
                    };
                    scriptWs.onerror = function(error) {
                        console.error("Script WebSocket error:", error);
                        reject(error);
                    };
                });
            }

            function initializeWs() {
                audioBuffer = [];
                isPlaying = false;
                
                if (currentAudioSource) {
                    currentAudioSource.stop();
                    currentAudioSource = null;
                }
                
                ws = new WebSocket("wss://curio-4dpf.onrender.com/ws/stt_tts");
                ws.onopen = function() {
                    console.log("Interruption WebSocket connected");
                };
                ws.onmessage = handleMessage;
                ws.onclose = function(event) {
                    console.log("Interruption WebSocket closed.");
                    //initializeScriptWs();  // Switch back to script generation
                };
                ws.onerror = function(error) {
                    console.error("Interruption WebSocket error:", error);
                };
            }

            // Initially start with script generation

            document.getElementById("startRecord").onclick = function() {
                initAudioContext();
                if (scriptWs && scriptWs.readyState === WebSocket.OPEN) {
                    scriptWs.close();
                }
                initializeWs();

                navigator.mediaDevices.getUserMedia(audioConstraints)
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm;codecs=opus',
                            audioBitsPerSecond: 48000
                        });
                        mediaRecorder.start();

                        mediaRecorder.addEventListener("dataavailable", event => {
                            audioChunks.push(event.data);
                        });
                    });
            };

            document.getElementById("stopRecord").onclick = function() {
                if (mediaRecorder && mediaRecorder.state !== "inactive") {
                    mediaRecorder.stop();
                    mediaRecorder.addEventListener("stop", () => {
                        let audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
                        audioChunks = [];
                        let reader = new FileReader();
                        reader.readAsArrayBuffer(audioBlob);
                        reader.onloadend = function() {
                            let buffer = reader.result;
                            sendDataWhenReady(buffer);
                        }
                    });
                }
            };

            function sendDataWhenReady(data) {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(data);
                } else {
                    console.log("WebSocket not ready. Waiting...");
                    setTimeout(() => sendDataWhenReady(data), 100);
                }
            }

            document.getElementById("startScriptGeneration").onclick = function() {
                initAudioContext();
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.close();
                }
                initializeScriptWs().then(ws => ws.send("start_script_generation"));
            };

            function handleMessage(event) {
                if (event.data instanceof Blob) {
                    handleAudioData(event.data);
                } else {
                    handleTextData(event.data);
                }
            }

            async function handleAudioData(data) {
                const arrayBuffer = await data.arrayBuffer();
                audioBuffer.push(arrayBuffer);
                if (!isPlaying) {
                    playNextAudio();
                }
            }

            async function playNextAudio() {
                if (audioBuffer.length > 0) {
                    isPlaying = true;
                    const arrayBuffer = audioBuffer.shift();
                    if (!audioContext) {
                        initAudioContext();
                    }
                    const audioBufferData = await audioContext.decodeAudioData(arrayBuffer);
                    
                    currentAudioSource = audioContext.createBufferSource();
                    currentAudioSource.buffer = audioBufferData;
                    currentAudioSource.connect(audioContext.destination);
                    currentAudioSource.onended = () => {
                        isPlaying = false;
                        currentAudioSource = null;
                        playNextAudio();
                    };
                    currentAudioSource.start();
                } else {
                    console.log("Entering the else statement")
                    isPlaying = false;
                    currentAudioSource = null;
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.close();
                    }
                    initializeScriptWs().then(ws => ws.send("start_script_generation"));  // Switch back to script generation
                }
            }

            function handleTextData(message) {
                if (message.startsWith("An error occurred:")) {
                    console.error(message);
                    document.getElementById("output").innerHTML += `<span style="color: red;">${message}</span><br>`;
                } else {
                    document.getElementById("output").innerHTML += message + "<br>";
                }
            }
        </script>
    </body>
</html>
"""


# Create FastAPI app
# app = FastAPI()

# Add the existing router
# app.include_router(stt_tts_router)

# Add a route for the HTML client
@stt_tts_router.get("/", response_class=HTMLResponse)
async def get_html_client():
    return HTMLResponse(content=html_content, status_code=200)

# Run the app if this script is executed directly
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

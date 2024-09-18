import React, { useState, useEffect, useRef } from 'react';
import { Button } from './button';
import { Play, Pause, Mic } from 'lucide-react';

const VoiceRecorder = () => {
  const [ws, setWs] = useState<any>(null);
  const [scriptWs, setScriptWs] = useState<any>(null);
  const [mediaRecorder, setMediaRecorder] = useState<any>(null);
  const [audioChunks, setAudioChunks] = useState<any>([]);
  const [audioBuffer, setAudioBuffer] = useState<any>([]);
  const [isPlaying, setIsPlaying] = useState<any>(false);
  const [currentAudioSource, setCurrentAudioSource] = useState<any>(null);
  const [audioContext, setAudioContext] = useState<any>(null);
  const outputRef = useRef(null);

  const audioConstraints = {
    audio: {
      channelCount: 1,
      sampleRate: 48000,
      echoCancellation: true,
      noiseSuppression: true,
    },
  };

  // Initialize AudioContext
  const initAudioContext = () => {
    if (!audioContext) {
      const context = new (window.AudioContext || window.Audio)();
      setAudioContext(context);
      context.resume();
    }
  };
  
  // Initialize WebSocket for script generation
  const initializeScriptWs = () => {
    return new Promise((resolve, reject) => {
      const scriptWebSocket = new WebSocket('ws://localhost:8000/ws/script_generation');
      scriptWebSocket.onmessage = handleMessage;
      scriptWebSocket.onopen = () => {
        console.log('Script WebSocket connected');
        resolve(scriptWebSocket);
      };
      scriptWebSocket.onclose = () => {
        console.log('Script WebSocket closed.');
      };
      scriptWebSocket.onerror = (error) => {
        console.error('Script WebSocket error:', error);
        reject(error);
      };
      setScriptWs(scriptWebSocket);
    });
  };

  // Initialize WebSocket for audio interruption
  const initializeWs = () => {
    const webSocket = new WebSocket('ws://localhost:8000/ws/stt_tts');
    setWs(webSocket);
    webSocket.onopen = () => {
      console.log('Interruption WebSocket connected');
    };
    webSocket.onmessage = handleMessage;
    webSocket.onclose = () => {
      console.log('Interruption WebSocket closed.');
    };
    webSocket.onerror = (error) => {
      console.error('Interruption WebSocket error:', error);
    };
  };

  // Handle start recording
  const startRecording = () => {
    initAudioContext();
    if (scriptWs && scriptWs.readyState === WebSocket.OPEN) {
      scriptWs.close();
    }
    initializeWs();

    navigator.mediaDevices.getUserMedia(audioConstraints).then((stream) => {
      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 48000,
      });
      setMediaRecorder(recorder);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          setAudioChunks((prevChunks: any) => [...prevChunks, event.data]);
          console.log('Audio chunk recorded:', event.data.size);
        }
      };

      recorder.start();
    });
  };

  // Handle stop recording
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      mediaRecorder.onstop = () => {
        console.log('Audio chunks before Blob creation:', audioChunks.map((chunk: { size: any; }) => chunk.size));
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        console.log('Created audio blob size:', audioBlob.size);
        if (audioBlob.size > 0) {
          const reader = new FileReader();
          reader.readAsArrayBuffer(audioBlob);
          reader.onloadend = () => {
            const buffer = reader.result;
            sendDataWhenReady(buffer);
          };
        } else {
          console.error('Audio blob is empty');
        }
      };
    }
  };

  // Send data when WebSocket is ready
  const sendDataWhenReady = (data: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      console.log('Sending data size:', data.byteLength);
      ws.send(data);
    } else {
      console.log('WebSocket not ready. Waiting...');
      setTimeout(() => sendDataWhenReady(data), 100);
    }
  };

  // Start script generation WebSocket
  const startScriptGeneration = () => {
    initAudioContext();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
    initializeScriptWs().then((ws:any) => ws.send('start_script_generation'));
  };

  // Handle incoming WebSocket messages
  const handleMessage = async (event:any) => {
    if (event.data instanceof Blob) {
      handleAudioData(event.data);
    } else {
      handleTextData(event.data);
    }
  };

  // Handle audio data
  const handleAudioData = async (data: { arrayBuffer: () => any; }) => {
    const arrayBuffer = await data.arrayBuffer();
    setAudioBuffer((prevBuffer: any) => [...prevBuffer, arrayBuffer]);
    if (!isPlaying) {
      playNextAudio();
    }
  };

  // Play next audio in the buffer
  const playNextAudio = async () => {
    if (audioBuffer.length > 0) {
      setIsPlaying(true);
      const arrayBuffer = audioBuffer.shift();
      if (!audioContext) {
        initAudioContext();
      }
      const audioBufferData = await audioContext.decodeAudioData(arrayBuffer);
      const audioSource = audioContext.createBufferSource();
      audioSource.buffer = audioBufferData;
      audioSource.connect(audioContext.destination);
      setCurrentAudioSource(audioSource);

      audioSource.onended = () => {
        setIsPlaying(false);
        setCurrentAudioSource(null);
        playNextAudio();
      };
      audioSource.start();
    } else {
      setIsPlaying(false);
      setCurrentAudioSource(null);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      initializeScriptWs().then((ws:any) => ws.send('start_script_generation'));
    }
  };

  // Handle text data
  const handleTextData = (message: string) => {
    const output:any = outputRef.current;
    if (message.startsWith('An error occurred:')) {
      console.error(message);
      output.innerHTML += `<span style="color: red;">${message}</span><br>`;
    } else {
      output.innerHTML += `${message}<br>`;
    }
  };

  return (
    // <div>
    //   <Button onClick={startRecording}>Start Recording</Button>
    //   <Button onClick={stopRecording}>Stop Recording</Button>
    //   <Button onClick={startScriptGeneration}>Start Script Generation</Button>
    //   <div id="output" ref={outputRef}></div>
    // </div>
    <>
    <div className="flex justify-center items-center mb-5">
    <button 
      className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 mr-3 ml-3"
      onClick={startRecording}
    >
      <Play size={25} />
    </button>
    <button 
      className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 mr-3 ml-3"
      onClick={stopRecording}
    >
      <Pause size={25} />
    </button>
    <button 
      className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 ml-3 mr-3"
      onClick={startScriptGeneration}
    >
      <Mic size={25} />
    </button>
    </div>
    <div className="flex-grow bg-white w-100 rounded-lg shadow-md p-4 mb-4 overflow-y-auto" id="output" ref={outputRef}></div>
    </>
  );
};

export default VoiceRecorder;

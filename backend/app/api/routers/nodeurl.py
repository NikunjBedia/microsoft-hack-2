import string
from typing import List, cast

from fastapi.responses import StreamingResponse

from threading import Thread
from app.api.routers.chat import _ChatData
from app.utils.json import json_to_model
from app.utils.index import EventObject, get_agent, get_retriever
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.base.llms.types import MessageRole, ChatMessage
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.chat_engine.types import StreamingAgentChatResponse
from pydantic import BaseModel
import logging
import json

class _Message(BaseModel):
    role: MessageRole
    content: str


nodeurl_router = r = APIRouter()

@r.post("")
async def nodeurl(
    message: _Message = Depends(json_to_model(_Message)),
    retreiver = Depends(get_retriever)
):

   if message.role!=MessageRole.USER:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
       )
   node = retreiver.retrieve(message.content) 
   text= ""
   for no in node:
       text+=no.text
   print(node[0].metadata['url'])
   return {"url": text}
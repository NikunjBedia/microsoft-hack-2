import json
import logging
import os
from pydantic import BaseModel
import shutil
from queue import Queue

from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.agent import ReActAgent
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import VectorStoreIndex,SummaryIndex
from llama_index.core.objects import ObjectIndex, SimpleToolNodeMapping
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import FlatReader
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import TextNode
from llama_index.core.settings import Settings
from llama_index.core.indices import load_index_from_storage
from llama_index.core.storage import StorageContext
from llama_index.core.storage.docstore.types import BaseDocumentStore
from llama_index.core.callbacks.schema import EventPayload
from llama_index.core.schema import NodeWithScore
import pymongo

from app.utils.misc import get_max_h_value

from typing import Optional, Dict, Any, List, Tuple

import os


PIPELINE_STORAGE_DIR = "./pipeline_storage"  # directory to cache the ingestion pipeline 
STORAGE_DIR = "./storage"
DATA_DIR = "./data"  # directory containing the documents to index

class EventObject(BaseModel):
    """
    Represents an event from the LlamaIndex callback handler.

    Attributes:
        type (str): The type of the event, e.g. "function_call".
        payload (dict): The payload associated with the event.
    """

    type: str
    payload: dict


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler specifically designed to stream function calls to a queue."""

    def __init__(self, queue: Queue) -> None:
        """Initialize the base callback handler."""
        super().__init__([], [])
        self._queue = queue
        self._counter = 0

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Run when an event starts and return id of event."""
        if event_type == CBEventType.FUNCTION_CALL:
            self._queue.put(
                EventObject(
                    type="function_call",
                    payload={
                        "arguments_str": payload["function_call"],
                        "tool_str": payload["tool"].name,
                    },
                )
            )

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        # print(event_type)
        # print(payload)
        """Run when an event ends."""
        # if event_type == CBEventType.FUNCTION_CALL:
        #     # print(payload)
        #     self._queue.put(
        #         EventObject(
        #             type="function_call_response",
        #             payload={"response": payload["function_call_response"]},
        #         )
        #     )
        if event_type == CBEventType.AGENT_STEP:
            # put LLM response into queue
            self._queue.put(payload["response"])
        elif event_type == CBEventType.RETRIEVE:
            nodes_with_scores: list[NodeWithScore] = payload[EventPayload.NODES]
            nodes_to_return = []
            for node_with_score in nodes_with_scores:
                node = node_with_score.node
                node_meta = node.metadata
                # print(node_meta)
                if 'section_link' in node_meta:
                    nodes_to_return.append({
                        "id": node.id_,
                        "title": get_max_h_value(node_meta)
                                    or node_meta['file_path'],
                        "url": node.metadata['file_path'],
                        "section": node.metadata['section_link'],
                        "summary": node.metadata['summary'],
                    })
            # print(nodes_to_return)
            self._queue.put(
                EventObject(
                    type="nodes_retrieved",
                    payload={
                        "nodes": nodes_to_return
                    }
                )
            )

    @property
    def queue(self) -> Queue:
        """Get the queue of events."""
        return self._queue

    @property
    def counter(self) -> int:
        """Get the counter."""
        return self._counter

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """Run when an overall trace is launched."""
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """Run when an overall trace is exited."""
        pass


def clean_old_persisted_indices(doc_id:str):
    dir_to_delete = f"{STORAGE_DIR}"
    if os.path.exists(dir_to_delete):
        print(f"Deleting dir: {dir_to_delete}")
        shutil.rmtree(dir_to_delete)


async def _build_document_agents(
    storage_dir: str, callback_manager: CallbackManager
) -> Dict:
    """Build document agents."""
    def get_llm():
        llm = Anthropic(model="claude-3-haiku-20240307",
                api_key="apikey")
        return llm
    async def get_store():
        mongo_uri = (
        "apikey"
        )
        mongodb_client = pymongo.MongoClient(mongo_uri)
        store = MongoDBAtlasVectorSearch(mongodb_client, collection_name="collectionSimplCommerce",index_name= "vector_index")
        return store

    def get_unique_docids():
        docids =store._collection.distinct("metadata.ref_doc_id")
        return docids
    def get_nodes(doc_id):
        filter_query = {"metadata.docid": doc_id}

        # Find documents matching the filter query
        documents = store._collection.find(filter_query)
        
        # Convert documents to a list
        document_list = list(documents)
        
        return document_list

    def get_embedding_model():
        model_name = "voyage-02"
        voyage_api_key = os.environ.get("VOYAGE_API_KEY", "apikey")

        embed_model = VoyageEmbedding(
            model_name=model_name, voyage_api_key=voyage_api_key
        )

    llm = get_llm()
    embed_model = get_embedding_model()
    Settings.llm = llm
    Settings.embed_model = embed_model
    # Settings.callback_manager = callback_manager
    # service_context = ServiceContext.from_defaults(llm=llm)

    # Build agents dictionary
    all_nodes =[]
    agents = {}
    store =  await get_store()

    for docid in get_unique_docids():


        if not os.path.exists(f"./{storage_dir}/{docid}"):
            # build vector index
            nodes = get_nodes(docid)
            all_nodes.extend(nodes)
            vector_index = VectorStoreIndex(
                nodes
            )
            vector_index.storage_context.persist(
                persist_dir=f"./{storage_dir}/{docid}"
            )
        else:
            vector_index = load_index_from_storage(
                StorageContext.from_defaults(
                    persist_dir=f"./{storage_dir}/{docid}"
                ),
            )
        summary_index = vector_index   
             # define query engines
        vector_index._callback_manager = callback_manager
        summary_index._callback_manager=callback_manager
        vector_query_engine = vector_index.as_query_engine(llm=llm)
        summary_query_engine = summary_index.as_query_engine(llm=llm)

        agents[docid] = [vector_query_engine,summary_query_engine]


    return agents


def _build_top_agent(
    storage_dir: str, doc_agents: Dict,
    callback_manager: CallbackManager
) -> ReActAgent:
    """Build top-level agent."""
    # define tool for each document agent
    def get_llm():
        llm = Anthropic(model="claude-3-haiku-20240307",
                api_key="apikey")
        return llm
    all_tools = []
    f =open("/Users/chaitanyav/Documents/Project/KTbuddy/app/utils/metadata.json")
    metadatas=json.load(f)
    for doc_id in doc_agents.keys():
        vector_query_engine,summary_query_engine = doc_agents[doc_id]
        query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    "Useful for questions related to specific aspects of "
                    f"  {metadatas[doc_id]['file_name'].split('.')[0]} (e.g. implementation,coding concepts"
                    " design patterns or more)."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=summary_query_engine,
            metadata=ToolMetadata(
                name="summary_tool",
                description=(
                    "Useful for any requests that require a holistic summary of"
                    f" {metadatas[doc_id]['file_name'].split('.')[0]} . For questions about"
                    " more specific sections, please use the vector_tool."
                ),
            ),
        ),
    ]
    tool_mapping = SimpleToolNodeMapping.from_objects(query_engine_tools)
    # if obj_index doesn't already exist
    if not os.path.exists(f"./{storage_dir}/top"):
        storage_context = StorageContext.from_defaults()
        obj_index = ObjectIndex.from_objects(
            query_engine_tools, tool_mapping, VectorStoreIndex, storage_context=storage_context
        )
        storage_context.persist(persist_dir=f"./{storage_dir}/top")
        # TODO: don't access private property

    else:
        # initialize storage context from existing storage
        storage_context = StorageContext.from_defaults(
            persist_dir=f"./{storage_dir}/top"
        )
        index = load_index_from_storage(storage_context)
        obj_index = ObjectIndex(index, tool_mapping)

    top_agent = ReActAgent.from_tools(
        tool_retriever=obj_index.as_retriever(similarity_top_k=7),
        system_prompt=""" \
    You are an agent designed to answer queries about codebase.
    Please always use the tools provided to answer a question. Do not rely on prior knowledge. Pass the provided tools with clear and elaborate queries (e.g. "how async method is being implemented") and then fully utilize their response to answer the original query. When using multiple tools, break the original query into multiple elaborate queries and pass them to the respective tool as input. Be sure to make the inputs long and elaborate to capture entire context of the query. Don't use 1-2 word queries.\

    """,
        verbose=True,
        callback_manager=callback_manager,
        llm=get_llm()
    )

    return top_agent


async def get_agent():
    logger = logging.getLogger("uvicorn")

    # define callback manager with streaming
    queue = Queue()
    handler = StreamingCallbackHandler(queue)
    callback_manager = CallbackManager([handler])


    mongo_uri = (
        "uri"
        )
    mongodb_client = pymongo.MongoClient(mongo_uri)
    store = MongoDBAtlasVectorSearch(mongodb_client, collection_name="collectionSimplCommerce",index_name= "vector_index")
    #storage_context = StorageContext.from_defaults(vector_store=store, callback_manager = callback_manager)
    model_name = "voyage-02"
    voyage_api_key = os.environ.get("VOYAGE_API_KEY", "apikey")

    embed_model = VoyageEmbedding(
            model_name=model_name, voyage_api_key=voyage_api_key
        )
    llm = Anthropic(model="claude-3-haiku-20240307",
                api_key="apikey")
    vectorindex = VectorStoreIndex.from_vector_store(store,embed_model= embed_model)
    vector_query_engine = vectorindex.as_query_engine(llm = llm, streaming=True)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    "Provides information about all code files in the codebase  like Controllers, Services"
                    
                ),
            ),
        )]
    #return vector_query_engine
    top_agent = ReActAgent.from_tools(
        query_engine_tools,
        system_prompt=""" \
        You are an agent designed to answer queries about codebase .
        Ensure responses strictly adhere to available knowledge in the provided tools. Do not fabricate information beyond this scope.
        """,
        verbose=True,
        callback_manager=callback_manager,
        llm=llm
    )

    logger.info(f"Built agent.")
    return vector_query_engine
    #return top_agent

async def get_retriever():
    mongo_uri = ("uri"       )
    mongodb_client = pymongo.MongoClient(mongo_uri)
    store = MongoDBAtlasVectorSearch(mongodb_client, collection_name="collectionSimplCommerce",index_name= "vector_index")
    #storage_context = StorageContext.from_defaults(vector_store=store, callback_manager = callback_manager)
    model_name = "voyage-02"
    voyage_api_key = os.environ.get("VOYAGE_API_KEY", "pa-UAbbSQ84rSuZdSMoMeMmpZcvbLjaZBa08jpCTW8n1x0")

    embed_model = VoyageEmbedding(
            model_name=model_name, voyage_api_key=voyage_api_key
        )
    llm = Anthropic(model="claude-3-haiku-20240307",
                api_key="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")
    vectorindex = VectorStoreIndex.from_vector_store(store,embed_model= embed_model)
    node = vectorindex.as_retriever(llm = llm)
    return node
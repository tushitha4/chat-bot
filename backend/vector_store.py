from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional
from config import settings
import chromadb


class VectorStore:
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai
        self.collection_name = "video_transcripts"
        
        if use_openai:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_base_url
            )
        else:
            # Use free open-source embeddings (BGE)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-en-v1.5",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
    
    def add_transcript(self, video_id: str, transcript: str, metadata: Dict[str, Any]) -> List[str]:
        """Chunk and embed transcript, store in vector DB."""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Create document with metadata
        doc = Document(
            page_content=transcript,
            metadata={
                "video_id": video_id,
                **metadata
            }
        )
        
        # Split document
        chunks = text_splitter.split_documents([doc])
        
        # Add video_id to each chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{video_id}_chunk_{i}"
        
        # Add to vector store
        ids = self.vectorstore.add_documents(chunks)
        return ids
    
    def similarity_search(self, query: str, video_id: Optional[str] = None, k: int = 4) -> List[Document]:
        """Search for similar chunks."""
        filter_dict = {}
        if video_id:
            filter_dict["video_id"] = video_id
        
        return self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None
        )
    
    def similarity_search_with_score(self, query: str, video_id: Optional[str] = None, k: int = 4) -> List[tuple]:
        """Search for similar chunks with scores."""
        filter_dict = {}
        if video_id:
            filter_dict["video_id"] = video_id
        
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None
        )
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents from the vector store."""
        return self.vectorstore.get()

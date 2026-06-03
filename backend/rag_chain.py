from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any, AsyncGenerator
from config import settings
from vector_store import VectorStore


class RAGChain:
    def __init__(self, vector_store: VectorStore, use_openai: bool = False):
        self.vector_store = vector_store
        self.use_openai = use_openai
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        if use_openai:
            self.llm = ChatOpenAI(
                model_name="gpt-4o",
                temperature=0.3,
                streaming=True,
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_base_url
            )
        else:
            # Use a cheaper alternative or local model
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.3,
                streaming=True,
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_base_url
            )
        
        self.chain = self._create_chain()
    
    def _create_chain(self):
        """Create the RAG chain with custom prompt."""
        template = """You are a video analytics expert helping creators understand their content performance. 
You have access to transcripts and metadata from two videos (Video A and Video B).

Use the following pieces of context to answer the question at the end. 
Always cite which video and which chunk you're referencing in your answer.
Format citations as [Video X, Chunk Y] where X is A or B and Y is the chunk number.

Context: {context}

Chat History: {chat_history}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": prompt},
            return_source_documents=True,
            verbose=True
        )
        
        return chain
    
    async def query(self, question: str) -> AsyncGenerator[str, None]:
        """Query the RAG chain with streaming response."""
        # Get relevant documents
        docs = self.vector_store.similarity_search_with_score(question, k=4)
        
        # Format context with citations
        context_parts = []
        for doc, score in docs:
            video_id = doc.metadata.get("video_id", "Unknown")
            chunk_id = doc.metadata.get("chunk_id", "Unknown")
            context_parts.append(
                f"[{video_id}, {chunk_id}] (relevance: {score:.2f}): {doc.page_content}"
            )
        context = "\n\n".join(context_parts)
        
        # Stream response
        async for chunk in self.llm.astream(
            f"Context: {context}\n\nQuestion: {question}"
        ):
            yield chunk.content
    
    def query_sync(self, question: str) -> Dict[str, Any]:
        """Synchronous query for non-streaming use."""
        result = self.chain.invoke({"question": question})
        
        # Format sources
        sources = []
        for doc in result.get("source_documents", []):
            sources.append({
                "video_id": doc.metadata.get("video_id", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", "Unknown"),
                "content": doc.page_content[:200] + "..."
            })
        
        return {
            "answer": result.get("answer", ""),
            "sources": sources,
            "chat_history": self.memory.chat_memory.messages
        }
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()

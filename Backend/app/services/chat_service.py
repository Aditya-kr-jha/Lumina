from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import time
import logging
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.callbacks.manager import get_openai_callback

from app.config import settings
from app.services.vector_store import vector_store_service
from app.models.schemas import ChatResponse, SourceChunk

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat and RAG operations with user isolation."""

    def __init__(self):
        """Initialize chat service with LLM and session message history."""
        self.llm = self._initialize_llm()
        # Store sessions per user: {user_id: {session_id: ChatMessageHistory}}
        self.sessions: Dict[int, Dict[str, ChatMessageHistory]] = {}
        self.vector_store = vector_store_service

    def _initialize_llm(self):
        """Initialize Language Model."""
        try:
            logger.info(f"Initializing LLM: {settings.LLM_MODEL}")
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )
            logger.info("✅ LLM initialized successfully")
            return llm
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise

    def _get_or_create_session(
        self, user_id: int, session_id: Optional[str] = None
    ) -> Tuple[str, ChatMessageHistory]:
        """Return an existing or new chat message history session for a user."""
        # Initialize user's session dict if not exists
        if user_id not in self.sessions:
            self.sessions[user_id] = {}

        # Check if session exists for this user
        if session_id and session_id in self.sessions[user_id]:
            return session_id, self.sessions[user_id][session_id]

        # Create new session for this user
        new_session_id = session_id or str(uuid.uuid4())
        history = ChatMessageHistory()
        self.sessions[user_id][new_session_id] = history
        logger.info(f"Created new session {new_session_id} for user {user_id}")
        return new_session_id, history

    def _build_chat_prompt(self) -> ChatPromptTemplate:
        """Prompt used by the document-combining chain."""
        system_text = (
            "You are an intelligent PDF assistant. Use the provided context and chat history to answer the user's question.\n\n"
            "IMPORTANT RULES:\n"
            "1. Answer ONLY based on the provided context below\n"
            "2. Always provide a direct answer to the question\n"
            "3. If the exact answer isn't in the context, provide the most relevant information available\n"
            "4. Be specific, concise, and helpful\n"
            "5. If truly no relevant information exists, clearly state that\n\n"
            "Context:\n{context}"
        )
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_text),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

    def _process_sources(
        self, source_documents: List[Document], query: str
    ) -> List[SourceChunk]:
        """Convert retrieved documents to SourceChunk objects."""
        sources: List[SourceChunk] = []
        for i, doc in enumerate(source_documents):
            metadata = doc.metadata or {}
            similarity_score = metadata.get("score", 0.0)
            source_chunk = SourceChunk(
                content=doc.page_content,
                page_number=metadata.get("page_number", 0),
                chunk_id=metadata.get("source", f"chunk_{i}"),
                similarity_score=similarity_score,
                metadata={
                    "word_count": metadata.get("word_count", 0),
                    "char_count": metadata.get("char_count", 0),
                    "chunk_index": metadata.get("chunk_index", i),
                },
            )
            sources.append(source_chunk)
        sources.sort(key=lambda x: x.page_number)
        return sources

    def _generate_direct_answer(
        self, question: str, context_docs: List[Document]
    ) -> str:
        """Generate answer directly from LLM when chain fails."""
        if not context_docs:
            return "I couldn't find relevant information in the document to answer your question."

        # Combine context from retrieved documents
        context_text = "\n\n---\n\n".join(
            [doc.page_content for doc in context_docs[:4]]
        )

        # Create a direct prompt
        direct_prompt = f"""Based on the following context from a PDF document, answer the user's question concisely and accurately.

Context:
{context_text}

Question: {question}

Instructions:
- Provide a direct, helpful answer based on the context
- If the context contains relevant information, extract and summarize it
- Be specific with numbers, names, and details when available
- If the answer is not in the context, say so clearly

Answer:"""

        try:
            response = self.llm.invoke(direct_prompt)
            answer = (
                response.content.strip()
                if hasattr(response, "content")
                else str(response).strip()
            )
            return (
                answer
                if answer
                else "I couldn't generate a proper answer from the available information."
            )
        except Exception as e:
            logger.error(f"Error in direct answer generation: {e}")
            return f"I encountered an error while processing your question: {str(e)}"

    def query(
        self,
        question: str,
        document_id: str,
        user_id: int,
        session_id: Optional[str] = None,
        include_sources: bool = True,
        top_k: int = 4,
    ) -> ChatResponse:
        """Process user query using RAG with user isolation."""
        start_time = time.time()
        answer = ""
        source_documents: List[Document] = []

        try:
            logger.info(
                f"Processing query for user {user_id}, document {document_id}: {question}"
            )

            # Verify user owns document
            chunks = self.vector_store.get_document_chunks(document_id, user_id)
            if not chunks:
                raise ValueError("Document not found or access denied")

            # Get or create session for this user
            session_id, history = self._get_or_create_session(user_id, session_id)

            # Perform similarity search with user filter
            results_with_scores = self.vector_store.similarity_search(
                query=question,
                user_id=user_id,
                document_id=document_id,
                k=top_k,
            )

            # Extract documents from results
            source_documents = [doc for doc, score in results_with_scores]
            logger.info(
                f"Retrieved {len(source_documents)} documents for user {user_id}"
            )

            if not source_documents:
                answer = "I couldn't find relevant information in the document to answer your question."
            else:
                # Build prompt
                prompt = self._build_chat_prompt()

                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)

                # Build the RAG chain
                rag_chain = (
                    {
                        "context": lambda x: format_docs(source_documents),
                        "input": lambda x: x["input"],
                        "chat_history": lambda x: history.messages,
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )

                # Invoke chain with callback
                logger.info("Invoking RAG chain...")
                with get_openai_callback() as cb:
                    answer = rag_chain.invoke({"input": question})

                    logger.info(f"Chain result type: {type(answer)}")
                    logger.info(f"Answer length: {len(answer) if answer else 0}")

                    if getattr(settings, "DEBUG", False):
                        logger.info(
                            f"Tokens - Total: {cb.total_tokens}, "
                            f"Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens}"
                        )

                # Ensure answer is a string
                answer = str(answer).strip()
                logger.info(f"Chain generated answer: {answer[:200]}...")

                # Add to history manually
                history.add_user_message(question)
                history.add_ai_message(answer)

            # Fallback: Generate direct answer if chain returned empty
            if not answer and source_documents:
                logger.warning("Empty answer from chain, using direct generation")
                answer = self._generate_direct_answer(question, source_documents)
            elif not answer:
                answer = "I couldn't find relevant information in the document."

            # Process sources
            sources = (
                self._process_sources(source_documents, question)
                if include_sources
                else []
            )

            processing_time = time.time() - start_time
            logger.info(
                f"✅ Query processed for user {user_id} in {processing_time:.2f}s"
            )

            return ChatResponse(
                answer=answer,
                sources=sources,
                session_id=session_id,
                document_id=document_id,
                question=question,
                timestamp=datetime.now(timezone.utc),
                processing_time=processing_time,
            )

        except ValueError as ve:
            # Access denied
            logger.warning(f"Access denied for user {user_id}: {str(ve)}")
            return ChatResponse(
                answer=f"Access denied: {str(ve)}",
                sources=[],
                session_id=session_id or str(uuid.uuid4()),
                document_id=document_id,
                question=question,
                timestamp=datetime.now(timezone.utc),
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)

            # Attempt fallback even on error if we have sources
            if source_documents:
                try:
                    logger.warning("Chain failed, using fallback generation")
                    answer = self._generate_direct_answer(question, source_documents)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    answer = f"I encountered an error: {str(e)}"
            else:
                answer = f"I encountered an error processing your question: {str(e)}"

            return ChatResponse(
                answer=answer,
                sources=(
                    self._process_sources(source_documents, question)
                    if source_documents
                    else []
                ),
                session_id=session_id or str(uuid.uuid4()),
                document_id=document_id,
                question=question,
                timestamp=datetime.now(timezone.utc),
                processing_time=time.time() - start_time,
            )

    def simple_query(
        self, question: str, document_id: str, user_id: int, top_k: int = 4
    ) -> str:
        """Stateless query without conversation history (user-isolated)."""
        try:
            logger.info(
                f"Simple query for user {user_id}, document {document_id}: {question}"
            )

            # Verify user owns document
            chunks = self.vector_store.get_document_chunks(document_id, user_id)
            if not chunks:
                return "Document not found or access denied."

            # Search with user filter
            results_with_scores = self.vector_store.similarity_search(
                query=question,
                user_id=user_id,
                document_id=document_id,
                k=top_k,
            )

            docs = [doc for doc, score in results_with_scores]

            if not docs:
                return "I couldn't find relevant information in the document."

            # Use direct generation for simple queries
            answer = self._generate_direct_answer(question, docs)
            logger.info(f"Simple query answered for user {user_id}: {answer[:120]}...")
            return answer

        except Exception as e:
            logger.error(f"Error in simple query: {str(e)}", exc_info=True)
            return f"Error processing your question: {str(e)}"

    def get_session_history(
        self, session_id: str, user_id: int
    ) -> List[Dict[str, str]]:
        """Get conversation history for a user's session."""
        if user_id not in self.sessions or session_id not in self.sessions[user_id]:
            logger.warning(f"Session {session_id} not found for user {user_id}")
            return []

        messages = self.sessions[user_id][session_id].messages
        history: List[Dict[str, str]] = []
        buf_q = None
        for m in messages:
            role_content = getattr(m, "content", "")
            if m.type == "human":
                buf_q = role_content
            elif m.type == "ai" and buf_q is not None:
                history.append({"question": buf_q, "answer": role_content})
                buf_q = None
        return history

    def clear_session(self, session_id: str, user_id: int) -> bool:
        """Clear a user's conversation session."""
        if user_id in self.sessions and session_id in self.sessions[user_id]:
            del self.sessions[user_id][session_id]
            logger.info(f"Cleared session {session_id} for user {user_id}")
            return True
        return False

    def get_active_sessions(self, user_id: int) -> List[str]:
        """Get list of active session IDs for a user."""
        if user_id not in self.sessions:
            return []
        return list(self.sessions[user_id].keys())

    def get_user_session_count(self, user_id: int) -> int:
        """Get number of active sessions for a user."""
        if user_id not in self.sessions:
            return 0
        return len(self.sessions[user_id])

    def clear_all_user_sessions(self, user_id: int) -> int:
        """Clear all sessions for a user."""
        if user_id not in self.sessions:
            return 0
        count = len(self.sessions[user_id])
        del self.sessions[user_id]
        logger.info(f"Cleared {count} sessions for user {user_id}")
        return count


chat_service = ChatService()

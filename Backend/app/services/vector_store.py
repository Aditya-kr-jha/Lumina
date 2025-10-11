import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing vector store operations"""

    def __init__(self):
        """Initialize vector store with ChromaDB"""
        self.persist_directory = str(settings.CHROMA_PERSIST_DIRECTORY)
        self.collection_name = settings.COLLECTION_NAME
        self.embeddings = self._initialize_embeddings()
        self.client = None
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_embeddings(self) -> Embeddings:
        """Initialize embedding model"""
        try:
            logger.info(f"Initializing embeddings: {settings.EMBEDDING_MODEL}")

            if (
                "openai" in settings.EMBEDDING_MODEL.lower()
                or "text-embedding" in settings.EMBEDDING_MODEL.lower()
            ):
                return OpenAIEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                )
            else:
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise

    def _initialize_vectorstore(self):
        """Initialize ChromaDB vector store"""
        try:
            logger.info(f"Initializing ChromaDB at: {self.persist_directory}")

            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

            # Use PersistentClient for on-disk persistence (no explicit .persist() needed)
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
            )

            # When passing a client, do not pass persist_directory to Chroma
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )

            logger.info("✅ Vector store initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(
        self, documents: List[Document], document_id: str, user_id: int
    ) -> Dict[str, Any]:
        """Add document chunks to vector store"""
        try:
            logger.info(f"Adding {len(documents)} chunks for document {document_id}")

            for doc in documents:
                doc.metadata["document_id"] = document_id
                doc.metadata["user_id"] = user_id

            # Chroma + PersistentClient persists automatically
            ids = self.vectorstore.add_documents(documents)

            logger.info(f"✅ Added {len(ids)} chunks to vector store")

            return {
                "success": True,
                "document_id": document_id,
                "user_id": user_id,
                "chunks_added": len(ids),
                "chunk_ids": ids,
            }

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return {"success": False, "error": str(e)}

    def similarity_search(
        self,
        query: str,
        user_id: int,
        document_id: Optional[str] = None,
        k: int = 4,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[Document, float]]:
        """Perform similarity search"""
        try:
            logger.info(f"Searching for: '{query[:50]}...' (k={k})")

            if document_id:
                filter_dict = {
                    "$and": [{"user_id": user_id}, {"document_id": document_id}]
                }
            else:
                filter_dict = {"user_id": user_id}  # Only user's documents

            results = self.vectorstore.similarity_search_with_relevance_scores(
                query=query, k=k, filter=filter_dict
            )

            if score_threshold is not None:
                results = [
                    (doc, score) for doc, score in results if score >= score_threshold
                ]

            logger.info(f"Found {len(results)} relevant chunks")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        user_id: int,
        document_id: Optional[str] = None,
        k: int = 4,
    ) -> List[Document]:
        """Search by embedding vector with user isolation"""
        try:
            # Build filter with user_id
            if document_id:
                filter_dict = {
                    "$and": [{"user_id": user_id}, {"document_id": document_id}]
                }
            else:
                filter_dict = {"user_id": user_id}

            results = self.vectorstore.similarity_search_by_vector(
                embedding=embedding, k=k, filter=filter_dict
            )

            return results

        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []

    def delete_document(self, document_id: str, user_id: int) -> Dict[str, Any]:
        """Delete all chunks for a document"""
        try:
            logger.info(f"Deleting chunks for document: {document_id}")

            collection = self.client.get_collection(self.collection_name)

            results = collection.get(
                where={
                    "$and": [
                        {"document_id": document_id},
                        {"user_id": user_id},  # ← OWNERSHIP VERIFICATION
                    ]
                },
                include=["metadatas"],
            )
            chunk_ids = results.get("ids", [])

            if chunk_ids:
                collection.delete(ids=chunk_ids)
                logger.info(f"✅ Deleted {len(chunk_ids)} chunks")
            else:
                logger.warning(f"No chunks found for document {document_id}")

            return {
                "success": True,
                "document_id": document_id,
                "chunks_deleted": len(chunk_ids),
            }

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_document_chunks(self, document_id: str, user_id: int) -> List[Document]:
        """Retrieve all chunks for a document"""
        try:
            collection = self.client.get_collection(self.collection_name)

            results = collection.get(
                where={
                    "$and": [
                        {"document_id": document_id},
                        {"user_id": user_id},  # ← USER FILTER
                    ]
                },
                include=["documents", "metadatas"],
            )

            documents = []
            for i, doc_text in enumerate(results.get("documents", [])):
                metadata = (
                    results["metadatas"][i] if i < len(results["metadatas"]) else {}
                )
                documents.append(Document(page_content=doc_text, metadata=metadata))

            logger.info(f"Retrieved {len(documents)} chunks for document {document_id}")
            return documents

        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            return []

    def get_user_documents(self, user_id: int) -> List[str]:
        """Get all document IDs for a user"""
        try:
            collection = self.client.get_collection(self.collection_name)

            results = collection.get(where={"user_id": user_id}, include=["metadatas"])

            document_ids = set()
            for metadata in results.get("metadatas", []):
                if "document_id" in metadata:
                    document_ids.add(metadata["document_id"])

            logger.info(f"Found {len(document_ids)} documents for user {user_id}")
            return list(document_ids)

        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()

            results = collection.get(include=["metadatas"])
            document_ids = set()
            for metadata in results.get("metadatas", []):
                if "document_id" in metadata:
                    document_ids.add(metadata["document_id"])

            return {
                "total_chunks": count,
                "unique_documents": len(document_ids),
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory,
            }

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"total_chunks": 0, "unique_documents": 0, "error": str(e)}

    def reset_collection(self) -> Dict[str, Any]:
        """Reset (delete) the entire collection"""
        try:
            logger.warning("⚠️ Resetting vector store collection")

            self.client.delete_collection(self.collection_name)

            self._initialize_vectorstore()

            logger.info("✅ Collection reset successfully")
            return {"success": True, "message": "Collection reset"}

        except Exception as e:
            logger.error(f"Error resetting collection: {str(e)}")
            return {"success": False, "error": str(e)}

    def as_retriever(self, **kwargs):
        """Get LangChain retriever interface"""
        return self.vectorstore.as_retriever(**kwargs)


# Create singleton instance
vector_store_service = VectorStoreService()

import fitz
import io
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
import hashlib

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF document processing class - supports both file and bytes input"""

    def __init__(self):
        self.supported_formats = [".pdf"]

    # ============================================================================
    # File-based methods (legacy support)
    # ============================================================================

    def validate_pdf(self, file_path: Path) -> Tuple[bool, str]:
        """Validate PDF file from path"""
        if not file_path.exists():
            return False, "File does not exist"

        if file_path.suffix.lower() not in self.supported_formats:
            return False, f"Unsupported format. Supported: {self.supported_formats}"

        try:
            with fitz.open(file_path) as doc:
                if len(doc) == 0:
                    return False, "PDF has no pages"
            return True, ""
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"

    def extract_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF file"""
        logger.info(f"Extracting text from: {file_path}")

        try:
            with fitz.open(file_path) as doc:
                pages_content = self._extract_pages_from_doc(doc)

            logger.info(f"Extracted {len(pages_content)} pages")
            return pages_content

        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata from file"""
        try:
            with fitz.open(file_path) as doc:
                return self._extract_metadata_from_doc(
                    doc, file_path.stat().st_size, file_path.name
                )

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                "pages": 0,
                "file_size": file_path.stat().st_size,
                "filename": file_path.name,
            }

    def generate_document_id(self, file_path: Path, user_id: int) -> str:
        """Generate unique document ID from file"""
        hasher = hashlib.sha256()
        hasher.update(str(user_id).encode("utf-8"))

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()[:16]

    # ============================================================================
    # Bytes-based methods (new - for in-memory processing)
    # ============================================================================

    def validate_pdf_bytes(self, file_content: bytes) -> Tuple[bool, str]:
        """
        Validate PDF from bytes

        Args:
            file_content: PDF file content as bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                if len(doc) == 0:
                    return False, "PDF has no pages"
            return True, ""
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"

    def extract_text_from_bytes(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Extract text from PDF bytes with metadata

        Args:
            file_content: PDF file content as bytes

        Returns:
            List of dictionaries containing page text and metadata
        """
        logger.info("Extracting text from PDF bytes")

        try:
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                pages_content = self._extract_pages_from_doc(doc)

            logger.info(f"Extracted {len(pages_content)} pages from bytes")
            return pages_content

        except Exception as e:
            logger.error(f"Error extracting text from bytes: {str(e)}")
            raise

    def extract_metadata_from_bytes(
        self, file_content: bytes, filename: str = "document.pdf"
    ) -> Dict[str, Any]:
        """
        Extract PDF metadata from bytes

        Args:
            file_content: PDF file content as bytes
            filename: Original filename (optional)

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                return self._extract_metadata_from_doc(doc, len(file_content), filename)

        except Exception as e:
            logger.error(f"Error extracting metadata from bytes: {str(e)}")
            return {
                "pages": 0,
                "file_size": len(file_content),
                "filename": filename,
            }

    def generate_document_id_from_bytes(self, file_content: bytes, user_id: int) -> str:
        """
        Generate unique document ID from bytes

        Args:
            file_content: PDF file content as bytes
            user_id: ID of the user uploading the document

        Returns:
            Unique document ID (deterministic per user + file combination)
        """
        hasher = hashlib.sha256()
        hasher.update(str(user_id).encode("utf-8"))
        hasher.update(file_content)
        return hasher.hexdigest()[:16]

    # ============================================================================
    # Internal helper methods (shared by file and bytes methods)
    # ============================================================================

    def _extract_pages_from_doc(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract page content from opened PyMuPDF document

        Args:
            doc: Opened fitz.Document

        Returns:
            List of dictionaries containing page text and metadata
        """
        pages_content = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            blocks = page.get_text("blocks")

            page_data = {
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text),
                "word_count": len(text.split()),
                "has_images": len(page.get_images()) > 0,
                "blocks": len(blocks),
                "metadata": {
                    "width": page.rect.width,
                    "height": page.rect.height,
                },
            }

            pages_content.append(page_data)

        return pages_content

    def _extract_metadata_from_doc(
        self, doc: fitz.Document, file_size: int, filename: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from opened PyMuPDF document

        Args:
            doc: Opened fitz.Document
            file_size: Size of the PDF file in bytes
            filename: Name of the file

        Returns:
            Dictionary containing PDF metadata
        """
        metadata = doc.metadata

        info = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "pages": len(doc),
            "file_size": file_size,
            "filename": filename,
        }

        return info

    # ============================================================================
    # Optional: Image extraction (file-based only)
    # ============================================================================

    def extract_images(self, file_path: Path, output_dir: Path) -> List[str]:
        """
        Extract images from PDF (optional feature)

        Args:
            file_path: Path to PDF file
            output_dir: Directory to save extracted images

        Returns:
            List of paths to extracted images
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            with fitz.open(file_path) as doc:
                image_paths = []

                for page_num, page in enumerate(doc):
                    images = page.get_images()

                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        image_name = (
                            f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                        )
                        image_path = output_dir / image_name

                        image_path.write_bytes(image_bytes)
                        image_paths.append(str(image_path))

            logger.info(f"Extracted {len(image_paths)} images")
            return image_paths

        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
            return []


# Singleton instance
pdf_processor = PDFProcessor()

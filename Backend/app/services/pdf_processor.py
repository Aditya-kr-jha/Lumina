import fitz
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
import hashlib
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF document processing class"""

    def __init__(self):
        self.supported_formats = [".pdf"]

    def validate_pdf(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (is_valid, error_message)
        """
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
        """
        Extract text from PDF with metadata

        Args:
            file_path: Path to PDF file

        Returns:
            List of dictionaries containing page text and metadata
        """
        logger.info(f"Extracting text from: {file_path}")

        try:
            with fitz.open(file_path) as doc:
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

            logger.info(f"Extracted {len(pages_content)} pages")
            return pages_content

        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract PDF metadata

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with fitz.open(file_path) as doc:
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
                    "file_size": file_path.stat().st_size,
                    "filename": file_path.name,
                }

            return info

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                "pages": 0,
                "file_size": file_path.stat().st_size,
                "filename": file_path.name,
            }

    def generate_document_id(self, file_path: Path, user_id: int) -> str:
        """
        Generate unique document ID based on file content AND user ID

        This ensures document IDs are user-specific, preventing privacy leaks.
        Same file uploaded by different users will have different IDs.

        Args:
            file_path: Path to PDF file
            user_id: ID of the user uploading the document

        Returns:
            Unique document ID (deterministic per user + file combination)
        """
        hasher = hashlib.sha256()

        hasher.update(str(user_id).encode("utf-8"))

        # Then hash file content
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        # Return hash: same file + same user = same ID
        # Different users uploading same file = different IDs
        return hasher.hexdigest()[:16]

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


pdf_processor = PDFProcessor()

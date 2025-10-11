from pathlib import Path
import sys

# Try to import the pdf_processor instance from your class file.
try:
    from app.services.pdf_processor import pdf_processor
except ImportError:
    print(
        "❌ ERROR: Make sure your PDFProcessor class is saved in 'pdf_processor_class.py'"
    )
    sys.exit(1)

INPUT_PDF_PATH = "test_pdf_1.pdf"


IMAGE_OUTPUT_DIR = "extracted_images"

# --- END OF CONFIGURATION ---


def main():
    """Main function to process the specified PDF."""
    pdf_path = Path(INPUT_PDF_PATH)
    output_dir = Path(IMAGE_OUTPUT_DIR)

    # --- 1. Check if the PDF file exists ---
    if not pdf_path.is_file():
        print(f"\n❌ ERROR: The file '{pdf_path}' was not found.")
        print(
            "Please update the INPUT_PDF_PATH variable in the script with the correct path."
        )
        return

    print(f"--- Processing PDF: {pdf_path} ---")

    # --- 2. Extract and display metadata ---
    print("\n[1] Extracting Metadata...")
    metadata = pdf_processor.extract_metadata(pdf_path)
    if metadata and metadata.get("pages") > 0:
        print("✅ Metadata Extracted:")
        for key, value in metadata.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ Could not extract metadata or PDF is invalid.")
        return

    # --- 3. Extract and display text content ---
    print("\n[2] Extracting Text Content...")
    pages_content = pdf_processor.extract_text(pdf_path)
    if pages_content:
        print(f"✅ Extracted content from {len(pages_content)} pages.")
        for page in pages_content:
            # Show a snippet of text to avoid flooding the terminal
            text_snippet = page["text"].strip().replace("\n", " ")
            if len(text_snippet) > 80:
                text_snippet = text_snippet[:80] + "..."

            print(
                f"  - Page {page['page_number']} ({page['word_count']} words): \"{text_snippet}\""
            )
    else:
        print("❌ Could not extract text.")

    # --- 4. Extract images ---
    print("\n[3] Extracting Images...")
    print(f"Images will be saved to the '{output_dir}' folder.")

    # Create the output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted_paths = pdf_processor.extract_images(pdf_path, output_dir)
    if extracted_paths:
        print(f"✅ Success! Extracted {len(extracted_paths)} images.")
        print(
            f"\n==> Go check the '{output_dir}' folder to see your extracted image files. <=="
        )
    else:
        print("✅ Finished. No images were found in the PDF.")


if __name__ == "__main__":
    # Check if the user has changed the default path
    if "path/to/your/document.pdf" in INPUT_PDF_PATH:
        print("👋 Welcome! Please edit the 'run_processor.py' file first.")
        print("Set the INPUT_PDF_PATH variable to the path of your PDF file.")
    else:
        main()

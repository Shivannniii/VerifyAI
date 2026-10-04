def extract_text_from_pdf(contents: bytes) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise ValueError("PyMuPDF is not installed. Run pip install -r requirements.txt") from exc
    try:
        doc = fitz.open(stream=contents, filetype="pdf")
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
        return text
    except Exception as exc:
        raise ValueError(f"Could not read the PDF: {exc}") from exc

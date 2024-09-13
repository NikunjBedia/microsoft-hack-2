import fitz  # PyMuPDF
from langchain.schema import Document
from io import BytesIO

class PdfParser:
    def __init__(self):
        pass

    def process_pdf_stream(self, pdf_stream):
        docs = []
        current_headings = []

        # Open the PDF from the byte stream
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")

        # Collect all spans with their font sizes and boldness
        spans = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            spans.append({
                                "text": span["text"],
                                "font_size": round(span["size"], 1),
                                "bold": span["flags"] & 2**1,
                                "page_num": page_num + 1
                            })

        # Sort spans by font size (descending) and boldness (descending)
        spans.sort(key=lambda x: (-x["font_size"], -x["bold"]))

        # Determine heading levels based on sorted spans
        heading_levels = {}
        current_level = 1
        for span in spans:
            if span["bold"]:
                if span["font_size"] not in heading_levels:
                    heading_levels[span["font_size"]] = current_level
                    current_level += 1

        # Process spans to create documents with metadata
        for span in spans:
            if span["font_size"] in heading_levels:
                heading_level = heading_levels[span["font_size"]]
                current_headings = current_headings[:heading_level - 1] + [span["text"]]
                heading_path = " > ".join(current_headings)
                docs.append(Document(
                    page_content=span["text"],
                    metadata={
                        "page": span["page_num"],
                        "type": "heading",
                        "heading_level": heading_level,
                        "current_heading": heading_path,
                        "font_size": span["font_size"],
                        "bold": span["bold"]
                    }
                ))
            else:
                heading_path = " > ".join(current_headings)
                docs.append(Document(
                    page_content=span["text"],
                    metadata={
                        "page": span["page_num"],
                        "type": "content",
                        "heading_level": None,
                        "current_heading": heading_path,
                        "font_size": span["font_size"],
                        "bold": span["bold"]
                    }
                ))

        return docs
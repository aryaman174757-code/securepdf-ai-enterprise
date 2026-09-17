import io
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
from PIL import Image
import docx
import openpyxl
from pptx import Presentation
from pptx.util import Inches

class ConversionService:
    """
    Universal Document Conversion Engine.
    Converts between PDF and DOCX, Excel, PPTX, HTML, Markdown, and Images.
    """

    @staticmethod
    def pdf_to_images(pdf_buffer: bytes, format: str = "PNG", dpi: int = 200) -> List[bytes]:
        """Convert each page of a PDF into an image buffer (PNG, JPEG, WEBP)."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        image_buffers: List[bytes] = []

        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            out_format = format.upper()
            if out_format == "JPG":
                out_format = "JPEG"
            
            img_bytes = pix.tobytes(out_format.lower())
            image_buffers.append(img_bytes)

        doc.close()
        return image_buffers

    @staticmethod
    def images_to_pdf(image_buffers: List[bytes]) -> bytes:
        """Combine multiple image streams into a unified PDF document."""
        doc = fitz.open()
        for img_bytes in image_buffers:
            img = fitz.open(stream=img_bytes, filetype="image")
            rect = img[0].rect
            pdf_bytes = img.convert_to_pdf()
            img.close()
            
            img_pdf = fitz.open("pdf", pdf_bytes)
            page = doc.new_page(width=rect.width, height=rect.height)
            page.show_pdf_page(rect, img_pdf, 0)
            img_pdf.close()

        output = doc.tobytes(garbage=4, deflate=True)
        doc.close()
        return output

    @staticmethod
    def pdf_to_docx(pdf_buffer: bytes) -> bytes:
        """Convert PDF text and structure into a formatted Word (.docx) document."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        word_doc = docx.Document()

        for page in doc:
            text = page.get_text("text")
            for paragraph in text.split("\n\n"):
                if paragraph.strip():
                    word_doc.add_paragraph(paragraph.strip())

        output_stream = io.BytesIO()
        word_doc.save(output_stream)
        doc.close()
        return output_stream.getvalue()

    @staticmethod
    def pdf_to_excel(pdf_buffer: bytes) -> bytes:
        """Extract structured tables and tabular text from PDF into an Excel spreadsheet."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Extracted PDF Data"
        
        current_row = 1
        for page_num, page in enumerate(doc):
            ws.cell(row=current_row, column=1, value=f"--- Page {page_num + 1} ---")
            current_row += 1
            
            # Extract tab-separated or table formatted blocks
            blocks = page.get_text("blocks")
            for b in blocks:
                text = b[4].strip()
                lines = text.split("\n")
                for line in lines:
                    items = [it.strip() for it in line.split("  ") if it.strip()]
                    for col_idx, item in enumerate(items):
                        ws.cell(row=current_row, column=col_idx + 1, value=item)
                    current_row += 1

        output_stream = io.BytesIO()
        wb.save(output_stream)
        doc.close()
        return output_stream.getvalue()

    @staticmethod
    def pdf_to_pptx(pdf_buffer: bytes) -> bytes:
        """Convert PDF pages into Presentation slides with rendered graphics."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        prs = Presentation()
        # Set 16:9 widescreen or default slide layout
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        blank_slide_layout = prs.slide_layouts[6]

        for page in doc:
            slide = prs.slides.add_slide(blank_slide_layout)
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            
            img_stream = io.BytesIO(img_bytes)
            slide.shapes.add_picture(img_stream, Inches(0.5), Inches(0.5), width=Inches(9))

        output_stream = io.BytesIO()
        prs.save(output_stream)
        doc.close()
        return output_stream.getvalue()

    @staticmethod
    def pdf_to_markdown(pdf_buffer: bytes) -> str:
        """Convert PDF document into structured Markdown."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        md_lines = []

        for page_idx, page in enumerate(doc):
            md_lines.append(f"\n## Page {page_idx + 1}\n")
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        line_text = "".join([span["text"] for span in l["spans"]]).strip()
                        # Detect heading based on font size
                        if l["spans"] and l["spans"][0]["size"] > 14:
                            md_lines.append(f"\n### {line_text}\n")
                        else:
                            md_lines.append(line_text)

        doc.close()
        return "\n".join(md_lines)

    @staticmethod
    def pdf_to_html(pdf_buffer: bytes) -> str:
        """Export PDF pages directly as formatted semantic HTML."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        html_pages = []
        for page in doc:
            html_pages.append(page.get_text("html"))
        doc.close()
        return "\n<hr/>\n".join(html_pages)

    @staticmethod
    def extract_assets(pdf_buffer: bytes) -> Dict[str, Any]:
        """Extract all embedded images, raw text, and tables."""
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        images = []
        full_text = []

        for page_idx, page in enumerate(doc):
            full_text.append(f"--- Page {page_idx + 1} ---\n" + page.get_text("text"))
            for img_idx, img in enumerate(page.get_images()):
                xref = img[0]
                base_img = doc.extract_image(xref)
                if base_img:
                    images.append({
                        "page": page_idx + 1,
                        "index": img_idx,
                        "format": base_img["ext"],
                        "size_bytes": len(base_img["image"])
                    })

        doc.close()
        return {
            "total_images_extracted": len(images),
            "images": images,
            "text_preview": "\n".join(full_text)[:2000]
        }

converter_service = ConversionService()

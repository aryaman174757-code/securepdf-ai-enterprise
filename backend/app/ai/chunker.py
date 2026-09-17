import fitz  # PyMuPDF
from typing import List, Dict, Any

class DocumentChunk:
    def __init__(self, chunk_index: int, page_number: int, content: str, bbox: List[float], chunk_type: str = "paragraph"):
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.content = content
        self.bbox = bbox  # [x0, y0, x1, y1]
        self.chunk_type = chunk_type  # header, paragraph, table

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "content": self.content,
            "bbox": self.bbox,
            "chunk_type": self.chunk_type
        }


class LayoutAwareChunker:
    """
    Layout & Hierarchy-Aware Document Chunker.
    Preserves document structure, headings, table boundaries, and page coordinates.
    """

    @classmethod
    def chunk_pdf(cls, pdf_buffer: bytes, max_chars_per_chunk: int = 800) -> List[DocumentChunk]:
        """
        Parses PDF into layout-aware chunks with bounding box geometry.
        """
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            # Extract structured text blocks with layout metadata
            blocks = page.get_text("dict")["blocks"]

            for b in blocks:
                if b.get("type") == 0:  # Text block
                    block_text = ""
                    block_bbox = [b["bbox"][0], b["bbox"][1], b["bbox"][2], b["bbox"][3]]
                    is_header = False

                    for line in b.get("lines", []):
                        line_text = "".join([span.get("text", "") for span in line.get("spans", [])]).strip()
                        if line_text:
                            # Check if first span has heading-level font size
                            if line.get("spans") and line["spans"][0].get("size", 10) >= 14:
                                is_header = True
                            block_text += " " + line_text

                    clean_text = block_text.strip()
                    if len(clean_text) >= 15:  # Filter out trivial noise
                        # If block is exceptionally long, subdivide safely
                        if len(clean_text) > max_chars_per_chunk:
                            sentences = clean_text.split(". ")
                            sub_accum = ""
                            for s in sentences:
                                if len(sub_accum) + len(s) < max_chars_per_chunk:
                                    sub_accum += s + ". "
                                else:
                                    if sub_accum.strip():
                                        chunks.append(DocumentChunk(
                                            chunk_index=chunk_idx,
                                            page_number=page_num,
                                            content=sub_accum.strip(),
                                            bbox=block_bbox,
                                            chunk_type="header" if is_header else "paragraph"
                                        ))
                                        chunk_idx += 1
                                    sub_accum = s + ". "
                            if sub_accum.strip():
                                chunks.append(DocumentChunk(
                                    chunk_index=chunk_idx,
                                    page_number=page_num,
                                    content=sub_accum.strip(),
                                    bbox=block_bbox,
                                    chunk_type="paragraph"
                                ))
                                chunk_idx += 1
                        else:
                            chunks.append(DocumentChunk(
                                chunk_index=chunk_idx,
                                page_number=page_num,
                                content=clean_text,
                                bbox=block_bbox,
                                chunk_type="header" if is_header else "paragraph"
                            ))
                            chunk_idx += 1

        doc.close()
        return chunks

layout_chunker = LayoutAwareChunker()

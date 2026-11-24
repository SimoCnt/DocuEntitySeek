"""Coordinate visive delle entita'/dei campi gia' mappati nel testo PDF.

Il confronto esatto impedisce di evidenziare il testo sbagliato quando la
rappresentazione geometrica differisce dal testo usato per l'analisi AI.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import pymupdf


@dataclass(frozen=True, slots=True)
class TextRegionRequest:
    """Text span that needs matching highlight rectangles on a PDF page."""

    kind: Literal["entity", "field"]
    id: str
    label: str
    start: int
    end: int


class PdfGeometryService:
    """Find normalized PDF rectangles for verified page-local AI spans."""

    def __init__(self, *, sort_text: bool = False) -> None:
        self.sort_text = sort_text

    def map_page(self, *, pdf_path: Path, page_number: int, expected_text: str, regions: list[TextRegionRequest]) -> dict:
        """Resolve normalized highlight rectangles for verified text spans.

        Re-extracts text from the original page with PyMuPDF. If the page text
        does not match the text used for inference, returns an unaligned result
        rather than potentially incorrect highlight geometry.
        """

        with pymupdf.open(pdf_path) as document:
            if not document.is_pdf or document.needs_pass or not 1 <= page_number <= document.page_count:
                raise ValueError("Il PDF o il numero di pagina non sono validi.")
            page = document[page_number - 1]
            extracted = page.get_text("rawdict", sort=self.sort_text)
            chars: list[str] = []
            positions: list[tuple[int, pymupdf.Rect] | None] = []
            line_id = 0

            for block in extracted["blocks"]:
                if block.get("type") != 0:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        for char in span["chars"]:
                            chars.append(char["c"])
                            positions.append((line_id, pymupdf.Rect(char["bbox"])))
                    chars.append("\n")
                    positions.append(None)
                    line_id += 1

            # Verifica rigorosa: mai usare coordinate di un testo che non e'
            # quello persistito (eventuale diversa opzione 'sort', OCR, ecc.).
            if "".join(chars) != expected_text:
                return {"pageNumber": page_number, "aligned": False, "regions": []}

            bounds = page.rect
            transform = page.rotation_matrix
            mapped = []
            for region in regions:
                if region.start < 0 or region.end > len(chars) or region.end <= region.start:
                    continue

                by_line: dict[int, list[pymupdf.Rect]] = defaultdict(list)
                for position in positions[region.start:region.end]:
                    if position is not None:
                        current_line, rect = position
                        by_line[current_line].append(rect)

                rectangles = []
                for line_rects in by_line.values():
                    joined = pymupdf.Rect(line_rects[0])
                    for rect in line_rects[1:]:
                        joined.include_rect(rect)
                    joined = joined * transform
                    x0 = max(0.0, min(1.0, (joined.x0 - bounds.x0) / bounds.width))
                    y0 = max(0.0, min(1.0, (joined.y0 - bounds.y0) / bounds.height))
                    x1 = max(0.0, min(1.0, (joined.x1 - bounds.x0) / bounds.width))
                    y1 = max(0.0, min(1.0, (joined.y1 - bounds.y0) / bounds.height))
                    if x1 > x0 and y1 > y0:
                        rectangles.append({"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})

                if rectangles:
                    mapped.append({"kind": region.kind, "id": region.id, "label": region.label, "rects": rectangles})

            return {"pageNumber": page_number, "aligned": True, "regions": mapped}

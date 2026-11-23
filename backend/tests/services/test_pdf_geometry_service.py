from pathlib import Path
import pymupdf

from app.services.pdf_geometry_service import PdfGeometryService, TextRegionRequest


def _make_pdf(tmp_path: Path, *, rotation: int = 0):
    path = tmp_path / "sample.pdf"
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((65, 90), "ALFA BETA\nLine two\nALFA BETA", fontsize=12)
        page.set_rotation(rotation)
        doc.save(path)
    with pymupdf.open(path) as doc:
        text = doc[0].get_text("text", sort=False)
    return path, text


def test_geometry_uses_offsets_to_distinguish_repeated_values(tmp_path):
    path, text = _make_pdf(tmp_path)
    assert text.count("ALFA BETA") == 2
    first = text.index("ALFA BETA")
    last = text.rindex("ALFA BETA")
    result = PdfGeometryService().map_page(
        pdf_path=path, page_number=1, expected_text=text,
        regions=[
            TextRegionRequest("entity", "e1", "ente", first, first + 9),
            TextRegionRequest("field", "f1", "campo", last, last + 9),
        ],
    )
    assert result["aligned"] is True
    assert len(result["regions"]) == 2
    assert result["regions"][0]["rects"][0]["y"] < result["regions"][1]["rects"][0]["y"]


def test_geometry_rejects_unaligned_text(tmp_path):
    path, text = _make_pdf(tmp_path)
    result = PdfGeometryService().map_page(pdf_path=path, page_number=1, expected_text=text + "!", regions=[TextRegionRequest("entity", "e", "x", 0, 4)])
    assert result == {"pageNumber": 1, "aligned": False, "regions": []}


def test_geometry_handles_multiline_spans(tmp_path):
    path, text = _make_pdf(tmp_path)
    start = text.index("BETA")
    end = text.index("two") + 3
    result = PdfGeometryService().map_page(pdf_path=path, page_number=1, expected_text=text, regions=[TextRegionRequest("entity", "e", "x", start, end)])
    assert result["aligned"] is True
    assert len(result["regions"][0]["rects"]) == 2
    for rect in result["regions"][0]["rects"]:
        assert all(0 <= rect[k] <= 1 for k in ("x", "y", "width", "height"))


def test_geometry_handles_rotated_pages(tmp_path):
    path, text = _make_pdf(tmp_path, rotation=90)
    result = PdfGeometryService().map_page(pdf_path=path, page_number=1, expected_text=text, regions=[TextRegionRequest("entity", "e", "x", 0, 4)])
    assert result["aligned"] and len(result["regions"]) == 1
    rect = result["regions"][0]["rects"][0]
    assert 0 <= rect["x"] < 1 and 0 <= rect["y"] < 1

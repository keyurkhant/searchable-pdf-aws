import json
import fitz
import math
from typing import Dict, Optional, List, Any
from geometry import BoundingBox

def make_pdf_doc_searchable(
    pdf_doc: fitz.Document,
    textract_blocks: List[Dict[str, Any]],
    add_word_bbox: bool = False,
    show_selectable_char: bool = False,
    pdf_image_dpi: int = 200,
    verbose: bool = False,
) -> fitz.Document:
    
    pdf_doc_img = fitz.open()
    for ppi, pdf_page in enumerate(pdf_doc.pages()):
        pdf_pix_map = pdf_page.get_pixmap(dpi=pdf_image_dpi, colorspace="RGB")
        pdf_page_img = pdf_doc_img.new_page(
            width=pdf_page.rect.width, height=pdf_page.rect.height
        )
        xref = pdf_page_img.insert_image(rect=pdf_page.rect, pixmap=pdf_pix_map)
    pdf_doc.close()

    print_step = 1000
    bbox_color = (220 / 255, 20 / 255, 60 / 255)  # red-ish color
    fontsize_initial = 15
    for blocki, block in enumerate(textract_blocks):
        if verbose:
            if blocki % print_step == 0:
                print(
                    (
                        f"processing blocks {blocki} to {blocki+print_step} out of {len(textract_blocks)} blocks"
                    )
                )
        if block["BlockType"] == "WORD":
            page = 0
            pdf_page = pdf_doc_img[page]

            bbox = BoundingBox.from_textract_bbox(block["Geometry"]["BoundingBox"])
            bbox.scale(pdf_page.rect.width, pdf_page.rect.height)

            if add_word_bbox:
                pdf_rect = fitz.Rect(bbox.left, bbox.top, bbox.right, bbox.bottom)
                pdf_page.draw_rect(
                    pdf_rect,
                    color=bbox_color,
                    fill=None,
                    width=0.7,
                    dashes=None,
                    overlay=True,
                    morph=None,
                )

            fill_opacity = 1 if show_selectable_char else 0
            text = block["Text"]
            text_length = fitz.get_text_length(
                text, fontname="helv", fontsize=fontsize_initial
            )
            fontsize_optimal = int(
                math.floor((bbox.width / text_length) * fontsize_initial)
            )
            rc = pdf_page.insert_text(
                point=fitz.Point(bbox.left, bbox.bottom),
                text=text,
                fontname="helv",
                fontsize=fontsize_optimal,
                rotate=0,
                color=bbox_color,
                fill_opacity=fill_opacity,
            )

    return pdf_doc_img
from pypdf import PdfReader, PdfWriter

def create_watermark(content_page, watermark, position, scale): 
    rotation = content_page.rotation
    if position == 'top_left':
        if rotation in [0, 180]:
            x = 0
            y = content_page.mediabox[3] - watermark.pages[0].mediabox[3] * scale
        elif rotation in [90, 270]:
            x = content_page.mediabox[2] - watermark.pages[0].mediabox[2] * scale
            y = 0
        else:
            raise ValueError(f"Unsupported rotation: {rotation}")
    elif position == 'bottom_left':
        if rotation in [0, 180]:
            x = 0
            y = 0
        elif rotation in [90, 270]:
            x = content_page.mediabox[2] - watermark.pages[0].mediabox[2] * scale
            y = content_page.mediabox[3] - watermark.pages[0].mediabox[3] * scale
        else:
            raise ValueError(f"Unsupported rotation: {rotation}")
    else:
        raise ValueError(f"Unsupported position: {position}")
    
    ctm = (scale, 0, 0, scale, x, y)

    content_page.merge_transformed_page(watermark.pages[0], ctm)

    return content_page

def apply_watermark(content_pdf, watermark_pdf, pdf_result, position, scale):
    watermark = PdfReader(watermark_pdf)

    writer = PdfWriter()
    reader = PdfReader(content_pdf)

    for i, content_page in enumerate(reader.pages):
        content_page.transfer_rotation_to_content()
        create_watermark(content_page, watermark, position, scale)
        writer.add_page(content_page)

    writer.write(pdf_result)
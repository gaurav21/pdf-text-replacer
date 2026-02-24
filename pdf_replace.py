#!/usr/bin/env python3
"""
PDF Text Replacement Tool - Version 3
Replaces "Premium" with "Standard" by properly sampling background color.
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
from collections import Counter


def sample_background_color(page, rect):
    """
    Sample the background color by looking at pixels around the text.
    Returns RGB tuple.
    """
    try:
        # Expand rect slightly to get surrounding pixels
        expanded = fitz.Rect(rect.x0 - 5, rect.y0 - 2, rect.x1 + 5, rect.y1 + 2)

        # Get pixmap of the area
        pix = page.get_pixmap(clip=expanded, alpha=False)

        # Sample pixels from the edges (likely to be background)
        samples = []
        width = pix.width
        height = pix.height

        # Sample top and bottom edges
        for x in range(0, width, max(1, width // 10)):
            # Top edge
            if height > 0:
                pixel_top = pix.pixel(x, 0)
                samples.append(pixel_top[:3])  # RGB only
            # Bottom edge
            if height > 1:
                pixel_bottom = pix.pixel(x, height - 1)
                samples.append(pixel_bottom[:3])

        # Find most common color (likely background)
        if samples:
            color_counter = Counter(samples)
            most_common_rgb = color_counter.most_common(1)[0][0]
            # Convert to 0-1 range
            return (most_common_rgb[0] / 255.0,
                   most_common_rgb[1] / 255.0,
                   most_common_rgb[2] / 255.0)
    except Exception as e:
        print(f"  Warning: Could not sample background color: {e}")

    return (1, 1, 1)  # Default to white


def replace_text_in_pdf(input_pdf: str, output_pdf: str, search_text: str = "Premium", replace_text: str = "Standard"):
    """
    Replace text in PDF while preserving formatting and background.
    """
    try:
        doc = fitz.open(input_pdf)
        replacements_count = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.search_for(search_text)

            if text_instances:
                blocks = page.get_text("dict")["blocks"]
                replacements = []

                for inst in text_instances:
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    span_rect = fitz.Rect(span["bbox"])

                                    if span_rect.intersects(inst) and search_text in span["text"]:
                                        font_size = span["size"]
                                        font_color = span["color"]
                                        font_flags = span.get("flags", 0)

                                        # Convert color
                                        if isinstance(font_color, int):
                                            r = ((font_color >> 16) & 0xFF) / 255.0
                                            g = ((font_color >> 8) & 0xFF) / 255.0
                                            b = (font_color & 0xFF) / 255.0
                                            text_color = (r, g, b)
                                        else:
                                            text_color = (0, 0, 0)

                                        # Detect font style
                                        fontname = "helv"
                                        if font_flags & 2**4:  # Bold
                                            fontname = "hebo"

                                        replacements.append({
                                            'rect': inst,
                                            'size': font_size,
                                            'color': text_color,
                                            'fontname': fontname,
                                        })

                                        replacements_count += 1
                                        break

                # Perform replacements
                for repl in replacements:
                    rect = repl['rect']

                    # Sample actual background color from the PDF
                    bg_color = sample_background_color(page, rect)

                    print(f"  Page {page_num + 1}: BG={bg_color}, Text={repl['color']}, Size={repl['size']:.1f}")

                    # Extend rectangle slightly to ensure full coverage
                    cover_rect = fitz.Rect(rect.x0 - 1, rect.y0, rect.x1 + 1, rect.y1)

                    # Cover old text with sampled background color
                    page.draw_rect(cover_rect, color=bg_color, fill=bg_color)

                    # Insert new text
                    page.insert_text(
                        (rect.x0, rect.y1 - 2),
                        replace_text,
                        fontsize=repl['size'],
                        color=repl['color'],
                        fontname=repl['fontname']
                    )

        doc.save(output_pdf, garbage=4, deflate=True, pretty=True)
        doc.close()

        print(f"\n✓ Successfully replaced {replacements_count} occurrence(s) of '{search_text}' with '{replace_text}'")
        print(f"✓ Output saved to: {output_pdf}")

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_replace_v3.py <input.pdf> [output.pdf]")
        sys.exit(1)

    input_pdf = sys.argv[1]

    if not Path(input_pdf).exists():
        print(f"✗ Error: Input file '{input_pdf}' not found", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_pdf = sys.argv[2]
    else:
        input_path = Path(input_pdf)
        output_pdf = str(input_path.parent / f"{input_path.stem}_modified{input_path.suffix}")

    print(f"Processing: {input_pdf}")
    replace_text_in_pdf(input_pdf, output_pdf)


if __name__ == "__main__":
    main()

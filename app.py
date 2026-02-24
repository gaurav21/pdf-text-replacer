#!/usr/bin/env python3
"""
PDF Text Replacement Tool - Web UI
Interactive UI for replacing text in PDFs with preview functionality.
"""

import streamlit as st
import fitz  # PyMuPDF
from collections import Counter
import io
from pathlib import Path
import tempfile


def sample_background_color(page, rect):
    """Sample the background color by looking at pixels around the text."""
    try:
        expanded = fitz.Rect(rect.x0 - 5, rect.y0 - 2, rect.x1 + 5, rect.y1 + 2)
        pix = page.get_pixmap(clip=expanded, alpha=False)

        samples = []
        width = pix.width
        height = pix.height

        for x in range(0, width, max(1, width // 10)):
            if height > 0:
                pixel_top = pix.pixel(x, 0)
                samples.append(pixel_top[:3])
            if height > 1:
                pixel_bottom = pix.pixel(x, height - 1)
                samples.append(pixel_bottom[:3])

        if samples:
            color_counter = Counter(samples)
            most_common_rgb = color_counter.most_common(1)[0][0]
            return (most_common_rgb[0] / 255.0,
                   most_common_rgb[1] / 255.0,
                   most_common_rgb[2] / 255.0)
    except Exception as e:
        st.warning(f"Could not sample background color: {e}")

    return (1, 1, 1)


def find_text_instances(pdf_bytes, search_text):
    """Find all instances of search text in the PDF and return details."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    instances = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.search_for(search_text)

        if text_instances:
            blocks = page.get_text("dict")["blocks"]

            for inst in text_instances:
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                span_rect = fitz.Rect(span["bbox"])

                                if span_rect.intersects(inst) and search_text in span["text"]:
                                    font_size = span["size"]
                                    font_color = span["color"]

                                    # Convert color
                                    if isinstance(font_color, int):
                                        r = ((font_color >> 16) & 0xFF) / 255.0
                                        g = ((font_color >> 8) & 0xFF) / 255.0
                                        b = (font_color & 0xFF) / 255.0
                                        text_color = (r, g, b)
                                    else:
                                        text_color = (0, 0, 0)

                                    bg_color = sample_background_color(page, inst)

                                    instances.append({
                                        'page': page_num + 1,
                                        'rect': inst,
                                        'text': search_text,
                                        'size': font_size,
                                        'text_color': text_color,
                                        'bg_color': bg_color,
                                        'context': span["text"]
                                    })
                                    break

    doc.close()
    return instances


def replace_text_in_pdf(pdf_bytes, search_text, replace_text):
    """Replace text in PDF and return the modified PDF bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
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
                bg_color = sample_background_color(page, rect)

                # Cover old text with background color
                cover_rect = fitz.Rect(rect.x0 - 1, rect.y0, rect.x1 + 1, rect.y1)
                page.draw_rect(cover_rect, color=bg_color, fill=bg_color)

                # Insert new text
                page.insert_text(
                    (rect.x0, rect.y1 - 2),
                    replace_text,
                    fontsize=repl['size'],
                    color=repl['color'],
                    fontname=repl['fontname']
                )

    # Save to bytes
    output_bytes = doc.write(garbage=4, deflate=True, pretty=True)
    doc.close()

    return output_bytes, replacements_count


def render_pdf_preview(pdf_bytes, page_num=0, zoom=2.0):
    """Render a PDF page as an image for preview."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_num]

    # Render page to image
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # Convert to PNG bytes
    img_bytes = pix.tobytes("png")
    doc.close()

    return img_bytes


def main():
    st.set_page_config(
        page_title="PDF Text Replacer",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 PDF Text Replacement Tool")
    st.markdown("Upload a PDF, specify text to find and replace, preview changes, and download the result.")

    # File upload
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()

        # Create two columns for input
        col1, col2 = st.columns(2)

        with col1:
            search_text = st.text_input("Text to find:", value="Premium", key="search")

        with col2:
            replace_text = st.text_input("Replace with:", value="Standard", key="replace")

        # Search button
        if st.button("🔍 Find Instances", type="primary"):
            if search_text:
                with st.spinner("Searching for text instances..."):
                    instances = find_text_instances(pdf_bytes, search_text)
                    st.session_state['instances'] = instances
                    st.session_state['pdf_bytes'] = pdf_bytes
                    st.session_state['search_text'] = search_text
                    st.session_state['replace_text'] = replace_text

        # Display found instances
        if 'instances' in st.session_state and st.session_state['instances']:
            instances = st.session_state['instances']

            st.success(f"✓ Found {len(instances)} instance(s) of '{st.session_state['search_text']}'")

            # Display instance details
            with st.expander("📋 View All Instances", expanded=True):
                for i, inst in enumerate(instances, 1):
                    st.markdown(f"""
                    **Instance {i}:**
                    - Page: {inst['page']}
                    - Context: `{inst['context']}`
                    - Font Size: {inst['size']:.1f}pt
                    - Text Color: RGB{tuple(round(c, 2) for c in inst['text_color'])}
                    - Background: RGB{tuple(round(c, 2) for c in inst['bg_color'])}
                    """)
                    st.divider()

            # Preview section
            st.subheader("👁️ Preview")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original PDF**")
                original_preview = render_pdf_preview(st.session_state['pdf_bytes'])
                st.image(original_preview, use_container_width=True)

            with col2:
                st.markdown("**After Replacement**")
                with st.spinner("Generating preview..."):
                    modified_bytes, _ = replace_text_in_pdf(
                        st.session_state['pdf_bytes'],
                        st.session_state['search_text'],
                        st.session_state['replace_text']
                    )
                    modified_preview = render_pdf_preview(modified_bytes)
                    st.image(modified_preview, use_container_width=True)
                    st.session_state['modified_bytes'] = modified_bytes

            # Download button
            if 'modified_bytes' in st.session_state:
                st.divider()

                # Generate filename
                original_name = Path(uploaded_file.name).stem
                output_filename = f"{original_name}_modified.pdf"

                st.download_button(
                    label="⬇️ Download Modified PDF",
                    data=st.session_state['modified_bytes'],
                    file_name=output_filename,
                    mime="application/pdf",
                    type="primary"
                )

                st.success(f"✓ Ready to download: {output_filename}")

        elif 'instances' in st.session_state and not st.session_state['instances']:
            st.warning(f"No instances of '{st.session_state['search_text']}' found in the PDF.")

    else:
        st.info("👆 Upload a PDF file to get started")

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Built with PyMuPDF and Streamlit | Preserves formatting, colors, and backgrounds
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

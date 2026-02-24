# PDF Text Replacer

A web-based tool for replacing text in PDF files while preserving formatting, colors, and backgrounds.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.54.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🔍 **Smart Text Search**: Find all occurrences of specific text in PDFs
- 🎨 **Format Preservation**: Maintains font size, color, and style
- 🖼️ **Background Detection**: Automatically samples and preserves background colors
- 👁️ **Side-by-Side Preview**: Compare original and modified PDFs before downloading
- ⚡ **Fast Processing**: Optimized with PyMuPDF for quick operations
- 🐳 **Docker Ready**: One-command deployment with Docker Compose

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-text-replacer.git
cd pdf-text-replacer

# Start the application
docker-compose up -d

# Access the app
open http://localhost:8501
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Usage

1. **Upload PDF**: Click "Upload PDF" and select your file
2. **Specify Text**: Enter the text to find and what to replace it with
3. **Find Instances**: Click "Find Instances" to locate all occurrences
4. **Preview Changes**: View side-by-side comparison of original and modified PDF
5. **Download**: Click "Download Modified PDF" to save the result

## How It Works

The application uses PyMuPDF to:

1. **Search**: Locate all instances of the search text with precise positioning
2. **Analyze**: Extract font properties (size, color, style) and background color
3. **Replace**: Cover old text with background color and redraw new text with identical formatting
4. **Preserve**: Maintain exact visual appearance except for the replaced text

### Background Color Detection

The app samples pixels around the text area to detect the actual background color, ensuring perfect preservation even with colored or patterned backgrounds.

## Architecture

```
pdf-text-replacer/
├── app.py                 # Streamlit web interface
├── pdf_replace.py         # Core PDF processing logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose setup
└── README.md            # This file
```

## Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Check status
docker-compose ps
```

## Configuration

### Environment Variables

You can customize the app by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Port Mapping

To use a different port, modify `docker-compose.yml`:

```yaml
ports:
  - "8080:8501"  # Change 8080 to your preferred port
```

## Requirements

- Python 3.12+
- PyMuPDF (fitz) 1.24.0+
- Streamlit 1.54.0+
- Docker & Docker Compose (for containerized deployment)

## Limitations

- Works best with text-based PDFs (not scanned images)
- Replacement text should be similar length to original for best results
- Some complex PDF layouts may require manual adjustment

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs pdf-replacer

# Ensure port 8501 is not in use
lsof -i :8501
```

### Module not found errors

```bash
# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Background color not detected correctly

The app samples pixels from the edges of the text area. For complex backgrounds:
- Ensure high-quality PDF (not compressed/downsampled)
- Try processing specific pages separately

## Development

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
streamlit run app.py --server.runOnSave true
```

### Running Tests

```bash
# Test with sample PDF
python -c "from pdf_replace import replace_text_in_pdf; replace_text_in_pdf('input.pdf', 'output.pdf')"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- PDF processing powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- Inspired by the need for format-preserving PDF text replacement

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for easy PDF text replacement

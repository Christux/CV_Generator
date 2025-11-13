# CV Generator

**CV Generator** is a Python-based static site generator designed to build a single-page HTML résumé or portfolio from structured data.  
It uses **YAML**, **Jinja2 templates**, and **Markdown**, allowing a clean separation between content, design, and assets.

---

## Features

- Template-based page generation using **Jinja2**
- Content and configuration loaded from **YAML** files
- **Markdown** support for content fields
- Automatic CSS/JS concatenation with cache-busting build IDs
- **Live reload** development server using WebSockets
- Dead link checker for the generated HTML
- FTP uploader support for deployment

---

## Project Structure
generator/
├── app_config.py           # Application-wide configuration  
├── app.py                  # CLI entry point  
├── page_generator.py       # Core static page builder  
├── dev_server.py           # Live reload development server  
├── ftp_uploader.py         # FTP upload utility  
├── dead_link_finder.py     # Link checker  
├── jinja_filters.py        # Custom Jinja2 filters  
├── templates/              # HTML templates  
└── assets/                 # CSS, JS, images, etc.  

Configuration and content are stored in:

config.yaml      # Template and assets configuration
data.yaml        # CV content (YAML + Markdown)
credentials.yaml # Optional, for FTP deployment

---

## Installation

### 1. Create a virtual environment
```bash
python3.12 -m venv .venv
```
### 2. Activate the environment
```bash
source .venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. (Optional) Backup dependencies
```bash
pip freeze > requirements.txt
```

---

## Usage

### Show all available commands
```bash
python -m generator -h
```

### Development Mode (with live reload)

Starts a local web server and automatically rebuilds your CV on file changes.
```bash
python -m generator --dev-server --open-browser --debug
```
This will:  

- Watch your templates, data, and assets folders
- Rebuild the page automatically when a file changes
- Open your browser to http://localhost:8080
- Reload the page automatically via WebSocket

### Production Build

Generates the final static page in the dist/ folder.

```bash
python -m generator --build
```

### Check for Dead Links

After building your CV, you can verify all links automatically.

```bash
python -m generator --find-dead-links --debug
```

### Upload via FTP (still in developpement)

Upload your built site to your hosting provider using the credentials from credentials.yaml.

```bash
python -m generator --ftp-upload
```

---

## Output

After a successful build, the generated files will be located in the dist/ folder:

dist/  
├── index.html  
├── sitemap.xml  
├── css/  
│   └── style.<build_id>.css  
└── js/  
    └── script.<build_id>.js

---

## Debug Mode

Use the --debug flag to print detailed internal logs, such as:  
- YAML parsing details
- Markdown rendering output
- Template rendering data
- Asset build and cleanup operations

---

## License

MIT License
© 2025 — Christophe Rubeck

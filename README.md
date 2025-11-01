# CV Generator
Python script for generating a single html CV

## Install

### Create virtual environmeent
python3.12 -m venv .venv

### Activate
source .venv/bin/activate

### Install dependencies
pip install -r requirements.txt

### Backup env
pip freeze > requirements.txt

## Lauch Generator
python -m generator -h

### Dev mode
python -m generator --dev-server --open-browser --debug

### Production
python -m generator --build
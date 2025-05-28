# winSIM Invoice Downloader

This script downloads your monthly invoices from the winSIM customer portal using Python.

## Features
- Logs in to https://service.winsim.de/ with your credentials
- Downloads all available invoices
- Saves invoices with the original filename from the server
- Skips invoices that are already downloaded

## Setup
1. **Clone this repository**
2. **Install dependencies using Poetry:**
   ```sh
   poetry install
   ```
3. **Configure your credentials:**
   - Copy `config.py` to your project root (see below for format)
   - Add your winSIM username and password:
     ```python
     USERNAME = "your_username_here"
     PASSWORD = "your_password_here"
     ```
   - `config.py` is in `.gitignore` and will not be committed.


## Usage
Run the script using Poetry:
```sh
poetry run python winsim.py
```

By default, the script stops when it finds the first invoice file that already exists in the `invoices/` directory. To check and attempt to download all invoices (skipping already downloaded files), use the `--all` option:
```sh
poetry run python winsim.py --all
```

Invoices will be saved in the `invoices/` directory.

## Security
- Your credentials are stored in `config.py`, which is excluded from version control by `.gitignore`.

## Requirements
- Python 3.8+
- [Poetry](https://python-poetry.org/)

## Disclaimer
This script is for personal use. Use at your own risk.
It was created with the help of GitHub Copilot.
The website structure may change and break the script.

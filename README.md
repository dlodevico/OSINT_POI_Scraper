# OSINT POI Scraper

A Python-based starter project for collecting and organizing point-of-interest (POI) data in OSINT workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

This repository provides a simple foundation for building an OSINT POI scraping workflow with Python. It includes a basic entrypoint and a GitHub Actions workflow to validate the project automatically.

## Project Structure

- `src/main.py` — sample Python entrypoint.

## Getting Started

Run the sample script:

```bash
python src/main.py
```

## Demo

To try the local web interface:

```bash
python src/main.py --server
```

Then open http://127.0.0.1:8000 in your browser. The page includes a visible version banner and a results table for the scraped account matches.

## Continuous Integration

A GitHub Actions workflow is included to run Python checks on pushes and pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

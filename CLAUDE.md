# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
AI Overviews Analysis tool for fetching and analyzing Google AI Overview results across keywords for brand analysis and competitor research. This is a Streamlit-based application that uses the DataForSEO API to gather search data and analyze AI overview citations.

## Commands

### Running the Application
```bash
streamlit run app.py
```

### Environment Setup
- Ensure `.env` file contains `SEO_API_KEY` with DataForSEO API credentials
- Install required dependencies: `streamlit`, `pandas`, `requests`, `tqdm`, `python-dotenv`

## Architecture

### Core Structure
- **app.py**: Main Streamlit application with two modes - "Fetch Keywords" (live API) and "Upload JSON" (file upload)
- **functions/**: Modular processing pipeline
  - `fetchKeywords.py`: Makes concurrent API calls to DataForSEO to fetch SERP data with AI overviews
  - `apiToDataFrame.py`: Currently a placeholder function for API data conversion
  - `analyzeDataFrame.py`: Core analysis engine that processes AI overview data, extracts citations, performs brand ranking, and generates competitor analysis
  - `loadAPI.py`: Loads existing JSON API results from file

### Data Flow
1. Keywords input → `fetchKeywords()` → API data collection with threading (50 concurrent workers)
2. Raw API data → `apiToDataFrame()` → DataFrame conversion (currently incomplete)
3. DataFrame → `analyzeDataFrame()` → Brand analysis, citation extraction, competitor ranking
4. Output: CSV files (`keywords.csv`, `competitor.csv`, `brand-mention-summary.csv`)

### Key Features
- **Concurrent API Processing**: Uses ThreadPoolExecutor with 50 max workers for parallel keyword fetching
- **AI Overview Analysis**: Extracts and cleans markdown content, processes citation references
- **Brand Citation Tracking**: Identifies brand mentions and ranking in AI overview citations
- **Competitor Analysis**: Generates comprehensive competitor citation and mention analysis
- **Multiple Input Modes**: Supports both live API fetching and JSON file upload

### Data Processing Pipeline
- Cleans markdown citations using regex patterns
- Extracts reference data (domain, source, URL, rank)
- Performs brand mention detection in AI overview text
- Calculates citation probabilities and prompt coverage rates
- Generates domain-based competitor matching

### Configuration
- API endpoint: DataForSEO Google SERP API v3
- Location and language codes configurable via Streamlit interface
- Search depth: 10 results with grouped organic results
- Async AI overview loading enabled
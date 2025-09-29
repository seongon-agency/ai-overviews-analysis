# AI Overviews Analysis Tool

A comprehensive Streamlit application for fetching and analyzing Google AI Overview results across keyword sets to provide brand analysis and competitive intelligence insights.

## Overview

This tool enables businesses and SEO professionals to understand how their brand and competitors appear in Google's AI Overview feature. It provides detailed analytics on citation rankings, brand mentions, and competitive positioning within AI-generated search responses.

## Features

- **Live Data Fetching**: Real-time keyword analysis using DataForSEO API
- **Batch Processing**: Upload and analyze existing JSON data files
- **Concurrent Processing**: High-performance data collection with 50 concurrent workers
- **Brand Analysis**: Track your brand's citations and mentions in AI Overviews
- **Competitor Intelligence**: Comprehensive analysis of competitor presence
- **Interactive Visualizations**: Dynamic charts showing competitive positioning
- **Export Capabilities**: Download analysis results in CSV format
- **Multi-language Support**: Configurable location and language codes

## Technical Architecture

### Core Components

- **app.py**: Main Streamlit application interface
- **functions/fetchKeywords.py**: DataForSEO API integration with concurrent processing
- **functions/analyzeDataFrame.py**: Core analysis engine for AI overview data processing
- **functions/apiToDataFrame.py**: Data transformation utilities
- **functions/loadAPI.py**: JSON data loading functionality

### Data Pipeline

1. **Data Collection**: Keywords → DataForSEO API → Raw SERP data with AI overviews
2. **Processing**: Raw data → Citation extraction → Brand mention detection
3. **Analysis**: Competitive ranking → Citation probability → Engagement metrics
4. **Output**: Interactive dashboards + Downloadable reports

## Installation

### Prerequisites

- Python 3.7+
- DataForSEO API account and credentials

### Dependencies

```bash
pip install streamlit pandas requests tqdm python-dotenv plotly
```

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-overviews-analysis
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Configure your DataForSEO API credentials in `.env`:
```
SEO_API_KEY=Basic <your-base64-encoded-credentials>
```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Operating Modes

#### 1. Live Keyword Fetching

- Input keywords (one per line or comma-separated)
- Specify location code (4-digit numeric)
- Set language code (2-letter ISO code)
- Execute real-time analysis

#### 2. JSON File Upload

- Upload previously downloaded DataForSEO results
- Process existing data without API calls
- Useful for re-analysis or batch processing

### Analysis Configuration

1. **Brand Information**:
   - Enter your brand name
   - Specify your primary domain

2. **Location Codes**:
   - Vietnam: 2704
   - United States: 2840
   - United Kingdom: 2826

3. **Language Codes**:
   - Vietnamese: vi
   - English: en

## Output Analysis

### Keywords Analysis
- Individual keyword performance
- AI overview citation rankings
- Reference source analysis
- Brand positioning per keyword

### Competitor Analysis
- Citation count comparison
- Brand mention frequency
- Engagement rate calculations
- Market share visualization

### Export Options
- Keywords analysis CSV
- Comprehensive competitor analysis CSV
- Executive summary report

## API Configuration

### DataForSEO Settings

- **Endpoint**: Google SERP Organic Live Advanced
- **Search Depth**: 10 results
- **Features**: Grouped organic results, async AI overview loading
- **Concurrency**: 50 parallel requests

### Rate Limiting

The application respects DataForSEO rate limits through controlled concurrency and proper request spacing.

## Data Processing

### Citation Extraction
- Parses AI overview reference lists
- Extracts domain information and ranking
- Calculates citation probabilities

### Brand Mention Detection
- Regex-based brand name identification
- Context-aware mention scoring
- False positive filtering

### Competitive Analysis
- Cross-reference citation and mention data
- Calculate market share metrics
- Generate ranking comparisons

## Contributing

### Development Setup

1. Install development dependencies
2. Follow PEP 8 coding standards
3. Add unit tests for new features
4. Update documentation

### Code Structure

- Modular function-based architecture
- Separation of concerns between data collection and analysis
- Streamlit components for user interface
- Plotly for data visualization

## Troubleshooting

### Common Issues

1. **API Authentication Errors**: Verify DataForSEO credentials in `.env`
2. **Rate Limiting**: Reduce concurrent workers in `fetchKeywords.py`
3. **Memory Issues**: Process smaller keyword batches
4. **Data Format Errors**: Ensure consistent JSON structure

### Performance Optimization

- Adjust `MAX_WORKERS` setting based on API limits
- Use JSON upload mode for large datasets
- Monitor memory usage with large keyword lists

## License

See LICENSE file for details.

## Support

For technical issues or feature requests, please refer to the project's issue tracker.

# MM Stock About Batch Processing Tool

## Overview
This Streamlit application allows you to:
- Upload an Excel or CSV file
- Customize a system prompt for OpenAI's GPT-4o
- Process a batch of inputs through the OpenAI API
- Download the processed results

## Prerequisites
- Python 3.8+
- Streamlit
- OpenAI API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/x1001000/mm-stock-about
cd mm-stock-about
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### OpenAI API Key Setup
1. Create a `.streamlit/secrets.toml` file in your project directory
2. Add your OpenAI API key:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

## Running the App
```bash
streamlit run streamlit_app.py
```

## Usage Instructions
1. Open the Streamlit app in your browser
2. Use the sidebar to set a system prompt
3. Upload an Excel or CSV file with an 'Input' column
4. Click "Process with OpenAI" to generate outputs
5. Download the processed file

## Input File Requirements
- Must be an Excel (.xlsx) or CSV (.csv) file
- Must contain an 'Input' column
- The 'Input' column will be used as user messages for GPT-4o

## Notes
- Ensure you have a stable internet connection
- OpenAI API usage is subject to their pricing and terms
- Be mindful of API rate limits and costs

## Troubleshooting
- Check that your OpenAI API key is correctly set in secrets
- Verify the input file format and 'Input' column
- Contact support if you encounter persistent issues

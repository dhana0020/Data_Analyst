
# AI Data Analyst

A GenAI-powered data analysis application that lets users upload CSV or Excel datasets and ask questions in natural language.

## Features

- Upload CSV and XLSX datasets
- Preview datasets and inspect data quality
- View dataset metrics and summary statistics
- Ask natural-language questions using Gemini
- Execute supported analyses using Pandas
- Generate exploratory charts
- Maintain conversation history
- Download analysis results as CSV
- Export dataset reports as Excel workbooks

## Tech Stack

- Python
- Streamlit
- Pandas and NumPy
- Google Gemini API
- Plotly
- OpenPyXL

## Setup

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies.
4. Create a `.env` file in the project root.
5. Add your own Gemini API key.
6. Run the Streamlit application.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `.env` with:

```text
GEMINI_API_KEY=your_own_gemini_api_key
```

Then run:

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Security

Never commit `.env` files, API keys, or virtual environments.

## Project Status

Core features are under development. Advanced multi-step analysis and further reliability improvements are planned.

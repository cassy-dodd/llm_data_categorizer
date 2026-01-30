# Data Categorizer

A Python tool for categorizing data using local language models.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the data categorizer from the command line:

```bash
python -m data_categorizer data_categorizer/input.csv data_categorizer/output.csv phi4-mini:latest
```

### Arguments

- `input.csv` - Path to the input CSV file containing data to categorize
- `output.csv` - Path where the categorized output will be saved
- `phi4-mini:latest` - The model to use for categorization

## Requirements

- Python 3.7+
- Required packages (see `requirements.txt`)
- Local model access (e.g., Ollama with phi4-mini model)

## Example

```bash
python -m data_categorizer data_categorizer/input.csv data_categorizer/output.csv phi4-mini:latest
```

This will read data from `input.csv`, categorize it using the `phi4-mini:latest` model, and save results to `output.csv`.

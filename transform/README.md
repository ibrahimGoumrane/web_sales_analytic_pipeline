# Data Transformation Pipeline

This module handles the cleaning and transformation of raw scraped data into a processed format suitable for analysis.

## 📁 Structure

```
transform/
├── clean_transform.py   # Main cleaning logic
└── README.md           # This documentation
```

## 🛠️ Usage

```python
from transform.clean_transform import CleanData

cleaner = CleanData()

# Process all files for a specific website
cleaner.process_website('jumia')
```

## 🔍 Methods Documentation

### `CleanData` Class

#### `__init__()`

Initializes the cleaner and ensures `data/raw` and `data/processed` directories exist.

#### `process_website(website: str) -> bool`

Main entry point to process all CSV files for a given website.

- **Input**: Website name (e.g., 'jumia').
- **Action**: Iterates through all CSV files in `data/raw/{website}/`.
- **Output**: Returns `True` if successful, `False` otherwise.

#### `clean(data: pd.DataFrame, website: str) -> pd.DataFrame`

Applies website-specific cleaning logic.

- **Input**: Raw DataFrame and website name.
- **Output**: Cleaned DataFrame.

#### `clean_jumia(df: pd.DataFrame) -> pd.DataFrame`

Specific cleaning logic for Jumia data.

**Transformations Applied:**

1. **`current_price`**:

   - Input: "1,229.00 Dhs" (string)
   - Output: 1229.0 (float)
   - Removes currency 'Dhs', commas, and whitespace.

2. **`old_price`**:

   - Input: "2,000.00 Dhs" (string)
   - Output: 2000.0 (float)
   - Same transformation as current_price.

3. **`discount`**:

   - Input: "-39%" (string)
   - Output: 39.0 (float)
   - Removes '%' and '-', extracts numeric value.

4. **`rating`**:

   - Input: "4.4 out of 5" or "4.4" (string/numeric)
   - Output: 4.4 (float)

5. **`review_count`**:

   - Input: "(123)" or "123" (string/numeric)
   - Output: 123.0 (float)

6. **Booleans** (`is_official_store`):

   - Converted to native boolean type.

7. **`scraped_at`**:
   - Converted to datetime objects.

#### `save(data: pd.DataFrame, path: str)`

Saves the processed DataFrame to a CSV file.

- **Input**: DataFrame and destination path.
- **Action**: Saves file without index.

## 📊 Data Flow

1. **Input**: Raw CSV files in `data/raw/{website}/`
   - Contains raw strings, currency symbols, mixed types.
2. **Process**: `CleanData` pipeline
   - Type conversion
   - String cleaning
   - Numeric extraction
3. **Output**: Processed CSV files in `data/processed/{website}/`
   - Clean numeric fields
   - Standardized dates
   - Ready for analysis/SQL loading

## 📝 Logs

Logs are written to:

- Console (Standard Output)
- `logs/transform.log`

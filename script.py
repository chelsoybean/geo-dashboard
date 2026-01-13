import pandas as pd

#FUNCTION TO READ GOOGLE SHEETS
def read_sheets(sheet_id, sheet_name=None):
    if sheet_name:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    return pd.read_csv(url)

#FUNCTION CONVERT STR TO NUMERIC WITH ERROR HANDLING
def clean_numeric(df, cols):
    df = df.copy()
    
    for col in cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r'[^\d\-\.]', '', regex=True)
                .replace('', pd.NA)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

import pandas as pd

#FUNCTION TO READ GOOGLE SHEETS
def read_sheets(sheet_id, sheet_name=None):
    if sheet_name:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    else:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    return pd.read_csv(url)
import pandas as pd


def process_csv(file):

    # Read CSV file
    data = pd.read_csv(file)

    # Remove completely empty rows
    data = data.dropna(how="all")

    # Remove extra spaces from column names
    data.columns = data.columns.str.strip()

    return data
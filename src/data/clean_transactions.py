import pandas as pd
from pathlib import Path

def load_all_sheets(path: Path) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    dfs = []
    for sheet in xls.sheet_names:
        tmp = pd.read_excel(path, sheet_name=sheet)
        tmp["source_sheet"] = sheet  # helps debugging
        dfs.append(tmp)
    return pd.concat(dfs, ignore_index=True)


def load_raw_data(path: Path) -> pd.DataFrame:
    return load_all_sheets(path)


def remove_cancelled_invoices(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["Invoice"].astype(str).str.startswith("C")]


def remove_invalid_quantities(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Quantity"] > 0]


def remove_invalid_prices(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Price"] > 0]


def drop_missing_customers(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=["Customer ID"])


def parse_invoice_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df

def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()


def main():
    # Paths relative to project root
    raw_path = Path("./online+retail+ii/online_retail_II.xlsx")
    output_path = Path("./transactions_clean.csv")

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw data file not found at {raw_path}")

    df = load_raw_data(raw_path)
    df = drop_exact_duplicates(df)
    
    df = remove_cancelled_invoices(df)
    df = remove_invalid_quantities(df)
    df = remove_invalid_prices(df)
    df = drop_missing_customers(df)
    df = parse_invoice_date(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Cleaned data saved to {output_path}")


if __name__ == "__main__":
    main()
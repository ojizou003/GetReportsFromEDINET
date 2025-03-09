import pdfplumber
import pandas as pd
import os
from tqdm import tqdm

input_folder = "./pdf_files"
pdf_file_list = [
    os.path.join(input_folder, file)
    for file in os.listdir(input_folder)
    if file.endswith(".pdf")
]

for pdf_file in tqdm(pdf_file_list):
    with pdfplumber.open(pdf_file) as pdf:
        table_list = []
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            tables = page.find_tables()
            if tables:
                for table in tables:
                    table_list.extend(table.extract())
                break
    _df = pd.DataFrame(table_list)
    _df.columns = [_df.iloc[0, :]]
    df = _df.iloc[1:, :].reset_index(drop=True)
    new_column_name = [column[0].replace("\n", " ") for column in df.columns]
    df.columns = new_column_name
    for i in range(len(df.columns)):
        df.iloc[:, i] = df.iloc[:, i].replace("\n", " ", regex=True).replace('△', '-', regex=True)
        # ファイル名を抽出
    file_name = os.path.basename(pdf_file)
    # 拡張子を除去
    extracted_name = os.path.splitext(file_name)[0]
    os.makedirs("output", exist_ok=True)
    df.to_csv(f"output/{extracted_name}.csv", index=False)

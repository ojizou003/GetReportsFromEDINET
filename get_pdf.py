# Imports
import datetime
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from tqdm import tqdm

# EDINET_API_KEY
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ENDPOINT
ENDPOINT_1 = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
ENDPOINT_2 = "https://api.edinet-fsa.go.jp/api/v2/documents"

# 証券コードリスト
company_df = pd.read_excel("./company_list.xlsx")
_secCode_list = company_df["証券コード"].astype(str).tolist()
# 4桁 -> 5桁
secCode_list = [_secCode + "0" for _secCode in _secCode_list]

def make_date_list():
    """
    過去200日の日付リストを作成する関数
    """
    past_120_days = [
        datetime.date.today() - datetime.timedelta(days=i) for i in range(200)
    ]
    return [d.strftime("%Y-%m-%d") for d in past_120_days]

# 対象の書類リストを抽出
url = ENDPOINT_1
docItem_list = []
for day in tqdm(make_date_list()):
    params = {"date": day, "type": 2, "Subscription-Key": API_KEY}
    res = requests.get(url, params=params)
    data = res.json()
    datum = data["results"]
    docItems = []
    for d in datum:
        if (d["secCode"] in secCode_list) and (
            ("有価証券報告書" in d["docDescription"])
            or ("半期報告書" in d["docDescription"])
        ):
            item_dict = {
                "docID": d["docID"],
                "証券コード": d["secCode"],
                "会社名": d["filerName"],
                "書類名": d["docDescription"],
            }
            docItems.append(item_dict)
    docItem_list.extend(docItems)

doc_df = pd.DataFrame(docItem_list)

# PDFを取得し、保存
for row in doc_df.iterrows():
    url = f"{ENDPOINT_2}/{row[1]['docID']}"
    params = {"type": 2, "Subscription-Key": API_KEY}  # PDF形式で取得する指定
    response = requests.get(url, params=params, verify=True)
    pdf_file = response.content
    if not os.path.exists("pdf_files"):
        os.mkdir("pdf_files")
    with open(f'pdf_files/{row[1]["会社名"]}{row[1]["書類名"][:2]}.pdf', "wb") as f:
        f.write(pdf_file)

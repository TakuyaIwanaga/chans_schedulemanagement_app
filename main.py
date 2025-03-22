#ルート検索の実装
import requests
import json
#環境変数ファイル呼び出し
import os
from dotenv import load_dotenv
load_dotenv('.env') 

# 🔹 APIキーを環境変数ファイルに設定（自分のキーを環境ファイルに入力）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
BASE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

# ヘッダーx-goog-FieldMask情報により取得するパラメータを指定
headers = {
#出力形式はjsonで取得
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY,
#ここが取得したい情報の指定
    "X-Goog-FieldMask": "routes.legs.steps.transitDetails,routes.legs.steps.travelMode"
}

#ヘッダー情報に応じたパラメータを設定
params = {
     "origin": {
        "address": "Humberto Delgado Airport, Portugal"
        },
        "destination": {
            "address": "Basílica of Estrela, Praça da Estrela, 1200-667 Lisboa, Portugal"
        },
        "travelMode": "TRANSIT",
        "computeAlternativeRoutes": True,
        "transitPreferences": {
            "routingPreference": "LESS_WALKING",
            "allowedTravelModes": ["TRAIN"]
        },
}

#結果をレスポンスに代入
response = requests.post(BASE_URL, headers=headers, json=params)

# 結果の表示　レスポンスが200ならjsonファイルで出力　項目多いので
if response.status_code == 200:
    response_json = response.json()
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(response_json, f, indent=4, ensure_ascii=False)
#レスポンスが200番以外の場合はエラー結果表示
else:
    print(f"Request failed: {response.status_code}")
    print(response.text)





#天気予報実装

#コンセント場所検索実装

#ルート検索の実装
#import streamlit as st
import googlemaps
import requests
import json
from datetime import datetime
#環境変数ファイル呼び出し
import os
from dotenv import load_dotenv

#環境変数呼び出し
load_dotenv('.env') 

# APIキーを環境変数ファイルに設定（自分のキーを環境ファイルに入力）
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
ROUTE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

# Streamlit タイトル
# st.title("🧑‍💼優秀な営業マンのための秘書アプリ👩‍💼")

# 出発地と到着地の入力
origin_address = "羽田空港"
destination_address = "東京駅"

#出発時間の入力
dt = datetime.strptime("2025-3-21-10:00:00", "%Y-%m-%d-%H:%M:%S")
start_time = dt.isoformat() + "Z"

#住所を経度、緯度に変換する関数（geocording）
def get_lat_lng(address):
    result = gmaps.geocode(address, language="ja")
    if result:
        lat = result[0]["geometry"]["location"]["lat"]
        lng = result[0]["geometry"]["location"]["lng"]
        return lat, lng
    else:
        return None, None

#出発地と到着地の経度・緯度を取得
try:
    origin_lat, origin_lng = get_lat_lng(origin_address)
    destination_lat, destination_lng = get_lat_lng(destination_address)

    if origin_lat is None or destination_lat is None:
        print("住所を正しく認識できませんでした。英語表記で入力してください。")
        exit()

    print(f"出発地: {origin_address} → 緯度 {origin_lat}, 経度 {origin_lng}")
    print(f"到着地: {destination_address} → 緯度 {destination_lat}, 経度 {destination_lng}")

except Exception as e:
    print(f"エラー発生: {e}")
    exit()

# 検索ボタン
# if st.button("ルートを検索"):
#     if not GOOGLE_API_KEY:
#         st.error("APIキーが設定されていません。")
#     else:

# ヘッダーx-goog-FieldMask情報により取得するパラメータを指定
headers = {
#出力形式はjsonで取得
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY,
#ここが取得したい情報の指定
    "X-Goog-FieldMask": "routes.legs.steps.transitDetails,routes.legs.steps.travelMode,routes.travelAdvisory.transitFare"
}

#ヘッダー情報に応じたパラメータを設定
params = {
    "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
    "destination": {"location": {"latLng": {"latitude": destination_lat, "longitude": destination_lng}}},
    "travelMode": "TRANSIT",
    "arrivalTime": start_time,
    "computeAlternativeRoutes": True,
    "transitPreferences": {
    "allowedTravelModes": ["SUBWAY"],
    "routingPreference": "FEWER_TRANSFERS"
    },
}

#結果をレスポンスに代入
response = requests.post(ROUTE_URL, headers=headers, json=params)

# APIレスポンスのJSONデータを取得
response_json = response.json()  # 実際のAPIレスポンスを使用

# ルート候補を3つ取得
routes = response_json.get("routes", [])[:3]

if not routes:
    print("ルートが見つかりませんでした。")
    exit()

# ルートを3つ選んで情報を取得して表示（繰り返し処理）
for i, route in enumerate(routes):
    print(f"ルート候補 {i+1}")

    leg = route.get("legs", [])[0]  # 各ルートの詳細情報
    steps = leg.get("steps", [])

    # transitDetails を持つステップのみ抽出
    transit_steps = [step for step in steps if "transitDetails" in step]

    if not transit_steps:
        print("このルートに公共交通機関の情報がありません。")
        continue

    # 出発時間・到着時間の取得
    departure_time_str = transit_steps[0]["transitDetails"]["stopDetails"]["departureTime"]
    arrival_time_str = transit_steps[-1]["transitDetails"]["stopDetails"]["arrivalTime"]

    # 出発地・到着地の取得
    departure_location = transit_steps[0]["transitDetails"]["stopDetails"]["departureStop"]["name"]
    arrival_location = transit_steps[-1]["transitDetails"]["stopDetails"]["arrivalStop"]["name"]

    # 日付・時刻の整形
    departure_time = datetime.fromisoformat(departure_time_str.replace("Z", "+00:00"))
    arrival_time = datetime.fromisoformat(arrival_time_str.replace("Z", "+00:00"))

    date = departure_time.strftime("%Y-%m-%d")
    departure_time_formatted = departure_time.strftime("%H:%M")
    arrival_time_formatted = arrival_time.strftime("%H:%M")

    # 所要時間の計算
    duration = arrival_time - departure_time
    duration_str = str(duration)

    # 経由地の取得（途中の駅をリスト化）
    waypoints = [step["transitDetails"]["stopDetails"]["arrivalStop"]["name"] for step in transit_steps[:-1]]

    # 費用（存在する場合のみ取得）
    fare_info = route.get("travelAdvisory", {}).get("transitFare", {})
    fare = fare_info.get("amount", "不明")
    currency = fare_info.get("currencyCode", "")

    # 出力
    print(f"日付: {date}")
    print(f"出発時刻: {departure_time_formatted}")
    print(f"出発地: {departure_location}")
    print(f"経由地: {', '.join(waypoints) if waypoints else 'なし'}")
    print(f"到着地: {arrival_location}")
    print(f"所要時間: {duration_str}")
    print(f"費用: {fare} {currency}")

# JSONを保存
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(response_json, f, indent=4, ensure_ascii=False)

print("ルート検索完了！")


    #Streamlitで表示
    # st.write("おすすめルートはこちら！")
    # st.info(response_json)  # JSONを整形表示
#レスポンスが200番以外の場合はエラー結果表示

# else:
#         st.write(f"APIリクエスト失敗: {response.status_code}")
#         st.text(response.text)  # エラー内容を表示



#天気予報実装

#コンセント場所検索実装

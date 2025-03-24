#----------------
#ルート提案の実装
#----------------
#import streamlit as st
import googlemaps
import requests
import json
#import folium
#from streamlit_folium import st_folium
#環境変数ファイル呼び出し
import os
from dotenv import load_dotenv

#環境変数呼び出し
load_dotenv('.env') 

# GeocodingのAPIキー
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
# NAVITIMEのAPIキー
NAVITIME_API_KEY = os.environ.get("NAVITIME_API_KEY")


#入力変数 ※フロントエンド実装の際は以下を取得-----------------
# 出発地と到着地の入力（駅名）
start_address = "浜松町"
goal_address = "新宿"

#出発時間の入力（文字列（日付時刻）YYYY-MM-DDThh:mm:s）
start_time = "2025-03-21T10:00:00"
goal_time = ""

#検索優先順位のオーダー（以下から選択）
order = "time_optimized"

#     "time_optimized"        #時刻順
#     "total_distance"        #総移動距離
#     "walk_distance"         #総徒歩移動距離
#     "fare"                  #料金
#     "time"                  #所要時間
#     "transit"               #乗換回数
#     "commuter_pass_price"   #定期券運賃
#     "co2"                   #二酸化炭素排出量"



#------------------------------------------------------


#経度・緯度取得_geo coding--------------
#住所を経度、緯度に変換する関数（geocording）
def get_lat_lon(address):
    result = gmaps.geocode(address, language="ja")
    if result:
        lat = result[0]["geometry"]["location"]["lat"]
        lon = result[0]["geometry"]["location"]["lng"]
        return lat, lon
    else:
        return None, None

#出発地と到着地の経度・緯度を取得してrootのパラメータ用変数へ代入
start_lat, start_lon = get_lat_lon(start_address)
goal_lat, goal_lon = get_lat_lon(goal_address)

#入力内容不備の場合にエラーで返す。
if start_lat is None or goal_lat is None:
    print("住所認識エラー")
    exit()

#経度緯度取得確認用--------------------------------------------------
# print(f"出発地: {start_address} 緯度 {start_lat}, 経度 {start_lon}")
# print(f"到着地: {goal_address} 緯度 {goal_lat}, 経度 {goal_lon}")
#-----------------------------------------------------------------

#ルート取得---------------------------------------------------------

#NAVITIMEのエンドポイント指定
root_url = "https://navitime-route-totalnavi.p.rapidapi.com/route_transit"

# ヘッダー情報 x-RapidAPI情報から取得
headers = {
    "X-RapidAPI-Key": NAVITIME_API_KEY,
    "X-RapidAPI-Host": "navitime-route-totalnavi.p.rapidapi.com"
}
#ルート検索のパラメータを設定
params = {
    "start": f"{start_lat},{start_lon}",
    "goal": f"{goal_lat},{goal_lon}",
    # "start_time": start_time,
    # "goal_time": goal_time,
    "coord_unit": "degree",
    "datum": "wgs84",
    "order": order,
    "term": "1440",
    "limit": "5",
    "shape": "true",
}
#start_timeまたはgoal_timeどちらかが入力されている場合paramsに入力
if start_time:
    params["start_time"] = start_time
if goal_time:
    params["goal_time"] = goal_time

#------------------------------------------

#結果をレスポンスに代入
response = requests.get(root_url, headers=headers, params=params)

# APIレスポンス確認用----------------------------
# print(f"Request URL: {response.url}")
# print(f"Status Code: {response.status_code}")
# print(f"Response Headers: {response.headers}")
#---------------------------------------------

#APIレスポンスの結果がNGの場合、エラー出力の確認用----------------------------------------------
if response.status_code != 200:
    print(f"エラー: APIリクエストが失敗しました (ステータスコード: {response.status_code})")
    print("レスポンス内容:", response.text)
    exit()
    
try:
        response_json = response.json()
        print("APIレスポンス成功")
except requests.exceptions.JSONDecodeError:
    print("エラー: JSONデータをデコードできません。")
    print("レスポンス内容:", response.text)
    exit()
#---------------------------------------------------------------------------------------

#jsonの結果から必要な項目のResponseを5つ取り出す関数
def extract_route_info(response_json, top_n=5):
    routes = response_json.get("items", [])[:top_n]
    extracted_routes = []

    for route in routes:
        sections = route.get("sections", [])
        stations = [s for s in sections if s.get("type") == "point" and "station" in s.get("node_types", [])]

        if not stations:
            print("データがありません")
            continue

        # 出発時間と到着時間
        start_time = (route.get("summary", {}).get("move", {}).get("from_time", ""))
        goal_time = (route.get("summary", {}).get("move", {}).get("to_time", ""))

        # 出発駅・到着駅を取得
        start_station = stations[0].get("name", "")
        goal_station = stations[-1].get("name", "")

        # 乗換駅の取得
        transfer_stations = [s.get("name", "") for s in stations[1:-1]]

        # 所要時間（分）
        duration = route.get("summary", {}).get("move", {}).get("time", "")

        # 費用（円）
        fare = route.get("summary", {}).get("move", {}).get("fare", {}).get("unit_0", "")

        extracted_routes.append({
            "出発時刻": start_time,
            "到着時刻": goal_time,
            "出発駅": start_station,
            "到着駅": goal_station,
            "乗換駅": transfer_stations,
            "所要時間": duration,
            "費用": fare
        })
    
    return extracted_routes

best_routes = extract_route_info(response_json)

# ルート情報を出力
if best_routes:
    for i, route in enumerate(best_routes, 1):
        print(f"ルート {i}:")
        print(f"  出発時刻: {route['出発時刻']}")
        print(f"  到着時刻: {route['到着時刻']}")
        print(f"  出発駅: {route['出発駅']}")
        print(f"  到着駅: {route['到着駅']}")
        print(f"  乗換駅: {', '.join(route['乗換駅']) if route['乗換駅'] else 'なし'}")
        print(f"  所要時間: {route['所要時間']} 分")
        print(f"  費用: {route['費用']} 円")
        print("-" * 30)
else:
    print("ルートが取得できませんでした。")


#出力確認用にJSONを保存
# with open("result.json", "w", encoding="utf-8") as f:
#     json.dump(response_json, f, indent=4, ensure_ascii=False)

#地図への作図 Streamlit----------------------------------------------------------------
# shapes = response_json["items"][0]["shapes"]

# #地図の生成
# point_geojson = shapes
# folium_map = folium.Map(location=[35.690921, 139.700258], zoom_start=15)
# st.title("地図")

# #地図表示
# st_folium(folium_map)

#------------------------------------------------------------------------------------

#------------------
#天気予報実装
#------------------


#------------------
#コンセント場所検索実装
#------------------


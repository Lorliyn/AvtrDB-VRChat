from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # 允许跨域，Udon直接访问

# 你抓包拿到的全套请求头，固定写在这里
AVTRDB_HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "origin": "https://avtrdb.com",
    "priority": "u=1, i",
    "referer": "https://avtrdb.com/",
    "sec-ch-ua": '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0"
}

# 简易限流：记录上一次请求时间，防止高频轰炸avtrdb
last_req_time = 0
MIN_INTERVAL = 1.5 # 两次请求最少间隔1.5秒

@app.route('/api/search')
def avatar_search():
    global last_req_time
    now = time.time()
    if now - last_req_time < MIN_INTERVAL:
        return jsonify({"error":"请求太频繁，请稍后再试"}),429
    last_req_time = now

    # 从Udon传来的三个参数
    query = request.args.get("query")
    page = request.args.get("page", 0)
    page_size = request.args.get("page_size",14)

    if not query:
        return jsonify({"error":"缺少query搜索词"}),400

    params = {
        "query": query,
        "page": page,
        "page_size": page_size
    }
    try:
        resp = requests.get(
            "https://api.avtrdb.com/v2/avatar/search",
            params=params,
            headers=AVTRDB_HEADERS,
            timeout=10
        )
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error":str(e)}),500

# 测试根路由，浏览器打开看服务是否在线
@app.route('/')
def index():
    return "AvtrDB Proxy OK | 接口地址 /api/search?query=关键词&page=0"

if __name__ == '__main__':
    # Render等云平台会自动注入PORT环境变量
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

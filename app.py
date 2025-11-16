from flask import Flask, request, jsonify
app = Flask(__name__)

# --- 簡易デモ用データ（本番は外部API or 正規データベースに差し替え） ---
stations = [
    {"code":"umeda","name":"梅田"},
    {"code":"juso","name":"十三"},
    {"code":"sannomiya","name":"三宮"},
    {"code":"kawaramachi","name":"河原町"},
    # 実際は阪急の全駅を用意する（公式サイトやAPIで取得）
]

# 簡易グラフ（無向、有向は路線に合わせて調整）
graph = {
    "umeda": [("juso",150), ("kawaramachi",400)], # (隣駅, 運賃想定)
    "juso": [("umeda",150), ("sannomiya",300)],
    "sannomiya": [("juso",300)],
    "kawaramachi": [("umeda",400)]
}

import heapq

def dijkstra(start, goal):
    q = [(0, start, [start])]
    seen = {start:0}
    while q:
        cost, node, path = heapq.heappop(q)
        if node == goal:
            return cost, path
        for nei, w in graph.get(node,[]):
            nc = cost + w
            if nei not in seen or nc < seen[nei]:
                seen[nei] = nc
                heapq.heappush(q, (nc, nei, path + [nei]))
    return None, []

@app.route('/stations')
def get_stations():
    return jsonify(stations)

@app.route('/route', methods=['POST'])
def route():
    body = request.get_json()
    frm = body.get('from')
    to = body.get('to')
    # デモ: dijkstraで最短（運賃）を返す
    fare, path = dijkstra(frm, to)
    if fare is None:
        return jsonify({"error":"経路が見つかりません"}), 404
    # 実運用: ここで駅すぱあと等のAPIを叩いて正確な運賃・所要時間・乗換を得る
    return jsonify({
        "from": frm,
        "to": to,
        "fare": int(fare/100)*100 if fare else 0,  # デモ調整
        "path": path,
        "note": "デモ用の簡易計算です。本番は駅すぱあと等APIを推奨"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
import hashlib
import json
import requests

class KuaiDi100:
    def __init__(self, key, customer):
        self.key = key
        self.customer = customer
        self.url = 'https://poll.kuaidi100.com/poll/query.do'

    def track(self, com, num, phone='', ship_from='', ship_to=''):
        param = {
            "com": com,
            "num": num,
            "phone": phone,
            "from": ship_from,
            "to": ship_to,
            "resultv2": "1",
            "show": "0",
            "order": "desc"
        }
        param_str = json.dumps(param, separators=(",", ":"), ensure_ascii=False)
        sign_text = param_str + self.key + self.customer
        md5 = hashlib.md5()
        md5.update(sign_text.encode('utf-8'))
        sign = md5.hexdigest().upper()

        payload = {
            'customer': self.customer,
            'param': param_str,
            'sign': sign
        }

        try:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(self.url, data=payload, headers=headers, timeout=15)
            return response.json()
        except Exception as e:
            return {"status": "error", "msg": str(e)}


# ================== 配置区（请替换为你的信息）==================
KEY = "LiYvcWLX7776"          # ← 你的 Key
CUSTOMER = "83F9C527E1E29C4EB914FCCFE32BAD56"  # ← 你的 Customer
kd_api = KuaiDi100(KEY, CUSTOMER)

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    number = data.get('number')
    com = data.get('com', 'auto')

    if not number:
        return jsonify({"code": -1, "msg": "请输入快递单号"})

    result = kd_api.track(com=com, num=number)

    if isinstance(result, dict) and result.get("status") == "200" and result.get("nu"):
        traces = result.get("data", [])
        history = []
        for item in traces:
            history.append({
                "time": item["time"],
                "context": item["context"]
            })
        return jsonify({
            "success": True,
            "message": "查询成功",
            "data": {
                "company": result.get("com", "unknown"),
                "number": result.get("nu"),
                "state": result.get("state"),
                "history": history
            }
        })
    elif "msg" in result:
        return jsonify({"success": False, "message": result['msg']})
    else:
        return jsonify({"success": False, "message": "网络错误，请检查连接"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
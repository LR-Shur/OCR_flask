from flask import jsonify

def create_response(code, message, data=None):
    # 确保 data 是一个字典
    if data is None or not isinstance(data, dict):
        data = {}
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    })



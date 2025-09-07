from flask import Flask, make_response

# 初始化Flask应用实例
app = Flask(__name__)

# 定义API路由，默认支持GET请求
@app.route('/api/helloworld', methods=['GET'])
def hello_world():
    response = make_response("helloworld")
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    print("API /api/helloworld 被访问")
    return response

# 定义页面路由，默认支持GET请求
@app.route('/test', methods=['GET'])
def test():
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    print("API /test 被访问")
    return response

# 404错误处理
@app.errorhandler(404)
def page_not_found(e):
    response = make_response("请求的API路径不存在", 404)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    print("404错误：请求的API路径不存在")
    return response

# 500错误处理
@app.errorhandler(500)
def internal_server_error(e):
    response = make_response("服务器内部错误", 500)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    print("500错误：服务器内部错误")
    return response

# if __name__ == '__main__':
#     app.run(debug=False, host='0.0.0.0', port=5000)
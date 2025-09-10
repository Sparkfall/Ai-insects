from flask import Flask, request, jsonify, make_response,send_file
from flask_cors import CORS
import os
# import psycopg2
# from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)
cameraList = ['camera1','camera2']
# app.config['SECRET_KEY'] = '3b6dc7732e7647d85f0dcbb44b337b504d1cc03870a358d290f14409bb912217'  

# def get_db_connection():
#     conn = psycopg2.connect(
#         dbname='insect',
#         user='postgres',
#         password="admin",
#         host='localhost',
#         port='7890'
#     )
#     return conn

# def execute_query(query, params=None):
#     conn = get_db_connection()
#     cursor = conn.cursor(cursor_factory=RealDictCursor)
#     cursor.execute(query, params)
#     conn.commit()
#     result = cursor.fetchall() if cursor.rowcount > 1 else cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return result

# 定义API路由，默认支持GET请求
@app.route('/api/helloworld', methods=['GET'])
def hello_world():
    response = make_response("helloworld")
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    print("API /api/helloworld 被访问")
    return response

# 定义listfile请求，返回文件目录
@app.route('/api/listfile', methods=['POST'])
def listfile():
    print('api/listfile Accessed.')
    data = request.json
    status = 'error'
    message = ''
    try:
        cameraID, date = data['cameraID'],data['date']
        dir_path = "images/" + cameraID
        if cameraID in cameraList:
            Date_items = os.listdir(dir_path)
            if date in Date_items:
                items = os.listdir(f"{dir_path}/{date}")
                status = 'success'
                message = items
            else:
                message = 'Date doesn\'t exist!'
        else:
            message = 'Camera doesn\'t exist!'
    except:
        message = 'request Params missing.'
    return jsonify({'status':status,'message':message})

# 定义getfile请求，返回文件目录
@app.route('/api/getfile', methods=['POST'])
def getfile():
    print('api/getfile Accessed.')
    data = request.json
    try:
        cameraID, date, filename = data['cameraID'],data['date'],data['filename']
        dir_path = f"../images/{cameraID}/{date}/{filename}"
        return send_file(dir_path, mimetype='image/jpeg')
    except:
        return jsonify({'status':'error','message':'File doesn\'t exist.'})
    

# 定义页面路由，默认支持GET请求
@app.route('/test', methods=['GET'])
def test():
    with open('index.html', 'rb', encoding='utf-8') as f:
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
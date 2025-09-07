from waitress import serve
from api_test import app

host = "0.0.0.0"
port = 8088

if __name__ == "__main__":
    print(f"生产环境服务已启动：http://{host}:{port}")
    # 配置生产环境参数
    serve(
        app,
        host=host,    # 允许外部访问
        port=port,         # 服务端口
        threads=4,         # 并发线程数（建议设为CPU核心数*2，如4核设8）
        connection_limit=1000  # 最大连接数（根据需求调整）
    )
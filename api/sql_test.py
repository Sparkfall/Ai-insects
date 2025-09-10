import mysql.connector
from mysql.connector import Error

def connect_mysql_local(host='172.28.137.235',port=3306, user='your_username', password='your_password', database='your_database'):
    """
    建立本地 MySQL 数据库连接
    :param host: 数据库主机地址（本地默认 localhost）
    :param user: 数据库用户名
    :param password: 数据库密码
    :param database: 要连接的数据库名
    :return: 数据库连接对象（成功）或 None（失败）
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset='utf8mb4'
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"成功连接 MySQL 服务器（版本：{db_info}）")
            
            # 获取当前数据库游标
            cursor = connection.cursor(dictionary=True)  # dictionary=True 使结果以字典形式返回
            return connection, cursor

    except Error as e:
        print(f"连接失败：{e}")
        return None, None

def execute_query(cursor, query, params=None):
    """
    执行 SQL 查询
    :param cursor: 数据库游标对象
    :param query: SQL 查询语句
    :param params: 查询参数（用于参数化查询，防止 SQL 注入）
    :return: 查询结果（SELECT 语句）或受影响行数（INSERT/UPDATE/DELETE）
    """
    try:
        # 执行查询（参数化查询，避免 SQL 注入）
        cursor.execute(query, params or ())
        
        # 判断是否为查询类语句（SELECT/SHOW 等）
        if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
            result = cursor.fetchall()  # 获取所有查询结果
            print(f"查询成功，共返回 {len(result)} 条数据")
            return result
        else:
            # 非查询语句（INSERT/UPDATE/DELETE）需要提交事务
            connection.commit()
            affected_rows = cursor.rowcount  # 获取受影响行数
            print(f"执行成功，受影响行数：{affected_rows}")
            return affected_rows

    except Error as e:
        # 执行失败回滚事务
        connection.rollback()
        print(f"查询执行失败：{e}")
        return None

if __name__ == "__main__":
    # --------------------------
    # 1. 配置本地 MySQL 连接信息（请根据实际情况修改）
    # --------------------------
    MYSQL_CONFIG = {
        'host':'122.112.224.186',
        'port':5432,
        'user': 'spark',          # 你的 MySQL 用户名（如 root）
        'password': '123a456b',    # 你的 MySQL 密码
        'database': 'insect'    # 你要操作的数据库名
    }

    # --------------------------
    # 2. 建立数据库连接
    # --------------------------
    connection, cursor = connect_mysql_local(**MYSQL_CONFIG)
    if not connection or not cursor:
        print("数据库连接失败，程序退出")
        exit()

    try:
        # --------------------------
        # 3. 示例 1：执行 SELECT 查询（查询表数据）
        # --------------------------
        print("\n=== 示例 1：查询 users 表数据 ===")
        select_query = "SELECT filename, cameraID, date FROM image WHERE cameraID = %s"
        select_params = ('camera1',)  # 参数化查询，%s 为占位符（与 Python 格式化不同）
        # select_query = "SELECT * FROM image"
        query_result = execute_query(cursor, select_query)
        
        # 打印查询结果
        if query_result:
            for idx, row in enumerate(query_result, 1):
                print(f"第 {idx} 条：ID={row['filename']}, cameraID={row['cameraID']}, date={row['date']}")

        # --------------------------
        # 4. 示例 2：执行 INSERT 操作（插入数据）
        # # --------------------------
        # print("\n=== 示例 2：插入数据到 users 表 ===")
        # insert_query = "INSERT INTO users (username, age, email) VALUES (%s, %s, %s)"
        # insert_params = ("new_user", 25, "new_user@example.com")
        # execute_query(cursor, insert_query, insert_params)

        # --------------------------
        # 5. 示例 3：执行 UPDATE 操作（更新数据）
        # --------------------------
        # print("\n=== 示例 3：更新 users 表数据 ===")
        # update_query = "UPDATE users SET age = %s WHERE username = %s"
        # update_params = (26, "new_user")
        # execute_query(cursor, update_query, update_params)

    finally:
        # --------------------------
        # 6. 关闭连接（必须执行，避免资源泄漏）
        # --------------------------
        cursor.close()
        if connection.is_connected():
            connection.close()
            print("\nMySQL 连接已关闭")
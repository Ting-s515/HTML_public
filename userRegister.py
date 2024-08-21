from flask import Flask, render_template, jsonify, request,session,redirect
import pyodbc

app = Flask(__name__)
#要留著
app.config['TEMPLATES_AUTO_RELOAD'] = True #每次刷新session
# 要留著
app.secret_key = 'P@ssw@rd' #為了安全性，這個密鑰應該設置得複雜且難以猜測
#模擬的用戶資料
# users = {
#     'ted@gmail.com': 'qwe123'
# }
# 連接到 SQL Server 的函數
def save_member_to_sql(data):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=172.17.100.209;'
        'DATABASE=用戶註冊;'
        'UID=sa;'
        'PWD=12345'
    )
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO register (name, email, password, phone)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['email'], data['password'], data['phone']))
    conn.commit()
    conn.close()
#獲取用戶的email password
def user_information(email, password):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=172.17.100.209;'
        'DATABASE=用戶註冊;'
        'UID=sa;'
        'PWD=12345'
    )
    #查詢資料庫用戶資料
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM register WHERE email = ? AND password = ?
    ''', (email, password))
    user_row = cursor.fetchone()
    conn.close()
    if user_row:
    # 将 Row 对象转换为字典
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, user_row))
        return user
    return None

# 定義根路徑顯示首頁
@app.route('/')
def index():
      # 從 session 中獲取用戶資訊
    user = session.get('user') 
    return render_template('citybreak.html', user=user)

# 定義路由來顯示會員註冊頁面
@app.route('/userRegister', methods=['GET'])
def register_page():
    return render_template('userRegister.html')
# 定義路由來處理會員註冊
@app.route('/userRegister', methods=['POST'])
def register():
    data = request.get_json()
    try:
        save_member_to_sql(data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

#顯示會員登入頁面get
@app.route('/userLogin', methods=['GET'])
def login_page():
    return render_template('userLogin.html')
#處理會員登入post
@app.route('/userLogin', methods=['POST'])
def login():
    data = request.get_json()  # 从JSON请求中获取数据
    email = data.get('email')
    password = data.get('password')
    user = user_information(email, password)
    if user:
        # 登錄成功，返回JSON响应
        # 設置 session 並返回成功消息
        session['user'] = user
        return jsonify({'status': 'success'}), 200
    else:
        # 登錄失敗，返回錯誤消息
        return jsonify({'status': 'error', 'message': '登入失敗，請檢查您的帳號或密碼。'}), 401

# 定義會員登出功能
@app.route('/logout')
def logout():
    session.pop('user', None)  # 清除 session 中的用戶資訊
    return redirect('/citybreak')
# return redirect('/citybreak'): 這會使瀏覽器發送一個新的 HTTP 請求到 /citybreak
# ，並由服務器返回該頁面。這是一個標準的重定向方法，確保瀏覽器地址欄會更新為 /citybreak。

# return render_template('citybreak.html'): 這會直接返回 citybreak.html 頁面的內容，
# 而不改變瀏覽器的 URL。這對於重新渲染當前頁面或在某些情況下直接顯示頁面內容是有效的

# 定義路由來顯示 citybreak 頁面
@app.route('/citybreak')
def citybreak():
    return render_template('citybreak.html')

# 定義路徑來顯示 clothes.html
@app.route('/clothes')
def clothes():
    return render_template('clothes.html')

# 定義路徑來顯示 clothes.html
@app.route('/backpack')
def backpack():
    return render_template('backpack.html')

# 定義路徑來顯示 clothes.html
@app.route('/outdoor_litems')
def outdoor_litems():
    return render_template('outdoor_litems.html')

# 定義路徑來顯示 clothes.html
@app.route('/equipment裝備')
def equipment():
    return render_template('equipment裝備.html') 
   
if __name__ == '__main__':
    app.run(debug=True)

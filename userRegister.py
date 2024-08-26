#每一個網頁分別做一個route，GET POST要分開做
from flask import Flask, render_template, jsonify, request,session,redirect
import pyodbc

app = Flask(__name__)
#要留著
app.config['TEMPLATES_AUTO_RELOAD'] = True #每次刷新session
# 要留著
app.secret_key = 'P@ssw@rd' #為了安全性，這個密鑰應該設置得複雜且難以猜測
def sql_connect():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=172.22.220.207;'
        'DATABASE=用戶註冊;'
        'UID=sa;'
        'PWD=12345'
    )
     # 返回 cursor 物件，用於執行 SQL 語句
    return conn.cursor()
# 定義建構子連接到 SQL Server 的函數
def save_member_to_sql(data):
    cursor=sql_connect() # 調用方法獲取 cursor
    print('data= ',data)#前端傳送json
    cursor.execute('''
        INSERT INTO 客戶資料 (姓名, 信箱, 密碼, 手機)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['email'], data['password'], data['phone']))
    #data={'key':'value','key':'value','key':'value','key':'value'}
    print(data['name'], data['email'], data['password'], data['phone'])
    cursor.commit()
    cursor.close()
#定義建構子獲取用戶的email password
def user_information(email, password):
    #查詢資料庫用戶資料
    cursor = sql_connect()
    cursor.execute('''
        SELECT * FROM 客戶資料 WHERE 信箱 = ? AND 密碼 = ?
    ''', (email, password))
    # 獲取第一列的資料
    columns = [column[0] for column in cursor.description]
    print('columns= ',columns)
    user_row = cursor.fetchone() #fetchone() 方法從查詢結果中獲取第一行數據
    # 在fetchone() 之前調用cursor.description 來取得column的資訊，然後將其儲存到 columns 列表中。
    # 這樣在關閉 cursor 之前可以正確存取列名稱。
    #user_row 是一個元組，'+' 運算符不能直接將str和元組tuple拼接。
    print('user row= ',user_row)
    cursor.close()
    if user_row:
    # 将 Row 对象转换为字典
        user = dict(zip(columns, user_row))#user字典(key,value)
        print('user dict= ',user)
        return user
    return None

# 定義根路徑顯示首頁
@app.route('/')
def index():
    # 從 session 中獲取用戶資訊，一個用來存儲特定用戶數據的字典，
    #它的數據在整個用戶登入期間保持有效，即使在不同頁面之間切換  
    user = session.get('user') 
    #用來讀取或獲取已經存儲在 session 中的數據。Flask會找 session 中是否有名為 'user' 的鍵
    return render_template('citybreak.html', user=user)

# 定義路由來顯示會員註冊頁面
@app.route('/userRegister', methods=['GET']) #GET: 用於從資料庫獲取數據。
def register_page():
    return render_template('userRegister.html') 
# 定義路由來處理會員註冊
@app.route('/userRegister', methods=['POST'])# POST: 用於將數據發送到服務器來創建或更新資源。
def register():
    data = request.get_json()#從前端接收到的 HTTP 請求中獲取 JSON 格式的數據
    try:
        save_member_to_sql(data) 
        return jsonify({'status': 'success'}), 200
    #返回一個 JSON 格式的響應，其中包含狀態 status: 'success'
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
    cursor=sql_connect()
    user = user_information(email, password)
    if user:
        # 登錄成功，返回JSON响应
        # 設置 session 並返回成功消息
        session['user'] = user 
        print('session_user= ',session['user'])
        #是用來設定或儲存數據到 session 中。在 session 中創建一個名為 'user' 的鍵，
        # #並將user的值存在這個鍵中。(key value)
        return jsonify({'status': 'success'}), 200
    else:
        # 登錄失敗，返回錯誤消息
        return jsonify({'status': 'error', 'message': '登入失敗，請檢查您的帳號或密碼。'}), 401

# 定義重設密碼功能
@app.route("/resetPassword",methods=['GET'])
def reset_page():
    return render_template('resetPassword.html') 
#POST   
@app.route('/resetPassword',methods=['POST'])
def reset_password():
    data=request.get_json()
    email=data.get('email')
    new_password=data.get('new_password')
    print('email= ',email)
    print('new_password= ',new_password)
    cursor = sql_connect()
    cursor.execute('SELECT * FROM 客戶資料 WHERE 信箱 = ?', (email,))
    user_row = cursor.fetchone()
    if not user_row:
        return jsonify({'status': 'error', 'message': '未找到該信箱對應的用戶。'})

    cursor.execute('''
        UPDATE 客戶資料 SET 密碼=? WHERE 信箱=?
    ''',(new_password,email))
    print('UPDATE pwd= ',new_password)
    cursor.commit()
    cursor.close()
    return jsonify({'status': 'success', 'message': '密碼已成功重設！'})

# 定義會員登出功能
@app.route('/logout')
def logout():
    session.pop('user', None)  # 清除 session 中的用戶資訊
    return redirect('/citybreak')
# return redirect('/citybreak'): 這會使瀏覽器發送一個新的 HTTP 請求到 /citybreak
# ，並由服務器返回該頁面。這是一個標準的重定向方法，確保瀏覽器地址欄會更新為 /citybreak。

# return render_template('citybreak.html'): 這會直接返回 citybreak.html 頁面的內容，
# 而不改變瀏覽器的 URL。這對於重新渲染當前頁面或在某些情況下直接顯示頁面內容是有效的

#搜尋
@app.route('/search_result', methods=['GET'])
def search_products():
    search_text = request.args.get('search', '')
    print('搜尋: ', search_text)
    if not search_text:
        return render_template('search_result.html', results=[],search_text='無此關鍵字')
    cursor = sql_connect()
    cursor.execute('''
        SELECT 商品名稱, 價格,圖片路徑,商品介紹
        FROM 商品資料 
        WHERE 商品名稱 LIKE ?
    ''', (f'%{search_text}%',))
    items = cursor.fetchall()
    print('fetchall_items= ',items)
    results = []
    for item in items:
        results.append({                                
            'name': item[0],
            'price': item[1],
            'image_url': item[2],
            'product_introduction': item[3]  # 商品介紹
        })

    cursor.close()
    return render_template('search_result.html', results=results,search_text=search_text)
    #把results,search_text 結果返回給前端使用

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

@app.route('/search_result')
def search_result():
    return render_template('search_result.html') 

if __name__ == '__main__':
    app.run(debug=True)

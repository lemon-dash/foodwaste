from flask import Flask, request, render_template, send_from_directory,jsonify,session,Response
import redis
import os
import detect_img,detect_video,camera
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
app.secret_key = 'simple_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    if file_path.endswith(('.png', '.jpg', '.jpeg')):
        result = detect_img.detect(s_pth=file_path)
    elif file_path.endswith(('.mp4', '.avi')):
        result = detect_video.detect(v_pth=file_path)
    else:
        return {'message': 'Unsupported file type'}, 400
    names = filename.split('.')
    print(names[0])
    print(names[1])
    return jsonify({'output_pth':f'/static/uploads/{names[0]}_detected.{names[1]}','conclusion':result})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/ivdetect')
def ivdetect():
    return render_template('ivdetect.html')

# 数据库连接函数
# 数据库连接函数
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',  # 数据库主机地址
            user='root',  # 数据库用户名
            password='mysql085231',  # 数据库密码
            database='foodwaste'  # 数据库名称
        )
    except:
        print('数据库连接失败')
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
         # 查询 Users 表是否存在
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username,password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            # 登录成功，存储用户信息到 session
            session['username'] = user['username']
            session['camera_ip'] = user['camera_ip']
            session['password'] = user['password']
            session['camera_password'] = user['camera_password']
            # 返回成功信息和摄像头 IP 地址
            return jsonify({'success': True, 'camera_ip': user['camera_ip'], 'camera_password': user['camera_password']})
        else:
            # 登录失败
            return jsonify({'success': False})
    else:
        return render_template('login.html')

@app.route('/camera_detection',methods=['GET', 'POST'])
def camera_detection():
    if request.method == 'POST':
        data = request.get_json()
        camera_ip = data.get('camera_ip')
        newIp = data.get('newIp')

        if newIp:
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='mysql085231',
                    database='foodwaste'
                )
                cursor = conn.cursor()
                username = session.get('username')
                password = session.get('password')
                # 根据用户名和密码查询用户信息
                query = "SELECT * FROM user WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                user = cursor.fetchone()

                if user:
                    # 更新camera_ip字段
                    update_query = "UPDATE user SET camera_ip = %s WHERE username = %s AND password = %s"
                    cursor.execute(update_query, (camera_ip, username, password))
                    conn.commit()# 根据session['username']查询用户记录

            except :
                return jsonify({'status': 'error','message':'连接数据库问题'})

            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
                camera.detect(camera_ip=camera_ip)
    else:
        return render_template('cdetection.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.detect(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
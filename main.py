import os
import pymysql
import uuid
import base64
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_cors import CORS  # ✅ CORS 추가
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import sys

pymysql.install_as_MySQLdb()
import MySQLdb

load_dotenv()

app = Flask(__name__)
CORS(app)  # ✅ 모든 엔드포인트에 CORS 허용
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key')

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'install')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'P@ssw0rd74')
DB_NAME = os.getenv('DB_NAME', 'installdb')

def get_db():
    return MySQLdb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        passwd=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4',
        cursorclass=MySQLdb.cursors.DictCursor
    )

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    current = session.get('dark_mode', False)
    session['dark_mode'] = not current
    return jsonify(success=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('❌ 로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password_hash = generate_password_hash(request.form['password'])
        email = request.form['email']
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                (username, password_hash, email)
            )
            db.commit()
            db.close()
            flash('✅ 회원가입 성공! 로그인 해주세요.')
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            flash('⚠️ 아이디 또는 이메일이 이미 존재합니다.')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    org = request.args.get('organization', '')
    success = request.args.get('success', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM installation_records WHERE success = '1'")
    success_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM installation_records")
    total_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT DISTINCT organization FROM finish_records")
    org_list = [row['organization'] for row in cursor.fetchall()]

    sql = """
        SELECT id, organization, installer_company, installer_name, date, success
        FROM installation_records
        WHERE 1=1
    """
    params = []
    if org:
        sql += " AND organization LIKE %s"; params.append(f"%{org}%")
    if success:
        sql += " AND success = %s"; params.append(success)
    sql += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(sql, params)
    records = cursor.fetchall()
    db.close()
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('dashboard.html',
                           records=records,
                           success_count=success_count,
                           total_count=total_count,
                           org_list=org_list,
                           current_page=page,
                           total_pages=total_pages)

@app.route('/ajax_dashboard')
def ajax_dashboard():
    if 'user_id' not in session:
        return "Unauthorized", 401
    org = request.args.get('organization', '')
    success = request.args.get('success', '')
    page = int(request.args.get('page', 1))
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    allowed_sort_fields = ['id', 'organization', 'date']
    sort = sort if sort in allowed_sort_fields else 'id'
    order = order if order in ['asc', 'desc'] else 'asc'
    per_page = 50
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM installation_records")
    total_count = cursor.fetchone()['cnt']

    sql = """
        SELECT id, organization, installer_company, installer_name, date, success
        FROM installation_records WHERE 1=1
    """
    params = []
    if org:
        sql += " AND organization LIKE %s"; params.append(f"%{org}%")
    if success:
        sql += " AND success = %s"; params.append(success)
    sql += f" ORDER BY {sort} {order} LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(sql, params)
    records = cursor.fetchall()
    db.close()
    total_pages = (total_count + per_page - 1) // per_page

    return render_template("partials/_record_table.html",
                           records=records,
                           current_page=page,
                           total_pages=total_pages,
                           sort=sort,
                           order=order)

@app.route('/record/<organization>')
def record_detail(organization):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM installation_records WHERE organization = %s", (organization,))
    record = cursor.fetchone()
    db.close()
    if record:
        session['current_org'] = organization
        return render_template("record_detail.html", record=record)
    flash("해당 데이터를 찾을 수 없습니다.")
    return redirect(url_for('dashboard'))

@app.route("/update_field", methods=["POST"])
def update_field():
    field = request.form["field"]
    value = request.form["value"]
    org = session.get("current_org")
    if not org: return "Organization not found", 400
    db = get_db(); cursor = db.cursor()
    cursor.execute(f"UPDATE installation_records SET {field} = %s WHERE organization = %s", (value, org))
    db.commit(); db.close()
    return "OK"

@app.route('/upload_image', methods=['POST'])
def upload_image():
    field = request.form['field']
    org = session.get('current_org')
    if not org: return "Organization not found", 400
    allowed = ['before_image','after_image','vpnspeed_image','router_image']
    if field not in allowed: return "Invalid field", 400
    f = request.files['image']
    filename = f"{org}_{field}.png"
    folder = 'uploads'
    path = os.path.join(app.static_folder, folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f.save(path)
    rel = f"{folder}/{filename}"
    db = get_db(); cur = db.cursor()
    cur.execute(f"UPDATE installation_records SET {field}_path=%s WHERE organization=%s", (rel, org))
    db.commit(); db.close()
    return "OK"

@app.route('/upload_signature', methods=['POST'])
def upload_signature():
    data = request.get_json()
    field = data['field']; org = session.get('current_org')
    if not org: return "Organization not found", 400
    img_data = base64.b64decode(data['dataURL'].split(',')[1])
    filename = f"{org}_{field}.png"
    folder = 'uploads'
    path = os.path.join(app.static_folder, folder, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as wf: wf.write(img_data)
    rel = f"{folder}/{filename}"
    db = get_db(); cur = db.cursor()
    cur.execute(f"UPDATE installation_records SET {field}_path=%s WHERE organization=%s", (rel, org))
    db.commit(); db.close()
    return "OK"

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/license-info')
def license_info():
    return render_template('license_info.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 앱 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

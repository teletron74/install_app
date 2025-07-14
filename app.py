from flask import Flask, request, jsonify, send_from_directory, session
import pymysql
import os
from datetime import datetime
import sys

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
# CORS 설정 (모든 엔드포인트에 대해 허용)
# MariaDB 접속 정보
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_USER = os.environ.get('DB_USER', 'install')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'P@ssw0rd74')
DB_NAME = os.environ.get('DB_NAME', 'installdb')

# 데이터베이스 연결 함수
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}", file=sys.stderr)
        return None

# 파일 저장 디렉토리 설정
# ✅ UPLOAD_FOLDER를 'uploads'로 변경
UPLOAD_FOLDER = 'uploads'
STATIC_UPLOAD_FOLDER = os.path.join('static', UPLOAD_FOLDER)
os.makedirs(STATIC_UPLOAD_FOLDER, exist_ok=True)

# 👇【추가된 유효성 목록 제공 라우트】👇
@app.route('/org_list', methods=['GET'])
def org_list():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "DB 연결 실패"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT organization FROM installation_records ORDER BY organization")
            rows = cursor.fetchall()
            orgs = [row['organization'] for row in rows]
        return jsonify({"organizations": orgs}), 200
    except Exception as e:
        print(f"기관 목록 조회 실패: {e}", file=sys.stderr)
        return jsonify({"error": "기관 목록 로딩 실패"}), 500
    finally:
        conn.close()

# 업로드된 파일은 http://your_server_ip:5000/static/uploads/your_file.png 로 접근 가능
@app.route(f'/static/{UPLOAD_FOLDER}/<filename>')
def uploaded_file(filename):
    return send_from_directory(STATIC_UPLOAD_FOLDER, filename)


# --- REST API 엔드포인트 정의 ---

@app.route('/upload', methods=['POST'])
def upload_pdf():
    print("'/upload' 엔드포인트 호출됨")
    if 'file' not in request.files:
        print("에러: 'file' 파트가 요청에 없음", file=sys.stderr)
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        print("에러: 선택된 파일이 없음", file=sys.stderr)
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(STATIC_UPLOAD_FOLDER, file.filename)

    try:
        file.save(save_path)
        print(f"파일 저장됨: {save_path}")
        return jsonify({"message": "File uploaded successfully", "path": save_path}), 200
    except Exception as e:
        print(f"파일 저장 중 에러: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/submit_installation_form', methods=['POST'])
def submit_installation_form():
    print("\n--- '/submit_installation_form' 엔드포인트 호출됨 ---")
    print(f"수신된 폼 데이터 (request.form): {request.form}")
    print(f"수신된 파일 데이터 (request.files): {request.files}")

    # 1. 텍스트 필드 데이터 추출
    data = {}
    for key, value in request.form.items():
        data[key] = value
    print(f"추출된 텍스트 데이터: {data}")

    organization_name = data.get('organization', 'UnknownOrganization') # 기관명 가져오기, 없으면 기본값

    # 2. 파일 데이터 추출 및 저장
    uploaded_file_paths = {} # DB에 저장할 파일의 서버 내 상대 경로 (uploads/filename 형태)
    file_name_map = {
        'beforeImage': 'before_image', #설치 전 사진',
        'afterImage': 'after_image', #설치 후 사진',
        'vpnImage': 'vpnspeed_image', #VPN 속도 체크',
        'routerImage': 'router_image', #5G 무선 라우터',
        'installerSignature': 'installer_signature', #설치자',
        'confirmerSignature': 'confirmer_signature', #확인자',
        'installationPdf': '설치확인서',
    }

    for file_key, file_obj in request.files.items():
        if file_obj.filename: # 파일이 존재하는 경우에만 처리
            original_ext = os.path.splitext(file_obj.filename)[1] # 원본 확장자 유지
            
            # 새로운 파일명 규칙 적용
            if file_key in file_name_map:
                unique_filename = f"{organization_name}_{file_name_map[file_key]}{original_ext}"
            else:
                # 매핑되지 않은 파일은 기존 타임스탬프 방식 사용
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                base, ext = os.path.splitext(file_obj.filename)
                unique_filename = f"{base}_{timestamp}{ext}"
            
            # 실제 파일 저장 경로 (static/uploads/filename)
            file_save_full_path = os.path.join(STATIC_UPLOAD_FOLDER, unique_filename)
            try:
                file_obj.save(file_save_full_path)
                # ✅ DB에 저장할 경로: 'uploads/filename' 형태로 변경, 구분자도 '/'로 통일
                db_path = os.path.join(UPLOAD_FOLDER, unique_filename).replace('\\', '/')
                uploaded_file_paths[file_key] = db_path
                print(f"파일 저장됨 ({file_key}): {file_save_full_path} (DB 경로: {db_path})")
            except Exception as e:
                print(f"파일 저장 실패 ({file_key}): {e}", file=sys.stderr)
                return jsonify({"error": f"Failed to save file {file_key}: {str(e)}"}), 500
        else:
            uploaded_file_paths[file_key] = None # 파일이 없으면 None으로 기록
    print(f"업로드된 파일 경로 (DB 저장용): {uploaded_file_paths}")

    # 3. DB 스키마에 맞춰 데이터 준비 및 유효성 검사
    try:
        organization = data.get('organization')
        business_name = data.get('business_name')
        provider = data.get('provider')
        department = data.get('department')
        installer_company = data.get('installer_company')
        installer_name = data.get('installer_name')
        requester = data.get('requester')
        officer = data.get('officer')
        install_reason = data.get('install_reason')
        
        # 날짜 형식 변환 (YYYY-MM-DD 또는,"%Y-%m-%d %H:%M:%S")
        date_str = data.get('date')
        if date_str:
            parsed_date = None
            try:
                parsed_date = datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_str, '%Y.%m.%d').date()
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(date_str, '%Y.%m.%d').date()
                    except ValueError as e:
                        print(f"날짜 형식 오류: {date_str}. 예상 형식: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS 또는 YYYY.MM.DD. 에러: {e}", file=sys.stderr)
                        return jsonify({"error": f"Invalid date format: {date_str}. Error: {e}"}), 400
        else:
            parsed_date = None # 날짜가 없을 경우 None

        # 이미지 및 PDF 파일 경로 (저장된 로컬 상대 경로)
        before_image_path = uploaded_file_paths.get('beforeImage')
        after_image_path = uploaded_file_paths.get('afterImage')
        vpnspeed_image_path = uploaded_file_paths.get('vpnImage')
        router_image_path = uploaded_file_paths.get('routerImage')
        installer_signature_path = uploaded_file_paths.get('installerSignature')
        confirmer_signature_path = uploaded_file_paths.get('confirmerSignature')
        installation_pdf_path = uploaded_file_paths.get('installationPdf')

        # 위치 정보 (문자열로 받아서 그대로 저장)
        # ✅ Flutter 앱에서 전송될 필드명과 일치시켜야 함
        location_text = data.get('location_text') # Flutter에서 locationText로 보냄
        latitude = data.get('latitude')
        longitude = data.get('longitude')

    except Exception as e:
        print(f"데이터 준비 중 오류: {e}", file=sys.stderr)
        return jsonify({"error": f"Data preparation error: {str(e)}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE installation_records SET
                business_name = %s,
                provider = %s,
                department = %s,
                installer_company = %s,
                installer_name = %s,
                requester = %s,
                officer = %s,
                install_reason = %s,
                date = %s,
                before_image_path = %s,
                after_image_path = %s,
                location_text = %s,
                latitude = %s,
                longitude = %s,
                installer_signature_path = %s,
                confirmer_signature_path = %s,
                vpnspeed_image_path = %s,
                router_image_path = %s,
                installation_pdf_path = %s
            WHERE organization = %s
            """

            values = (
                business_name, provider, department,
                installer_company, installer_name, requester, officer,
                install_reason, parsed_date, before_image_path,
                after_image_path, location_text, latitude, longitude,
                installer_signature_path, confirmer_signature_path,
                vpnspeed_image_path, router_image_path, installation_pdf_path,
                organization  # 조건절의 WHERE 값은 마지막에
            )

            print(f"실행될 SQL: {sql}")
            print(f"SQL 값: {values}")

            cursor.execute(sql, values)
            conn.commit()
            affected = cursor.rowcount
            print(f"{affected}개의 레코드가 수정됨.")

            return jsonify({
            "message": f"{affected} record(s) updated successfully",
            "received_fields": data,
            "received_files": uploaded_file_paths
        }), 200

    except pymysql.Error as e:
        conn.rollback()
        print(f"데이터베이스 오류 (pymysql.Error): {e}", file=sys.stderr)
        return jsonify({"error": f"Database error occurred. ({e.args[1]})"}), 500
    except Exception as e:
        conn.rollback()
        print(f"서버 처리 중 예상치 못한 오류: {e}", file=sys.stderr)
        return jsonify({"error": f"Server processing error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
            print("데이터베이스 연결 닫힘.")

# Flask 앱 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

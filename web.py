from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import config
from werkzeug.utils import secure_filename
import metaboanalystbot
import llmverfy
from docx import Document
import threading
import uuid
import time
import mammoth

app = Flask(__name__)
tasks = {}
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 設定上傳資料夾
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
# 允許的檔案副檔名
ALLOWED_EXTENSIONS = {'.csv'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
def run_analyst(task_id):
    try:
        csv_path = tasks[task_id]['file_path']
        firstcheck = llmverfy.main(csv_path)
        if firstcheck.find('Pass') != -1:
            word_path = os.path.join(UPLOAD_FOLDER, "檢驗報告.docx")
            with open(word_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
            html_content = result.value 
            print("HTMLword轉檔成功")
            tasks[task_id]['status'] = "完成"
            tasks[task_id]['result'] = html_content
            tasks[task_id]['file_name'] = "檢驗報告.docx"
        else:
            tasks[task_id]['status'] = "LLM檢測資料錯誤"
            tasks[task_id]['result'] = firstcheck
    except Exception as e:
        tasks[task_id]['status'] = "失敗"
        tasks[task_id]['result'] = f"錯誤：{str(e)}"
@app.route('/')
def Home():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
    if "file" not in request.files:
        return jsonify({"message": "沒有檔案"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "檔名為空"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "只允許上傳 .csv 檔案"}), 400

    # 確保檔名安全
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    print(f"檔案已儲存到 {save_path}")

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "進行中", "result": None, "file_path": save_path}

    thread = threading.Thread(target=run_analyst, args=(task_id,))
    thread.start()
    print(task_id)
    return jsonify({"message": "任務已接受", "task_id": task_id})
@app.route("/task_status/<task_id>")
def task_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": "找不到任務"}), 404
    return jsonify(task)
@app.route("/download/<filename>")
def download_file(filename):
    abs_upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(abs_upload_folder, filename, as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)

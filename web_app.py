from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from video_editor import VideoEditor
import tempfile
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'video_uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 限制上传文件大小为500MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov', 'mkv'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 生成唯一的文件名
    filename = secure_filename(file.filename)
    unique_filename = f"{str(uuid.uuid4())}_{filename}"
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    # 保存上传的文件
    file.save(input_path)
    
    # 设置输出文件路径
    output_filename = f"edited_{unique_filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    try:
        # 创建VideoEditor实例并处理视频
        editor = VideoEditor(input_path, output_path)
        success = editor.process_video()
        
        if success:
            # 返回处理后的视频文件名，供后续下载使用
            return jsonify({
                'message': '视频处理成功',
                'filename': output_filename
            })
        else:
            return jsonify({'error': '视频处理失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'处理过程出错: {str(e)}'}), 500
    finally:
        # 清理临时文件
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

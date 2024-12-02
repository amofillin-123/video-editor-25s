from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from video_editor import VideoEditor
import tempfile
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

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
    try:
        if 'video' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400

        # 生成唯一的文件名
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()  # 获取文件扩展名
        unique_filename = f"{str(uuid.uuid4())}{file_ext}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # 保存上传的文件
        file.save(input_path)
        app.logger.info(f'文件已保存到: {input_path}')
        
        # 设置输出文件路径，确保包含扩展名
        output_filename = f"edited_{unique_filename}"  # 现在包含了原始文件的扩展名
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        try:
            # 创建VideoEditor实例并处理视频
            app.logger.info('开始处理视频...')
            editor = VideoEditor(input_path, output_path)
            success = editor.process_video()
            
            if success:
                app.logger.info('视频处理成功')
                # 检查带扩展名和不带扩展名的文件是否存在
                if os.path.exists(output_path):
                    actual_output_path = output_path
                elif os.path.exists(output_path + '.mp4'):
                    actual_output_path = output_path + '.mp4'
                    output_filename = output_filename + '.mp4'
                else:
                    app.logger.error('输出文件不存在')
                    return jsonify({'error': '视频处理失败：输出文件不存在'}), 500
                
                return jsonify({
                    'message': '视频处理成功',
                    'filename': output_filename
                })
            else:
                app.logger.error('视频处理失败')
                return jsonify({'error': '视频处理失败'}), 500
                
        except Exception as e:
            app.logger.error(f'处理过程出错: {str(e)}')
            return jsonify({'error': f'处理过程出错: {str(e)}'}), 500
        finally:
            # 清理临时文件
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                    app.logger.info(f'已删除临时文件: {input_path}')
            except Exception as e:
                app.logger.error(f'删除临时文件失败: {str(e)}')
    except Exception as e:
        app.logger.error(f'上传处理失败: {str(e)}')
        return jsonify({'error': f'上传处理失败: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        # 设置正确的 MIME 类型
        mime_type = 'video/mp4' if ext.lower() == '.mp4' else 'video/quicktime'
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f"edited_video{ext}"  # 确保下载时有正确的扩展名
        )
    return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

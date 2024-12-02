import streamlit as st
import os
from video_editor import VideoEditor
import tempfile

st.set_page_config(
    page_title="25秒自动剪辑工具",
    page_icon="🎬",
    layout="centered"
)

# 设置页面样式
st.markdown("""
    <style>
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        .upload-box {
            border: 2px dashed #cccccc;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .success-message {
            color: #28a745;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# 标题
st.title("25秒自动剪辑工具 🎬")
st.markdown("---")

# 上传视频
st.subheader("第一步：上传视频")
uploaded_file = st.file_uploader("选择要剪辑的视频文件", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    # 创建临时文件来保存上传的视频
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        input_path = tmp_file.name

    # 创建输出文件路径
    output_filename = f"edited_{uploaded_file.name}"
    output_path = os.path.join('output', output_filename)
    
    # 确保输出目录存在
    os.makedirs('output', exist_ok=True)

    # 添加处理按钮
    if st.button("开始处理", key="process_button"):
        with st.spinner('视频处理中...'):
            try:
                # 创建进度条
                progress_bar = st.progress(0)
                
                # 处理视频
                editor = VideoEditor(input_path, output_path)
                success = editor.create_final_video()
                
                # 更新进度条
                progress_bar.progress(100)
                
                if success:
                    st.success("视频处理完成！")
                    
                    # 显示下载按钮
                    with open(output_path, 'rb') as file:
                        st.download_button(
                            label="下载处理后的视频",
                            data=file,
                            file_name=output_filename,
                            mime="video/mp4"
                        )
                else:
                    st.error("视频处理失败，请重试。")
            
            except Exception as e:
                st.error(f"处理过程中出现错误: {str(e)}")
            
            finally:
                # 清理临时文件
                if os.path.exists(input_path):
                    os.unlink(input_path)

# 添加使用说明
with st.expander("使用说明"):
    st.markdown("""
    1. 点击上方的"选择要剪辑的视频文件"按钮上传视频
    2. 支持的视频格式：MP4, MOV, AVI
    3. 程序会自动保留原视频前25秒的音频
    4. 视频画面会随机从原视频中选取片段
    5. 处理完成后可以直接下载
    
    **注意事项：**
    - 建议上传时长大于25秒的视频
    - 处理过程可能需要一些时间，请耐心等待
    - 如果处理失败，请检查视频格式是否正确
    """)

# 添加页脚
st.markdown("---")
st.markdown("Made with ❤️ by Codeium")

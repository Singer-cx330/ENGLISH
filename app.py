import streamlit as st
from openai import OpenAI
import json
import time
import numpy as np
import tempfile
import os
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pyttsx3
import edge_tts
import asyncio
import hashlib
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="英语学习助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 深色主题配色 */
    :root {
        --primary-color: #00a67d;
        --secondary-color: #008255;
        --background-color: #1a1a1a;
        --card-bg: #2d2d2d;
        --text-color: #e0e0e0;
        --border-color: #404040;
        --hover-color: #404040;
    }

    /* 全局样式 */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* 功能卡片样式 */
    .custom-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    /* 结果容器样式 */
    .result-container {
        background: linear-gradient(135deg, #2d2d2d 0%, #363636 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        color: var(--text-color);
    }

    /* 词汇卡片样式 */
    .word-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #363636 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--primary-color);
        color: var(--text-color);
    }

    /* 示例文本样式 */
    .example-text {
        background: #363636;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid var(--primary-color);
        color: var(--text-color);
    }

    /* 进度条样式 */
    .progress-bar {
        background: #363636;
        height: 12px;
        border-radius: 6px;
        margin: 1rem 0;
        overflow: hidden;
    }

    .progress-bar-fill {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    /* 成就卡片样式 */
    .achievement-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #363636 100%);
        color: var(--text-color);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-color);
        transition: transform 0.3s ease;
    }

    .achievement-card:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #363636 0%, #404040 100%);
    }

    /* 计时器显示样式 */
    .timer-display {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* 输入框样式 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #363636 !important;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-color) !important;
        padding: 0.5rem;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(0,166,125,0.2);
    }

    /* 选择框样式 */
    .stSelectbox>div>div>div {
        background-color: #363636 !important;
        border: 2px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-color) !important;
    }

    /* 提示文本样式 */
    .hint-text {
        color: #888;
        font-size: 0.9em;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #363636;
        border-radius: 6px;
    }

    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #363636;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: var(--text-color);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
    }

    /* 侧边栏样式 */
    .sidebar-content {
        background: linear-gradient(180deg, #2d2d2d 0%, #363636 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: var(--text-color);
    }

    /* 展开面板样式 */
    .streamlit-expanderHeader {
        background: #363636;
        border-radius: 8px;
        border: none;
        color: var(--text-color);
    }

    .streamlit-expanderContent {
        border: none;
        background: transparent;
        color: var(--text-color);
    }

    /* 闪卡样式 */
    .flashcard {
        background: linear-gradient(135deg, #2d2d2d 0%, #363636 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        cursor: pointer;
        transition: transform 0.3s ease;
        color: var(--text-color);
        border-left: 4px solid var(--primary-color);
    }

    .flashcard:hover {
        transform: translateY(-5px);
        background: linear-gradient(135deg, #363636 0%, #404040 100%);
    }

    /* 发音指南样式 */
    .pronunciation-guide {
        background: #363636;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: var(--text-color);
        border-left: 4px solid var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

def get_ai_response(prompt, system_prompt=""):
    if not st.session_state.api_key:
        st.error("请先输入API密钥！")
        return None
        
    try:
        client = OpenAI(
            api_key=st.session_state.api_key,
            base_url="https://api.deepseek.com"
        )
        
        # 创建一个空的占位符用于流式输出
        output_placeholder = st.empty()
        full_response = ""
        
        # 发送请求并获取流式响应
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        # 逐步显示响应内容
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                output_placeholder.markdown(full_response + "▌")
        
        # 显示最终完整响应
        output_placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# 添加历史记录功能
def save_to_history(category, content, result):
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'category': category,
        'content': content,
        'result': result
    })
    # 保存用户数据
    st.session_state.user_manager.save_user_data()

# 添加学习进度追踪
def update_progress(category):
    if 'progress' not in st.session_state:
        st.session_state.progress = {
            '写作': 0,
            '口语': 0,
            '词汇': 0,
            '语法': 0
        }
    st.session_state.progress[category] = min(100, st.session_state.progress[category] + 5)

# 添加数据导出功能
def export_history_to_csv():
    if 'history' in st.session_state and st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        return df.to_csv(index=False).encode('utf-8')
    return None

# 添加学习时长追踪
def update_study_time(category):
    if 'study_time' not in st.session_state:
        st.session_state.study_time = {}
    current_date = datetime.now().strftime('%Y-%m-%d')
    if current_date not in st.session_state.study_time:
        st.session_state.study_time[current_date] = {}
    if category not in st.session_state.study_time[current_date]:
        st.session_state.study_time[current_date][category] = 0
    st.session_state.study_time[current_date][category] += 5  # 假设每次使用花费5分钟

# 生成学习报告
def generate_study_report():
    if 'study_time' in st.session_state:
        # 转换数据为DataFrame
        data = []
        for date, categories in st.session_state.study_time.items():
            for category, minutes in categories.items():
                data.append({
                    'date': date,
                    'category': category,
                    'minutes': minutes
                })
        if data:
            df = pd.DataFrame(data)
            
            # 创建时间趋势图
            fig_trend = px.line(df, x='date', y='minutes', color='category',
                              title='学习时间趋势')
            st.plotly_chart(fig_trend)
            
            # 创建类别分布饼图
            fig_pie = px.pie(df, values='minutes', names='category',
                           title='学习时间分布')
            st.plotly_chart(fig_pie)
            
            return df
    return None

# 添加学习目标追踪
def set_learning_goals():
    if 'learning_goals' not in st.session_state:
        st.session_state.learning_goals = {
            '写作': {'daily': 30, 'achieved': 0},
            '口语': {'daily': 20, 'achieved': 0},
            '词汇': {'daily': 50, 'achieved': 0},
            '语法': {'daily': 15, 'achieved': 0}
        }

# 添加成就系统
def check_achievements():
    if 'achievements' not in st.session_state:
        st.session_state.achievements = {
            '初学者': False,
            '勤奋学习者': False,
            '词汇大师': False,
            '写作能手': False
        }
    
    # 检查并更新成就
    if 'study_time' in st.session_state:
        total_time = sum(sum(times.values()) for times in st.session_state.study_time.values())
        if total_time >= 60 and not st.session_state.achievements['初学者']:
            st.session_state.achievements['初学者'] = True
            st.balloons()
            st.success("🎉 解锁成就：初学者！")

# 添加专注模式计时器
def focus_timer():
    if 'timer' not in st.session_state:
        st.session_state.timer = {
            'running': False,
            'start_time': None,
            'duration': 25  # 默认25分钟
        }
    
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.session_state.timer['duration'] = st.slider('专注时长(分钟)', 5, 60, 25)
    with col2:
        if st.button('开始专注' if not st.session_state.timer['running'] else '结束专注'):
            if not st.session_state.timer['running']:
                st.session_state.timer['running'] = True
                st.session_state.timer['start_time'] = time.time()
            else:
                st.session_state.timer['running'] = False
                st.session_state.timer['start_time'] = None

    if st.session_state.timer['running']:
        elapsed = time.time() - st.session_state.timer['start_time']
        remaining = st.session_state.timer['duration'] * 60 - elapsed
        if remaining <= 0:
            st.success("🎉 专注时间结束！")
            st.session_state.timer['running'] = False
        else:
            mins, secs = divmod(int(remaining), 60)
            st.markdown(f"""
            <div class="timer-display">
                {mins:02d}:{secs:02d}
            </div>
            """, unsafe_allow_html=True)

# 添加学习计划生成器
def generate_study_plan():
    if 'study_plan' not in st.session_state:
        st.session_state.study_plan = {
            'daily_tasks': [],
            'weekly_goals': [],
            'monthly_targets': []
        }
    
    # 基于用户进度和学习历史生成计划
    if 'progress' in st.session_state and 'study_time' in st.session_state:
        weak_areas = []
        for category, value in st.session_state.progress.items():
            if value < 50:  # 进度低于50%的领域需要加强
                weak_areas.append(category)
        
        return {
            'focus_areas': weak_areas,
            'daily_time': 30,  # 建议每日学习时间（分钟）
            'priority_tasks': [f"加强{area}学习" for area in weak_areas]
        }
    return None

# 添加智能复习提醒系统
def check_review_needed():
    if 'last_review' not in st.session_state:
        st.session_state.last_review = {}
    
    current_time = datetime.now()
    review_items = []
    
    # 检查词汇复习
    if 'vocabulary' in st.session_state:
        for word in st.session_state.vocabulary:
            last_review = st.session_state.last_review.get(word['word'], None)
            if last_review is None or (current_time - last_review).days >= 3:
                review_items.append({
                    'type': '词汇',
                    'content': word['word'],
                    'days_passed': (current_time - last_review).days if last_review else 'New'
                })
    
    return review_items

# 添加学习竞赛系统
def update_leaderboard():
    if 'leaderboard' not in st.session_state:
        st.session_state.leaderboard = []
    
    if 'study_time' in st.session_state:
        total_time = sum(sum(times.values()) for times in st.session_state.study_time.values())
        st.session_state.leaderboard.append({
            'user': '当前用户',
            'total_time': total_time,
            'achievements': len([a for a in st.session_state.achievements.values() if a])
        })

# 在口语练习指导部分添加语音识别功能
def add_speech_recognition():
    st.markdown("""
    <div class="pronunciation-guide">
        <h3>🎤 语音练习</h3>
        <p>1. 输入要练习的文本</p>
        <p>2. 听标准发音</p>
        <p>3. 跟读练习</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 示例文本
    sample_text = st.text_area(
        "练习文本",
        value="The quick brown fox jumps over the lazy dog.",
        height=100
    )
    
    if st.button("播放标准发音 🔊"):
        audio_file = asyncio.run(text_to_speech(sample_text))
        if audio_file:
            st.audio(audio_file)
            try:
                os.unlink(audio_file)
            except:
                pass
    
    # AI 发音建议
    if st.button("获取发音技巧"):
        system_prompt = f"""
        请为以下文本提供详细的发音指导：
        {sample_text}
        
        包含：
        1. 重点音素分析
        2. 重音和语调建议
        3. 常见发音错误提醒
        4. 练习方法建议
        """
        evaluation = get_ai_response("", system_prompt)
        st.markdown("### 🎯 发音指导")
        st.markdown(evaluation)

# 修改文本转语音函数
async def text_to_speech(text, lang='en'):
    temp_file = None
    try:
        # 根据语言选择合适的声音
        if lang == 'en':
            voice = "en-US-EricNeural"
        elif lang == 'zh':
            voice = "zh-CN-YunxiNeural"
        else:
            voice = "en-US-EricNeural"
        
        # 创建通信对象
        communicate = edge_tts.Communicate(text, voice)
        
        # 使用唯一的临时文件名
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', prefix='tts_')
        await communicate.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        st.error(f"语音合成失败: {str(e)}")
        return None

# 在词汇学习部分修改播放功能
def play_audio(word):
    audio_file = None
    try:
        audio_file = asyncio.run(text_to_speech(word, lang='en'))
        if audio_file:
            st.audio(audio_file)
            # 等待一段时间确保音频加载完成
            import time
            time.sleep(2)
    except Exception as e:
        st.error(f"播放失败: {str(e)}")
    finally:
        # 清理临时文件
        if audio_file and os.path.exists(audio_file):
            try:
                os.unlink(audio_file)
            except Exception as e:
                pass

# 添加学习笔记系统
class NoteSystem:
    def __init__(self):
        if 'notes' not in st.session_state:
            st.session_state.notes = {
                '写作': [],
                '口语': [],
                '词汇': [],
                '语法': []
            }
    
    def add_note(self, category, title, content):
        note = {
            'title': title,
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tags': []
        }
        st.session_state.notes[category].append(note)
    
    def display_notes(self, category=None):
        if category:
            notes = st.session_state.notes[category]
        else:
            notes = [note for notes in st.session_state.notes.values() for note in notes]
        
        for note in sorted(notes, key=lambda x: x['timestamp'], reverse=True):
            with st.expander(f"{note['title']} - {note['timestamp']}"):
                st.markdown(note['content'])
                # 添加编辑和删除按钮
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("删除", key=f"del_{note['timestamp']}"):
                        notes.remove(note)
                        st.success("笔记已删除")

# 添加智能学习路径规划
def generate_learning_path():
    if 'learning_path' not in st.session_state:
        st.session_state.learning_path = {
            'current_level': 'beginner',
            'target_level': 'advanced',
            'milestones': [],
            'completed_steps': []
        }
    
    # 基于用户当前水平和目标生成学习路径
    levels = {
        'beginner': ['基础词汇', '简单对话', '基础语法'],
        'intermediate': ['进阶词汇', '日常交流', '复杂语法'],
        'advanced': ['专业词汇', '流利表达', '学术写作']
    }
    
    current_skills = levels[st.session_state.learning_path['current_level']]
    target_skills = levels[st.session_state.learning_path['target_level']]
    
    return {
        'current_skills': current_skills,
        'target_skills': target_skills,
        'estimated_time': '3个月',
        'recommended_pace': '每日2小时'
    }

# 添加用户管理类
class UserManager:
    def __init__(self):
        self.users_dir = Path("user_data")
        self.users_dir.mkdir(exist_ok=True)
        self.current_user = None
    
    def hash_password(self, password):
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password):
        """用户注册"""
        user_file = self.users_dir / f"{username}.json"
        if user_file.exists():
            return False, "用户名已存在"
        
        user_data = {
            "username": username,
            "password": self.hash_password(password),
            "data": {
                "history": [],
                "progress": {
                    "写作": 0,
                    "口语": 0,
                    "词汇": 0,
                    "语法": 0
                },
                "study_time": {},
                "vocabulary": [],
                "notes": {
                    "写作": [],
                    "口语": [],
                    "词汇": [],
                    "语法": []
                },
                "achievements": {
                    "初学者": False,
                    "勤奋学习者": False,
                    "词汇大师": False,
                    "写作能手": False
                },
                "learning_path": {
                    "current_level": "beginner",
                    "target_level": "advanced",
                    "milestones": [],
                    "completed_steps": []
                }
            }
        }
        
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        return True, "注册成功"
    
    def login(self, username, password):
        """用户登录"""
        user_file = self.users_dir / f"{username}.json"
        if not user_file.exists():
            return False, "用户不存在"
        
        with open(user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        if user_data["password"] != self.hash_password(password):
            return False, "密码错误"
        
        self.current_user = username
        self.load_user_data(username)
        return True, "登录成功"
    
    def load_user_data(self, username):
        """加载用户数据到session_state"""
        user_file = self.users_dir / f"{username}.json"
        with open(user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)["data"]
        
        for key, value in user_data.items():
            st.session_state[key] = value
    
    def save_user_data(self):
        """保存session_state数据到用户文件"""
        if not self.current_user:
            return
        
        user_file = self.users_dir / f"{self.current_user}.json"
        with open(user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        # 更新用户数据
        user_data["data"] = {
            "history": st.session_state.get("history", []),
            "progress": st.session_state.get("progress", {}),
            "study_time": st.session_state.get("study_time", {}),
            "vocabulary": st.session_state.get("vocabulary", []),
            "notes": st.session_state.get("notes", {}),
            "achievements": st.session_state.get("achievements", {}),
            "learning_path": st.session_state.get("learning_path", {})
        }
        
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

def main():
    st.title("🎓 英语学习助手")
    
    # 初始化用户管理器
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    # 如果用户未登录，显示登录/注册界面
    if 'current_user' not in st.session_state:
        st.markdown("### 👤 用户登录")
        
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            login_username = st.text_input("用户名", key="login_username")
            login_password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录"):
                success, message = st.session_state.user_manager.login(login_username, login_password)
                if success:
                    st.session_state.current_user = login_username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            reg_username = st.text_input("用户名", key="reg_username")
            reg_password = st.text_input("密码", type="password", key="reg_password")
            reg_password2 = st.text_input("确认密码", type="password", key="reg_password2")
            if st.button("注册"):
                if reg_password != reg_password2:
                    st.error("两次输入的密码不一致")
                else:
                    success, message = st.session_state.user_manager.register(reg_username, reg_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.stop()  # 如果未登录，停止显示后续内容
    
    # 显示当前用户信息和登出按钮
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"### 👤 当前用户：{st.session_state.current_user}")
    with col2:
        if st.button("登出"):
            # 保存用户数据
            st.session_state.user_manager.save_user_data()
            # 清除session state
            for key in list(st.session_state.keys()):
                if key != "user_manager":
                    del st.session_state[key]
            st.rerun()
    
    # 初始化session_state
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
        
    # 添加learning_path初始化
    if 'learning_path' not in st.session_state:
        st.session_state.learning_path = {
            'current_level': 'beginner',
            'target_level': 'advanced',
            'milestones': [],
            'completed_steps': []
        }
    
    # 侧边栏设置
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.title("⚙️ 设置")
        api_key = st.text_input("DeepSeek API密钥：", type="password", help="请输入您的API密钥")
        if api_key:
            st.session_state.api_key = api_key
            st.success("API密钥已设置！")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.title("🔍 功能选择")
        option = st.selectbox(
            "选择功能",
            ["写作助手", "口语练习指导", "词汇学习", "语法检查", "文献翻译"],
            format_func=lambda x: {
                "写作助手": "✍️ 写作助手",
                "口语练习指导": "🗣️ 口语练习指导",
                "词汇学习": "📚 词汇学习",
                "语法检查": "✔️ 语法检查",
                "文献翻译": "🔄 文献翻译"
            }[x]
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 如果没有API密钥，显示提示信息
    if not st.session_state.api_key:
        st.warning("👋 请在侧边栏输入DeepSeek API密钥以继续使用")
        return
        
    # 添加历史记录和进度标签页
    if st.session_state.api_key:
        tabs = st.tabs(["主要功能", "学习历史", "学习进度", "学习分析", "学习计划", "学习路径"])
        
        with tabs[0]:
            # 原有的主要功能代码
            if option == "写作助手":
                st.markdown('<div class="custom-header">', unsafe_allow_html=True)
                st.header("✍️ 写作助手")
                st.markdown('<p class="feature-description">专业的英语写作指导，帮助你提升写作水平</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    writing_type = st.selectbox(
                        "写作类型",
                        ["学术论文", "邮件写作", "简历制作", "创意写作"]
                    )
                    st.markdown('<p class="hint-text">选择写作类型以获得更专业的建议</p>', unsafe_allow_html=True)
                
                with col1:
                    user_input = st.text_area("请输入你的写作内容或提示：", height=200)
                
                if st.button("获取建议 💡"):
                    if user_input:
                        with st.spinner('正在分析您的写作...'):
                            system_prompt = f"你是一位专业的英语写作教师，专注于{writing_type}。请针对学生的写作内容提供详细的修改建议和改进方案。"
                            st.markdown('<div class="result-container">', unsafe_allow_html=True)
                            response = get_ai_response(user_input, system_prompt)
                            if response:
                                save_to_history('写作', user_input, response)
                                update_progress('写作')
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # 添加写作风格分析
                with st.expander("📊 写作风格分析"):
                    if user_input:
                        system_prompt = f"""
                        请对以下文本进行写作风格分析，包含：
                        1. 词汇多样性评分
                        2. 句式复杂度分析
                        3. 语气风格评估
                        4. 形容词/动词使用频率
                        5. 改进建议
                        """
                        response = get_ai_response(user_input, system_prompt)
                        st.markdown(response)
                
                # 添加写作模板库
                with st.expander("📚 写作模板库"):
                    template_categories = {
                        "学术写作": ["论文摘要", "研究计划", "文献综述"],
                        "商务写作": ["商务邮件", "报告", "提案"],
                        "求职写作": ["求职信", "个人陈述", "简历"],
                        "创意写作": ["故事", "散文", "诗歌"]
                    }
                    
                    template_category = st.selectbox("选择模板类别", list(template_categories.keys()))
                    template_type = st.selectbox("选择具体类型", template_categories[template_category])
                    
                    if st.button("获取模板"):
                        system_prompt = f"""
                        请提供一个专业的{template_category}-{template_type}写作模板，包含：
                        1. 结构框架
                        2. 关键词组
                        3. 常用句式
                        4. 写作技巧
                        5. 示例片段
                        """
                        response = get_ai_response("", system_prompt)
                        st.markdown(response)

                # 添加写作目标设置
                with st.expander("📌 写作目标"):
                    daily_goal = st.number_input("设置每日写作字数目标", min_value=100, value=500, step=100)
                    if st.button("设置目标"):
                        st.session_state.writing_goal = daily_goal
                        st.success(f"已设置每日目标：{daily_goal}字")
                
                # 添加写作提示生成器
                with st.expander("💡 写作提示生成器"):
                    prompt_type = st.selectbox(
                        "选择提示类型",
                        ["话题展开", "论点支持", "过渡段落", "结论总结"]
                    )
                    if st.button("生成提示"):
                        system_prompt = f"请为{prompt_type}生成3个具体的写作提示或建议。"
                        response = get_ai_response("", system_prompt)
                        st.markdown(response)

            elif option == "口语练习指导":
                st.markdown('<div class="custom-header">', unsafe_allow_html=True)
                st.header("🗣️ 口语练习指导")
                st.markdown('<p class="feature-description">个性化口语练习建议和情景对话生成</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    topic = st.text_input("请输入想练习的话题：", placeholder="例如：工作面试、日常购物、旅游会话...")
                    situation = st.selectbox(
                        "选择场景",
                        ["日常对话", "商务会议", "学术讨论", "面试情境", "社交场合"]
                    )
                with col2:
                    level = st.select_slider(
                        "选择难度级别",
                        options=["初级", "中级", "高级"],
                        value="中级"
                    )
                
                if st.button("生成口语练习 🎯"):
                    if topic:
                        with st.spinner('正在生成口语练习内容...'):
                            system_prompt = f"你是一位英语口语教师。请为{level}水平的学生提供关于'{topic}'的口语练习建议和{situation}场景下的示例对话。"
                            st.markdown('<div class="result-container">', unsafe_allow_html=True)
                            response = get_ai_response(topic, system_prompt)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # 添加发音技巧指导
                with st.expander("🎯 发音技巧"):
                    pronunciation_focus = st.multiselect(
                        "选择需要重点练习的发音要素",
                        ["元音", "辅音", "重音", "语调", "连音"],
                        default=["重音", "语调"]
                    )
                    if st.button("获取发音指导"):
                        system_prompt = f"请提供关于{', '.join(pronunciation_focus)}的详细发音技巧和练习方法。"
                        response = get_ai_response("", system_prompt)
                        st.markdown(response)

                # 添加发音评估功能
                with st.expander("🎯 发音评估"):
                    add_speech_recognition()

                # 添加情境对话生成器
                with st.expander("🎭 情境对话"):
                    col1, col2 = st.columns(2)
                    with col1:
                        scenario = st.selectbox(
                            "选择场景",
                            ["商务会议", "日常购物", "餐厅点餐", "旅游问路", "医院就医", "学校生活"]
                        )
                    with col2:
                        role = st.selectbox(
                            "选择角色",
                            ["顾客", "服务员", "学生", "老师", "医生", "病人", "导游", "游客"]
                        )
                    
                    if st.button("生成对话"):
                        system_prompt = f"""
                        请生成一段在{scenario}场景下，以{role}身份进行的英语对话。包含：
                        1. 完整的对话内容（至少5轮对话）
                        2. 重点词汇和短语解释
                        3. 文化差异提示
                        4. 常见错误提醒
                        """
                        response = get_ai_response("", system_prompt)
                        st.markdown(response)
                
                # 添加发音评分系统
                with st.expander("🎯 发音评分"):
                    sample_sentences = [
                        "The quick brown fox jumps over the lazy dog.",
                        "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                        "She sells seashells by the seashore."
                    ]
                    practice_text = st.selectbox("选择练习句子", sample_sentences)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 标准发音")
                        if st.button("播放标准发音"):
                            audio_file = asyncio.run(text_to_speech(practice_text))
                            if audio_file:
                                st.audio(audio_file)
                                os.unlink(audio_file)
                    
                    with col2:
                        st.markdown("### 录制发音")
                        # ... 现有的录音代码 ...

            elif option == "词汇学习":
                st.markdown('<div class="custom-header">', unsafe_allow_html=True)
                st.header("📚 词汇学习")
                st.markdown('<p class="feature-description">深入了解单词含义、用法和例句</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    word = st.text_input("输入想要学习的单词：", placeholder="输入单词或短语...")
                with col2:
                    study_focus = st.multiselect(
                        "学习重点",
                        ["发音", "词义", "例句", "同义词", "词源", "常见搭配"],
                        default=["发音", "词义", "例句"]
                    )
                
                if st.button("开始学习 📖"):
                    if word:
                        with st.spinner('正在查询词汇信息...'):
                            system_prompt = f"请提供单词 '{word}' 的详细信息，重点关注：{', '.join(study_focus)}。"
                            st.markdown('<div class="word-card">', unsafe_allow_html=True)
                            response = get_ai_response(word, system_prompt)
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # 添加生词本功能
                with st.expander("📖 我的生词本"):
                    if 'vocabulary' not in st.session_state:
                        st.session_state.vocabulary = []
                    
                    # 显示已保存的单词
                    if st.session_state.vocabulary:
                        for word_item in st.session_state.vocabulary:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{word_item['word']}** - {word_item['meaning']}")
                            with col2:
                                if st.button("复习", key=f"review_{word_item['word']}"):
                                    system_prompt = f"请生成一个包含单词 '{word_item['word']}' 的例句，并解释用法。"
                                    response = get_ai_response("", system_prompt)
                                    st.markdown(response)
                    else:
                        st.info("生词本还是空的，开始添加新单词吧！")

                # 添加词汇闪卡功能
                with st.expander("📝 词汇闪卡"):
                    if 'flashcards' not in st.session_state:
                        st.session_state.flashcards = []
                    
                    # 添加新词卡
                    col1, col2 = st.columns(2)
                    with col1:
                        new_word = st.text_input("添加新词")
                    with col2:
                        meaning = st.text_input("中文含义")
                    
                    if st.button("添加到闪卡"):
                        if new_word and meaning:
                            st.session_state.flashcards.append({
                                'word': new_word,
                                'meaning': meaning,
                                'mastered': False
                            })
                            st.success("添加成功！")
                    
                    # 显示闪卡
                    if st.session_state.flashcards:
                        for i, card in enumerate(st.session_state.flashcards):
                            with st.container():
                                st.markdown(f"""
                                <div class="flashcard" onclick="this.classList.toggle('flipped')">
                                    <h3>{card['word']}</h3>
                                    <p>{card['meaning']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                # 添加播放发音功能
                if st.button("播放发音 🔊"):
                    play_audio(word)

                # 添加词汇分类系统
                word_categories = {
                    "基础词汇": ["日常用语", "数字时间", "颜色形状"],
                    "商务词汇": ["会议用语", "商务邮件", "谈判术语"],
                    "学术词汇": ["论文写作", "学术报告", "研究方法"],
                    "考试词汇": ["IELTS", "TOEFL", "GRE"]
                }
                
                # 添加词汇测试功能
                with st.expander("📝 词汇测试"):
                    test_category = st.selectbox("选择测试类别", list(word_categories.keys()))
                    test_subcategory = st.selectbox("选择具体方向", word_categories[test_category])
                    
                    if st.button("开始测试"):
                        system_prompt = f"""
                        请生成一个{test_category}-{test_subcategory}方向的词汇测试，包含：
                        1. 5个单词释义选择题
                        2. 3个句子填空题
                        3. 2个情境应用题
                        每个题目都提供详细解析。
                        """
                        response = get_ai_response("", system_prompt)
                        st.markdown(response)
                
                # 添加智能复习提醒
                if 'vocabulary' in st.session_state and st.session_state.vocabulary:
                    with st.expander("📅 复习计划"):
                        today = datetime.now().date()
                        for word in st.session_state.vocabulary:
                            if 'last_review' not in word:
                                word['last_review'] = today
                                word['review_count'] = 0
                            
                            days_passed = (today - word['last_review']).days
                            if days_passed >= get_review_interval(word['review_count']):
                                st.warning(f"该复习 '{word['word']}' 了！")
                                if st.button(f"复习 {word['word']}", key=f"review_{word['word']}"):
                                    word['last_review'] = today
                                    word['review_count'] += 1
                                    st.success("复习完成！")

            elif option == "语法检查":
                st.markdown('<div class="custom-header">', unsafe_allow_html=True)
                st.header("✔️ 语法检查")
                st.markdown('<p class="feature-description">智能语法检查和改进建议</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                text = st.text_area("请输入需要检查的文本：", height=200)
                col1, col2 = st.columns(2)
                with col1:
                    check_focus = st.multiselect(
                        "检查重点",
                        ["语法错误", "用词建议", "句式优化", "标点符号", "时态检查"],
                        default=["语法错误", "用词建议"]
                    )
                with col2:
                    formality = st.select_slider(
                        "文本正式程度",
                        options=["非正式", "中性", "正式"],
                        value="中性"
                    )
                
                if st.button("开始检查 🔍"):
                    if text:
                        with st.spinner('正在分析文本...'):
                            system_prompt = f"请以{formality}的语气检查文本，重点关注：{', '.join(check_focus)}。"
                            st.markdown('<div class="result-container">', unsafe_allow_html=True)
                            response = get_ai_response(text, system_prompt)
                            st.markdown('</div>', unsafe_allow_html=True)
            
            elif option == "文献翻译":
                st.markdown('<div class="custom-header">', unsafe_allow_html=True)
                st.header("🔄 文献翻译")
                st.markdown('<p class="feature-description">专业的学术文献翻译服务</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    text = st.text_area("请输入需要翻译的文本：", height=200)
                with col2:
                    direction = st.radio("翻译方向", ["英译中", "中译英"])
                    field = st.selectbox(
                        "学科领域",
                        ["通用学术", "计算机科学", "医学", "经济", "文学", "工程"]
                    )
                    preserve = st.multiselect(
                        "保留要素",
                        ["专业术语", "参考文献", "图表标注", "作者注释"],
                        default=["专业术语"]
                    )
                
                if st.button("开始翻译 🚀"):
                    if text:
                        with st.spinner('正在翻译...'):
                            system_prompt = f"请将以下{field}领域的文本{'从英文翻译成中文' if direction == '英译中' else '从中文翻译成英文'}，需要特别保留：{', '.join(preserve)}。"
                            st.markdown('<div class="result-container">', unsafe_allow_html=True)
                            response = get_ai_response(text, system_prompt)
                            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[1]:
            st.header("📚 学习历史")
            if 'history' in st.session_state and st.session_state.history:
                for item in reversed(st.session_state.history[-10:]):  # 显示最近10条记录
                    with st.expander(f"{item['timestamp']} - {item['category']}"):
                        st.markdown("**输入内容：**")
                        st.markdown(item['content'])
                        st.markdown("**AI反馈：**")
                        st.markdown(item['result'])
            else:
                st.info("还没有学习记录，开始使用各项功能来积累你的学习历史吧！")

        with tabs[2]:
            st.header("📊 学习进度")
            if 'progress' in st.session_state:
                for category, value in st.session_state.progress.items():
                    st.markdown(f"### {category}学习进度")
                    st.markdown(
                        f"""<div class="progress-bar">
                            <div class="progress-bar-fill" style="width: {value}%"></div>
                        </div>
                        {value}%
                        """,
                        unsafe_allow_html=True
                    )
            
            # 添加学习建议
            with st.expander("📝 学习建议"):
                if 'progress' in st.session_state:
                    lowest_category = min(st.session_state.progress.items(), key=lambda x: x[1])[0]
                    st.markdown(f"建议加强 **{lowest_category}** 方面的练习。")
                    
                    system_prompt = f"请针对用户在{lowest_category}方面的学习给出具体的提升建议和练习方法。"
                    suggestion = get_ai_response("", system_prompt)
                    st.markdown(suggestion)

        with tabs[3]:
            st.header("📊 学习分析")
            
            # 时间范围选择
            col1, col2 = st.columns(2)
            with col1:
                date_range = st.date_input(
                    "选择时间范围",
                    value=(datetime.now(), datetime.now())
                )
            with col2:
                analysis_type = st.selectbox(
                    "分析类型",
                    ["总体概览", "详细分析", "学习建议"]
                )
            
            # 生成并显示报告
            df = generate_study_report()
            if df is not None:
                # 显示基本统计信息
                st.subheader("📈 学习统计")
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_time = df['minutes'].sum()
                    st.metric("总学习时长", f"{total_time}分钟")
                with col2:
                    avg_time = df['minutes'].mean()
                    st.metric("平均每日学习时长", f"{avg_time:.1f}分钟")
                with col3:
                    most_studied = df.groupby('category')['minutes'].sum().idxmax()
                    st.metric("最常学习项目", most_studied)
                
                # 显示详细分析
                if analysis_type == "详细分析":
                    st.subheader("📊 详细分析")
                    
                    # 学习时间分布热力图
                    study_matrix = df.pivot_table(
                        index='date',
                        columns='category',
                        values='minutes',
                        fill_value=0
                    )
                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=study_matrix.values,
                        x=study_matrix.columns,
                        y=study_matrix.index,
                        colorscale='Viridis'
                    ))
                    fig_heatmap.update_layout(title='学习时间分布热力图')
                    st.plotly_chart(fig_heatmap)
                    
                    # 学习进度追踪
                    if 'progress' in st.session_state:
                        progress_df = pd.DataFrame(list(st.session_state.progress.items()),
                                                columns=['category', 'progress'])
                        fig_progress = px.bar(progress_df, x='category', y='progress',
                                            title='学习进度概览')
                        st.plotly_chart(fig_progress)
                
                # 生成学习建议
                elif analysis_type == "学习建议":
                    st.subheader("📝 学习建议")
                    
                    # 分析学习模式
                    weak_areas = df.groupby('category')['minutes'].sum().nsmallest(2)
                    st.write("### 需要加强的领域：")
                    for area, time in weak_areas.items():
                        st.write(f"- {area}: 仅投入 {time} 分钟")
                    
                    # 生成个性化建议
                    system_prompt = f"""
                    基于以下学习数据生成个性化学习建议：
                    - 最需要加强的领域：{weak_areas.index[0]}
                    - 总学习时长：{total_time}分钟
                    - 平均每日学习时长：{avg_time:.1f}分钟
                    请提供具体的改进建议和学习计划。
                    """
                    suggestions = get_ai_response("", system_prompt)
                    st.write("### AI建议：")
                    st.write(suggestions)
            
            # 添加数据导出功能
            st.subheader("💾 数据导出")
            csv_data = export_history_to_csv()
            if csv_data is not None:
                st.download_button(
                    label="下载学习历史记录",
                    data=csv_data,
                    file_name=f'learning_history_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv'
                )

        with tabs[4]:
            st.header("📅 学习计划")
            
            # 生成个性化学习计划
            study_plan = generate_study_plan()
            if study_plan:
                st.subheader("🎯 重点关注领域")
                for area in study_plan['focus_areas']:
                    st.markdown(f"- {area}")
                
                st.subheader("⏰ 每日学习建议")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("建议学习时长", f"{study_plan['daily_time']}分钟")
                with col2:
                    st.metric("优先任务数", f"{len(study_plan['priority_tasks'])}个")
                
                # 添加自定义计划
                with st.expander("🎨 自定义学习计划"):
                    custom_time = st.number_input("设置每日学习时长(分钟)", 
                                               min_value=15, 
                                               value=study_plan['daily_time'],
                                               step=5)
                    priority = st.multiselect("选择优先学习领域",
                                            ["写作", "口语", "词汇", "语法"],
                                            default=study_plan['focus_areas'])
                    
                    if st.button("更新学习计划"):
                        study_plan['daily_time'] = custom_time
                        study_plan['focus_areas'] = priority
                        st.success("学习计划已更新！")
                
                # 添加学习提醒
                with st.expander("⏰ 学习提醒设置"):
                    remind_time = st.time_input("设置每日提醒时间")
                    remind_days = st.multiselect("选择提醒日期",
                                               ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                                               default=["周一", "周三", "周五"])
                    if st.button("设置提醒"):
                        st.success(f"已设置在 {', '.join(remind_days)} 的 {remind_time} 提醒学习")
            
            # 显示需要复习的内容
            st.subheader("📚 待复习内容")
            review_items = check_review_needed()
            if review_items:
                for item in review_items:
                    with st.container():
                        col1, col2, col3 = st.columns([3,1,1])
                        with col1:
                            st.write(f"**{item['content']}**")
                        with col2:
                            st.write(f"上次复习: {item['days_passed']}天前")
                        with col3:
                            if st.button("开始复习", key=f"review_{item['content']}"):
                                # 更新复习时间
                                st.session_state.last_review[item['content']] = datetime.now()
                                st.success("已完成复习！")
            else:
                st.info("目前没有需要复习的内容")

        with tabs[5]:
            st.header("🎯 学习路径规划")
            
            col1, col2 = st.columns(2)
            with col1:
                current_level = st.selectbox(
                    "当前水平",
                    ["beginner", "intermediate", "advanced"],
                    index=["beginner", "intermediate", "advanced"].index(
                        st.session_state.learning_path.get('current_level', 'beginner')
                    )
                )
            with col2:
                target_level = st.selectbox(
                    "目标水平",
                    ["intermediate", "advanced"],
                    index=["intermediate", "advanced"].index(
                        st.session_state.learning_path.get('target_level', 'advanced')
                    )
                )
            
            if st.button("生成学习路径"):
                st.session_state.learning_path['current_level'] = current_level
                st.session_state.learning_path['target_level'] = target_level
                
                path = generate_learning_path()
                
                st.subheader("📋 学习计划")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**当前技能水平：**")
                    for skill in path['current_skills']:
                        st.markdown(f"- {skill}")
                with col2:
                    st.markdown("**目标技能水平：**")
                    for skill in path['target_skills']:
                        st.markdown(f"- {skill}")
                
                st.markdown(f"**预计学习时间：** {path['estimated_time']}")
                st.markdown(f"**建议学习节奏：** {path['recommended_pace']}")

    # 添加成就系统显示
    with st.sidebar:
        with st.expander("🏆 我的成就"):
            check_achievements()
            for achievement, unlocked in st.session_state.achievements.items():
                st.markdown(
                    f"""<div class="achievement-card" style="opacity: {'1' if unlocked else '0.5'}">
                        {'🌟' if unlocked else '🔒'} {achievement}
                    </div>""",
                    unsafe_allow_html=True
                )

    # 添加专注模式
    with st.sidebar:
        with st.expander("⏱️ 专注模式"):
            focus_timer()

    # 在侧边栏添加排行榜
    with st.sidebar:
        with st.expander("🏆 学习排行榜"):
            update_leaderboard()
            if st.session_state.leaderboard:
                # 显示排行榜
                for i, user in enumerate(sorted(
                    st.session_state.leaderboard,
                    key=lambda x: (x['total_time'], x['achievements']),
                    reverse=True
                )[:5]):  # 只显示前5名
                    st.markdown(
                        f"""<div class="achievement-card">
                            {i+1}. {user['user']}
                            <br>学习时长: {user['total_time']}分钟
                            <br>成就数: {user['achievements']}
                        </div>""",
                        unsafe_allow_html=True
                    )

    # 添加笔记系统
    note_system = NoteSystem()
    with st.sidebar:
        with st.expander("📝 学习笔记"):
            note_category = st.selectbox("选择分类", list(st.session_state.notes.keys()))
            note_title = st.text_input("笔记标题")
            note_content = st.text_area("笔记内容")
            if st.button("保存笔记"):
                if note_title and note_content:
                    note_system.add_note(note_category, note_title, note_content)
                    st.success("笔记已保存！")
            
            # 显示笔记
            st.markdown("### 我的笔记")
            note_system.display_notes(note_category)

def get_review_interval(review_count):
    """基于艾宾浩斯遗忘曲线设置复习间隔"""
    intervals = [1, 2, 4, 7, 15, 30, 60]  # 复习间隔（天）
    return intervals[min(review_count, len(intervals)-1)]

if __name__ == "__main__":
    main()
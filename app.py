import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# 1. Cấu hình trang web
st.set_page_config(
    page_title="ShipControl - Quản Lý Công Việc Tàu",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. TÙY CHỈNH CSS: TĂNG KÍCH THƯỚC ĐIỀU HƯỚNG, NÚT BẤM VÀ Ô NHẬP LIỆU
st.markdown("""
    <style>
    /* Nền tổng thể */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 1. THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR) */
    section[data-testid="stSidebar"] {
        background-color: #1a252f !important;
        width: 320px !important; /* Mở rộng chiều rộng thanh sidebar */
    }
    
    /* Tiêu đề điều hướng */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }

    /* Các lựa chọn Menu điều hướng (Radio Buttons) */
    div[data-testid="stRadio"] label {
        font-size: 1.35rem !important; /* Chữ menu to rõ */
        font-weight: 600 !important;
        padding: 10px 5px !important;
        color: #ffffff !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: #2c3e50;
        border-radius: 8px;
    }

    /* 2. CÁC NÚT BẤM (BUTTONS) TO LÊN */
    .stButton > button {
        font-size: 1.2rem !important; /* Chữ trên nút to lên */
        font-weight: bold !important;
        padding: 12px 28px !important; /* Tăng độ dày nút */
        border-radius: 10px !important;
        width: 100% !important; /* Kéo rộng nút bấm */
        box-shadow: 0px 4px 8px rgba(0,0,0,0.15) !important;
    }

    /* 3. TĂNG KÍCH THƯỚC Ô NHẬP LIỆU (INPUTS, SELECTBOX) */
    input, textarea, select, div[data-baseweb="select"] {
        font-size: 1.1rem !important;
    }
    
    label {
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    /* Tiêu đề chính */
    .main-title {
        font-size: 2.5rem;
        color: #0F4C81;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
        border-bottom: 4px solid #0F4C81;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Kết nối cơ sở dữ liệu SQLite
conn = sqlite3.connect("ship_control.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng dữ liệu nếu chưa có
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT UNIQUE,
        task_name TEXT,
        task_cost_code TEXT,
        description TEXT,
        initial_by TEXT,
        initial_date TEXT,
        area TEXT,
        deck TEXT,
        frame TEXT,
        in_charge_by TEXT,
        plan_start_date TEXT,
        plan_finish_date TEXT,
        progress INTEGER,
        remark TEXT,
        image_path TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')
conn.commit()

# --- TIÊU ĐỀ TRANG WEB ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

# Thanh điều hướng bên trái (Đã làm to)
st.sidebar.markdown("## 🧭 MENU CHÍNH")
menu = st.sidebar.radio("", [
    "📋 Bảng Công Việc", 
    "➕ Thêm Công Việc", 
    "✏️ Chỉnh Sửa / Xóa",
    "🗑️ Thùng Rác (Khôi Phục)",
    "📊 Báo Cáo & Thống Kê"
])

# --- 1. DANH SÁCH CÔNG VIỆC ---
if menu == "📋 Bảng Công Việc":
    st.subheader("📋 Bảng Quản Lý Tiến Độ Công Việc")
    
    df = pd.read_sql_query("SELECT task_id, task_name, task_cost_code, description, initial_by, initial_date, area, deck, frame, in_charge_by, plan_start_date, plan_finish_date, progress, remark FROM tasks WHERE is_deleted = 0", conn)
    
    if df.empty:
        st.info("Chưa có dữ liệu công việc nào trong hệ thống.")
    else:
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔍 Chi Tiết Công Việc")
        all_tasks = pd.read_sql_query("SELECT task_id, task_name FROM tasks WHERE is_deleted = 0", conn)
        task_ids = all_tasks['task_id'].tolist()
        selected_task_id = st.selectbox("Chọn Task ID để xem:", task_ids)
        
        if selected_task_id:
            task_detail = pd.read_sql_query("SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0", conn, params=(selected_task_id,)).iloc[0]
            
            st.markdown(f"### **Task:** {task_detail['task_name']}")
            st.write(f"**Mã chi phí (Cost Code):** `{task_detail['task_cost_code']}`")
            st.write(f"**Khu vực (Area):** {task_detail['area']} | **Boong (Deck):** {task_detail['deck']} | **Khung (Frame):** {task_detail['frame']}")
            st.write(f"**Người phụ trách:** {task_detail['in_charge_by']}")
            st.write(f"**Mô tả:** {task_detail['description']}")
            st.write(f"**Ghi chú:** {task_detail['remark']}")
            st.progress(int(task_detail['progress']) / 100, text=f"Hoàn thành: {task_detail['progress']}%")

# --- 2. THÊM CÔNG VIỆC MỚI ---
elif menu == "➕ Thêm Công Việc":
    st.subheader("➕ Thêm Công Việc Mới")
    
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            task_id = st.text_input("Task ID *")
            task_name = st.text_input("Task Name *")
            task_cost_code = st.text_input("Task Cost Code")
            initial_by = st.text_input("Initial By")
            initial_date = st.date_input("Initial Date", datetime.now())

        with col2:
            area = st.text_input("Area")
            deck = st.text_input("Deck")
            frame = st.text_input("Frame")
            in_charge_by = st.text_input("In Charge By")
            progress = st.slider("Progress (%)", 0, 100, 0)

        with col3:
            plan_start_date = st.date_input("Plan Start Date", datetime.now())
            plan_finish_date = st.date_input("Plan Finish Date", datetime.now())
            description = st.text_area("Description")
            remark = st.text_area("Remark")

        submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
        
        if submitted:
            if not task_id or not task_name:
                st.error("Vui lòng điền đầy đủ Task ID và Task Name!")
            else:
                try:
                    cursor.execute('''
                        INSERT INTO tasks (
                            task_id, task_name, task_cost_code, description, initial_by, 
                            initial_date, area, deck, frame, in_charge_by, 
                            plan_start_date, plan_finish_date, progress, remark, image_path, is_deleted
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', 0)
                    ''', (
                        task_id, task_name, task_cost_code, description, initial_by,
                        str(initial_date), area, deck, frame, in_charge_by,
                        str(plan_start_date), str(plan_finish_date), progress, remark
                    ))
                    conn.commit()
                    st.success(f"Đã thêm công việc '{task_name}' thành công!")
                except sqlite3.IntegrityError:
                    st.error("Task ID này đã tồn tại trong hệ thống!")

# --- 3. CHỈNH SỬA / XÓA CÔNG VIỆC ---
elif menu == "✏️ Chỉnh Sửa / Xóa":
    st.subheader("✏️ Quản Lý & Chỉnh Sửa Công Việc")
    
    df_tasks = pd.read_sql_query("SELECT task_id, task_name FROM tasks WHERE is_deleted = 0", conn)
    
    if df_tasks.empty:
        st.info("Chưa có công việc nào để chỉnh sửa.")
    else:
        task_list = df_tasks['task_id'].tolist()
        selected_id = st.selectbox("Chọn Task ID cần thao tác:", task_list)
        
        task = pd.read_sql_query("SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0", conn, params=(selected_id,)).iloc[0]
        
        tab_edit, tab_delete = st.tabs(["✏️ Chỉnh sửa thông tin", "🗑️ Xóa công việc"])
        
        with tab_edit:
            with st.form("edit_task_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.text_input("Task ID (Không thể đổi)", value=task['task_id'], disabled=True)
                    new_task_name = st.text_input("Task Name", value=task['task_name'])
                    new_task_cost_code = st.text_input("Task Cost Code", value=task['task_cost_code'] or "")
                    new_initial_by = st.text_input("Initial By", value=task['initial_by'] or "")
                    
                    try:
                        init_d = datetime.strptime(task['initial_date'], '%Y-%m-%d')
                    except:
                        init_d = datetime.now()
                    new_initial_date = st.date_input("Initial Date", value=init_d)

                with col2:
                    new_area = st.text_input("Area", value=task['area'] or "")
                    new_deck = st.text_input("Deck", value=task['deck'] or "")
                    new_frame = st.text_input("Frame", value=task['frame'] or "")
                    new_in_charge_by = st.text_input("In Charge By", value=task['in_charge_by'] or "")
                    new_progress = st.slider("Progress (%)", 0, 100, int(task['progress'] or 0))

                with col3:
                    try:
                        start_d = datetime.strptime(task['plan_start_date'], '%Y-%m-%d')
                    except:
                        start_d = datetime.now()
                    try:
                        finish_d = datetime.strptime(task['plan_finish_date'], '%Y-%m-%d')
                    except:
                        finish_d = datetime.now()
                        
                    new_plan_start_date = st.date_input("Plan Start Date", value=start_d)
                    new_plan_finish_date = st.date_input("Plan Finish Date", value=finish_d)
                    new_description = st.text_area("Description", value=task['description'] or "")
                    new_remark = st.text_area("Remark", value=task['remark'] or "")

                update_submitted = st.form_submit_button("💾 CẬP NHẬT THÔNG TIN")
                
                if update_submitted:
                    cursor.execute('''
                        UPDATE tasks SET 
                            task_name = ?, task_cost_code = ?, description = ?, initial_by = ?,
                            initial_date = ?, area = ?, deck = ?, frame = ?, in_charge_by = ?,
                            plan_start_date = ?, plan_finish_date = ?, progress = ?, remark = ?
                        WHERE task_id = ?
                    ''', (
                        new_task_name, new_task_cost_code, new_description, new_initial_by,
                        str(new_initial_date), new_area, new_deck, new_frame, new_in_charge_by,
                        str(new_plan_start_date), str(new_plan_finish_date), new_progress, new_remark,
                        selected_id
                    ))
                    conn.commit()
                    st.success(f"Đã cập nhật công việc {selected_id}!")
                    st.rerun()

        with tab_delete:
            st.warning(f"Đưa công việc **{task['task_id']} - {task['task_name']}** vào Thùng rác?")
            if st.button("🗑️ XÁC NHẬN CHUYỂN VÀO THÙNG RÁC", type="primary"):
                cursor.execute("UPDATE tasks SET is_deleted = 1 WHERE task_id = ?", (selected_id,))
                conn.commit()
                st.success("Đã chuyển công việc vào Thùng rác thành công!")
                st.rerun()

# --- 4. THÙNG RÁC ---
elif menu == "🗑️ Thùng Rác (Khôi Phục)":
    st.subheader("🗑️ Khôi Phục Công Việc Đã Xóa")
    
    df_deleted = pd.read_sql_query("SELECT task_id, task_name, area, in_charge_by FROM tasks WHERE is_deleted = 1", conn)
    
    if df_deleted.empty:
        st.success("Thùng rác rỗng.")
    else:
        st.dataframe(df_deleted, use_container_width=True)
        restore_id = st.selectbox("Chọn Task ID cần khôi phục:", df_deleted['task_id'].tolist())
        if st.button("🔄 KHÔI PHỤC CÔNG VIỆC NÀY", type="primary"):
            cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE task_id = ?", (restore_id,))
            conn.commit()
            st.success("Đã khôi phục thành công!")
            st.rerun()

# --- 5. BÁO CÁO & THỐNG KÊ ---
elif menu == "📊 Báo Cáo & Thống Kê":
    st.subheader("📊 Báo Cáo Tiến Độ")
    df = pd.read_sql_query("SELECT * FROM tasks WHERE is_deleted = 0", conn)
    
    if not df.empty:
        total = len(df)
        completed = len(df[df['progress'] == 100])
        in_progress = len(df[(df['progress'] > 0) & (df['progress'] < 100)])
        pending = len(df[df['progress'] == 0])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng Số Công Việc", total)
        c2.metric("Đã Hoàn Thành", completed)
        c3.metric("Đang Thực Hiện", in_progress)
        c4.metric("Chưa Bắt Đầu", pending)
    else:
        st.info("Chưa có dữ liệu thống kê.")
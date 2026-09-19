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

# 2. TÙY CHỈNH CSS GIAO DIỆN LỚN
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    section[data-testid="stSidebar"] {
        background-color: #1a252f !important;
        width: 320px !important;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }

    div[data-testid="stRadio"] label {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        padding: 10px 5px !important;
        color: #ffffff !important;
    }

    .stButton > button {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        padding: 12px 28px !important;
        border-radius: 10px !important;
        width: 100% !important;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.15) !important;
    }

    input, textarea, select, div[data-baseweb="select"] { font-size: 1.1rem !important; }
    label { font-size: 1.1rem !important; font-weight: bold !important; }

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

# Kết nối CSDL SQLite
conn = sqlite3.connect("ship_control.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng lưu trữ dữ liệu nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT UNIQUE,
        task_name TEXT,
        task_cost_code TEXT,
        block TEXT,
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_task_names (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        is_deleted INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_cost_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        is_deleted INTEGER DEFAULT 0
    )
''')
conn.commit()

# --- XỬ LÝ NÂNG CẤP BẢNG CỦ (MIGRATION): TỰ ĐỘNG THÊM CỘT NẾU THIẾU ---
try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN block TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE custom_task_names ADD COLUMN is_deleted INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE custom_cost_codes ADD COLUMN is_deleted INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

# --- TIÊU ĐỀ & MENU ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

st.sidebar.markdown("## 🧭 MENU CHÍNH")
menu = st.sidebar.radio("", [
    "📋 Bảng Công Việc", 
    "⚙️ Quản Lý Danh Mục (Task Name & Cost Code)",
    "➕ Thêm Công Việc", 
    "✏️ Chỉnh Sửa / Xóa",
    "🗑️ Thùng Rác (Khôi Phục)",
    "📊 Báo Cáo & Thống Kê"
])

# --- 1. DANH SÁCH CÔNG VIỆC ---
if menu == "📋 Bảng Công Việc":
    st.subheader("📋 Bảng Quản Lý Tiến Độ Công Việc")
    df = pd.read_sql_query("SELECT task_id, task_name, task_cost_code, block, description, initial_by, initial_date, area, deck, frame, in_charge_by, plan_start_date, plan_finish_date, progress, remark FROM tasks WHERE is_deleted = 0", conn)
    
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
            st.markdown(f"### **Task Name:** {task_detail['task_name']}")
            st.write(f"**Mã chi phí (Cost Code):** `{task_detail['task_cost_code']}` | **Block:** `{task_detail['block']}`")
            st.write(f"**Khu vực (Area):** {task_detail['area']} | **Boong (Deck):** {task_detail['deck']} | **Khung (Frame):** {task_detail['frame']}")
            st.write(f"**Người phụ trách:** {task_detail['in_charge_by']}")
            st.write(f"**Mô tả:** {task_detail['description']}")
            st.write(f"**Ghi chú:** {task_detail['remark']}")
            st.progress(int(task_detail['progress']) / 100, text=f"Hoàn thành: {task_detail['progress']}%")

# --- 2. QUẢN LÝ DANH MỤC (TASK NAME & COST CODE) ---
elif menu == "⚙️ Quản Lý Danh Mục (Task Name & Cost Code)":
    st.subheader("⚙️ Quản Lý Danh Mục Task Name & Cost Code")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🛠️ Danh Mục Tên Công Việc (Task Name)")
        tab_add_task, tab_del_task = st.tabs(["➕ Thêm Task Name mới", "🗑️ Đưa vào Thùng rác"])
        
        with tab_add_task:
            with st.form("add_task_name_form", clear_on_submit=True):
                new_task_name_input = st.text_input("Nhập Task Name mới:")
                submit_task_name = st.form_submit_button("➕ Thêm Task Name")
                if submit_task_name and new_task_name_input.strip():
                    name_clean = new_task_name_input.strip()
                    existing = pd.read_sql_query("SELECT * FROM custom_task_names WHERE name = ?", conn, params=(name_clean,))
                    if not existing.empty:
                        cursor.execute("UPDATE custom_task_names SET is_deleted = 0 WHERE name = ?", (name_clean,))
                        conn.commit()
                        st.success(f"Đã kích hoạt lại Task Name: '{name_clean}'!")
                        st.rerun()
                    else:
                        cursor.execute("INSERT INTO custom_task_names (name, is_deleted) VALUES (?, 0)", (name_clean,))
                        conn.commit()
                        st.success(f"Đã thêm Task Name: '{name_clean}'!")
                        st.rerun()

        with tab_del_task:
            task_names_list = pd.read_sql_query("SELECT name FROM custom_task_names WHERE is_deleted = 0", conn)['name'].tolist()
            if task_names_list:
                selected_del_task = st.selectbox("Chọn Task Name cần xóa tạm:", task_names_list)
                if st.button("🗑️ Đưa vào Thùng rác", type="primary", key="btn_del_task"):
                    cursor.execute("UPDATE custom_task_names SET is_deleted = 1 WHERE name = ?", (selected_del_task,))
                    conn.commit()
                    st.success("Đã chuyển Task Name vào Thùng rác!")
                    st.rerun()
            else:
                st.info("Danh mục Task Name đang trống.")

        st.dataframe(pd.read_sql_query("SELECT id, name AS 'Task Name Hiện Có' FROM custom_task_names WHERE is_deleted = 0", conn), use_container_width=True)

    with col_b:
        st.markdown("### 🏷️ Danh Mục Mã Chi Phí (Cost Code)")
        tab_add_cc, tab_del_cc = st.tabs(["➕ Thêm Cost Code mới", "🗑️ Đưa vào Thùng rác"])
        
        with tab_add_cc:
            with st.form("add_cost_code_form", clear_on_submit=True):
                new_cost_code_input = st.text_input("Nhập Cost Code mới:")
                submit_cost_code = st.form_submit_button("➕ Thêm Cost Code")
                if submit_cost_code and new_cost_code_input.strip():
                    code_clean = new_cost_code_input.strip()
                    existing = pd.read_sql_query("SELECT * FROM custom_cost_codes WHERE code = ?", conn, params=(code_clean,))
                    if not existing.empty:
                        cursor.execute("UPDATE custom_cost_codes SET is_deleted = 0 WHERE code = ?", (code_clean,))
                        conn.commit()
                        st.success(f"Đã kích hoạt lại Cost Code: '{code_clean}'!")
                        st.rerun()
                    else:
                        cursor.execute("INSERT INTO custom_cost_codes (code, is_deleted) VALUES (?, 0)", (code_clean,))
                        conn.commit()
                        st.success(f"Đã thêm Cost Code: '{code_clean}'!")
                        st.rerun()

        with tab_del_cc:
            cost_codes_list = pd.read_sql_query("SELECT code FROM custom_cost_codes WHERE is_deleted = 0", conn)['code'].tolist()
            if cost_codes_list:
                selected_del_cc = st.selectbox("Chọn Cost Code cần xóa tạm:", cost_codes_list)
                if st.button("🗑️ Đưa vào Thùng rác", type="primary", key="btn_del_cc"):
                    cursor.execute("UPDATE custom_cost_codes SET is_deleted = 1 WHERE code = ?", (selected_del_cc,))
                    conn.commit()
                    st.success("Đã chuyển Cost Code vào Thùng rác!")
                    st.rerun()
            else:
                st.info("Danh mục Cost Code đang trống.")

        st.dataframe(pd.read_sql_query("SELECT id, code AS 'Cost Code Hiện Có' FROM custom_cost_codes WHERE is_deleted = 0", conn), use_container_width=True)

# --- 3. THÊM CÔNG VIỆC MỚI (ĐÃ BỔ SUNG THƯ MỤC/TRƯỜNG BLOCK) ---
elif menu == "➕ Thêm Công Việc":
    st.subheader("➕ Thêm Công Việc Mới")
    task_name_list = pd.read_sql_query("SELECT name FROM custom_task_names WHERE is_deleted = 0", conn)['name'].tolist()
    cost_code_list = pd.read_sql_query("SELECT code FROM custom_cost_codes WHERE is_deleted = 0", conn)['code'].tolist()
    
    if not task_name_list or not cost_code_list:
        st.warning("⚠️ Vui lòng vào **'⚙️ Quản Lý Danh Mục'** để tạo ít nhất 1 Task Name và 1 Cost Code trước.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                task_id = st.text_input("Task ID *")
                selected_task_name = st.selectbox("Chọn Task Name *", task_name_list)
                selected_cost_code = st.selectbox("Chọn Cost Code *", cost_code_list)
                block = st.text_input("Block (Ví dụ: 170151)")
            with col2:
                initial_by = st.text_input("Initial By")
                initial_date = st.date_input("Initial Date", datetime.now())
                area = st.text_input("Area")
                deck = st.text_input("Deck")
                frame = st.text_input("Frame")
            with col3:
                in_charge_by = st.text_input("In Charge By")
                progress = st.slider("Progress (%)", 0, 100, 0)
                plan_start_date = st.date_input("Plan Start Date", datetime.now())
                plan_finish_date = st.date_input("Plan Finish Date", datetime.now())
                description = st.text_area("Description")
                remark = st.text_area("Remark")

            submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
            if submitted and task_id:
                try:
                    cursor.execute('''
                        INSERT INTO tasks (
                            task_id, task_name, task_cost_code, block, description, initial_by, 
                            initial_date, area, deck, frame, in_charge_by, 
                            plan_start_date, plan_finish_date, progress, remark, image_path, is_deleted
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', 0)
                    ''', (
                        task_id, selected_task_name, selected_cost_code, block, description, initial_by,
                        str(initial_date), area, deck, frame, in_charge_by,
                        str(plan_start_date), str(plan_finish_date), progress, remark
                    ))
                    conn.commit()
                    st.success("Đã thêm công việc thành công!")
                except Exception as e:
                    st.error(f"Lỗi: Task ID này đã tồn tại hoặc dữ liệu không hợp lệ!")

# --- 4. CHỈNH SỬA / XÓA ---
elif menu == "✏️ Chỉnh Sửa / Xóa":
    st.subheader("✏️ Quản Lý & Chỉnh Sửa Công Việc")
    df_tasks = pd.read_sql_query("SELECT task_id, task_name FROM tasks WHERE is_deleted = 0", conn)
    task_name_list = pd.read_sql_query("SELECT name FROM custom_task_names WHERE is_deleted = 0", conn)['name'].tolist()
    cost_code_list = pd.read_sql_query("SELECT code FROM custom_cost_codes WHERE is_deleted = 0", conn)['code'].tolist()
    
    if df_tasks.empty:
        st.info("Chưa có công việc nào.")
    else:
        selected_id = st.selectbox("Chọn Task ID:", df_tasks['task_id'].tolist())
        task = pd.read_sql_query("SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0", conn, params=(selected_id,)).iloc[0]
        tab_edit, tab_delete = st.tabs(["✏️ Chỉnh sửa", "🗑️ Xóa"])
        
        with tab_edit:
            with st.form("edit_task_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Task ID", value=task['task_id'], disabled=True)
                    new_task_name = st.selectbox("Task Name", task_name_list) if task_name_list else st.text_input("Task Name", value=task['task_name'])
                    new_task_cost_code = st.selectbox("Cost Code", cost_code_list) if cost_code_list else st.text_input("Cost Code", value=task['task_cost_code'])
                    new_block = st.text_input("Block", value=task['block'] or "")
                    new_initial_by = st.text_input("Initial By", value=task['initial_by'] or "")
                    new_initial_date = st.date_input("Initial Date", datetime.now())
                with col2:
                    new_area = st.text_input("Area", value=task['area'] or "")
                    new_deck = st.text_input("Deck", value=task['deck'] or "")
                    new_frame = st.text_input("Frame", value=task['frame'] or "")
                    new_in_charge_by = st.text_input("In Charge By", value=task['in_charge_by'] or "")
                    new_progress = st.slider("Progress (%)", 0, 100, int(task['progress'] or 0))
                with col3:
                    new_plan_start_date = st.date_input("Plan Start", datetime.now())
                    new_plan_finish_date = st.date_input("Plan Finish", datetime.now())
                    new_description = st.text_area("Description", value=task['description'] or "")
                    new_remark = st.text_area("Remark", value=task['remark'] or "")

                if st.form_submit_button("💾 CẬP NHẬT"):
                    cursor.execute('''
                        UPDATE tasks SET 
                            task_name = ?, task_cost_code = ?, block = ?, description = ?, initial_by = ?,
                            initial_date = ?, area = ?, deck = ?, frame = ?, in_charge_by = ?,
                            plan_start_date = ?, plan_finish_date = ?, progress = ?, remark = ?
                        WHERE task_id = ?
                    ''', (
                        new_task_name, new_task_cost_code, new_block, new_description, new_initial_by,
                        str(new_initial_date), new_area, new_deck, new_frame, new_in_charge_by,
                        str(new_plan_start_date), str(new_plan_finish_date), new_progress, new_remark,
                        selected_id
                    ))
                    conn.commit()
                    st.success("Đã cập nhật!")
                    st.rerun()

        with tab_delete:
            if st.button("🗑️ CHUYỂN VÀO THÙNG RÁC", type="primary"):
                cursor.execute("UPDATE tasks SET is_deleted = 1 WHERE task_id = ?", (selected_id,))
                conn.commit()
                st.success("Đã xóa tạm!")
                st.rerun()

# --- 5. THÙNG RÁC (KHÔI PHỤC) ---
elif menu == "🗑️ Thùng Rác (Khôi Phục)":
    st.subheader("🗑️ Khôi Phục Dữ Liệu Đã Xóa")
    
    tab1, tab2, tab3 = st.tabs(["📋 Khôi phục Công Việc", "🛠️ Khôi phục Task Name", "🏷️ Khôi phục Cost Code"])
    
    with tab1:
        df_deleted_tasks = pd.read_sql_query("SELECT task_id, task_name, block, area, in_charge_by FROM tasks WHERE is_deleted = 1", conn)
        if df_deleted_tasks.empty:
            st.info("Không có Công việc nào trong thùng rác.")
        else:
            st.dataframe(df_deleted_tasks, use_container_width=True)
            restore_task_id = st.selectbox("Chọn Task ID cần khôi phục:", df_deleted_tasks['task_id'].tolist())
            if st.button("🔄 Khôi Phục Công Việc Này", type="primary"):
                cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE task_id = ?", (restore_task_id,))
                conn.commit()
                st.success(f"Đã khôi phục thành công Task ID: {restore_task_id}!")
                st.rerun()

    with tab2:
        df_deleted_tn = pd.read_sql_query("SELECT id, name FROM custom_task_names WHERE is_deleted = 1", conn)
        if df_deleted_tn.empty:
            st.info("Không có Task Name nào trong thùng rác.")
        else:
            st.dataframe(df_deleted_tn, use_container_width=True)
            restore_tn = st.selectbox("Chọn Task Name cần khôi phục:", df_deleted_tn['name'].tolist())
            if st.button("🔄 Khôi Phục Task Name Này", type="primary"):
                cursor.execute("UPDATE custom_task_names SET is_deleted = 0 WHERE name = ?", (restore_tn,))
                conn.commit()
                st.success(f"Đã khôi phục thành công Task Name: {restore_tn}!")
                st.rerun()

    with tab3:
        df_deleted_cc = pd.read_sql_query("SELECT id, code FROM custom_cost_codes WHERE is_deleted = 1", conn)
        if df_deleted_cc.empty:
            st.info("Không có Cost Code nào trong thùng rác.")
        else:
            st.dataframe(df_deleted_cc, use_container_width=True)
            restore_cc = st.selectbox("Chọn Cost Code cần khôi phục:", df_deleted_cc['code'].tolist())
            if st.button("🔄 Khôi Phục Cost Code Này", type="primary"):
                cursor.execute("UPDATE custom_cost_codes SET is_deleted = 0 WHERE code = ?", (restore_cc,))
                conn.commit()
                st.success(f"Đã khôi phục thành công Cost Code: {restore_cc}!")
                st.rerun()

# --- 6. BÁO CÁO & THỐNG KÊ ---
elif menu == "📊 Báo Cáo & Thống Kê":
    st.subheader("📊 Báo Cáo Tiến Độ")
    df = pd.read_sql_query("SELECT * FROM tasks WHERE is_deleted = 0", conn)
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng Công Việc", len(df))
        c2.metric("Đã Hoàn Thành", len(df[df['progress'] == 100]))
        c3.metric("Đang Thực Hiện", len(df[(df['progress'] > 0) & (df['progress'] < 100)]))
        c4.metric("Chưa Bắt Đầu", len(df[df['progress'] == 0]))
    else:
        st.info("Chưa có dữ liệu thống kê.")
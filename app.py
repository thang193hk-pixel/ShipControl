import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import hmac
import html
import secrets
from datetime import datetime, date, timedelta
import altair as alt
import extra_streamlit_components as stx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


MODERN_CSS_TEMPLATE = r'''
/* ================================================================
   🎨 GIAO DIỆN HIỆN ĐẠI (lớp phủ cuối cùng, ghi đè các kiểu cũ)
   ================================================================ */

html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li, .stApp span:not([data-testid="stIconMaterial"]) {
    font-family: 'Twemoji Country Flags', 'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

/* ---------- 🏳️ Cờ các nước: Windows không tự hiện emoji cờ (chỉ hiện chữ "VN"),
   nên tải một phông chữ nhỏ CHỈ chứa hình cờ (các ký tự khác vẫn dùng phông bình thường) ---------- */
@font-face {
    font-family: 'Twemoji Country Flags';
    unicode-range: U+1F1E6-1F1FF, U+1F3F4, U+E0062-E0063, U+E0065, U+E0067, U+E006C, U+E006E, U+E0073-E0074, U+E0077, U+E007F;
    src: url('https://cdn.jsdelivr.net/npm/country-flag-emoji-polyfill@0.1/dist/TwemojiCountryFlags.woff2') format('woff2');
    font-display: swap;
}
[data-baseweb="popover"] li, [data-baseweb="popover"] li *, [role="listbox"] [role="option"], [role="listbox"] [role="option"] * {
    font-family: 'Twemoji Country Flags', 'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;
}

/* ---------- Nền: ảnh tàu, mỗi trang một ảnh ----------
   Ảnh nằm trên một lớp cố định riêng (nhẹ hơn nhiều so với background-attachment: fixed),
   mờ dần vào khi đổi trang, và tất cả ảnh được tải trước nên đổi trang không bị nháy. */
.stApp {
    background: __BASE_BG__ !important;
}
.stApp::after {
    content: __PRELOAD__;
    position: absolute;
    width: 0;
    height: 0;
    overflow: hidden;
    opacity: 0;
    z-index: -1;
    pointer-events: none;
}
div[data-testid="stAppViewContainer"] {
    /* Giữ nguyên kiểu định vị gốc của Streamlit (để thanh bên và trang cuộn được), chỉ đưa lên trên lớp ảnh nền */
    z-index: 1;
    background: transparent !important;
}
.main, .stMain, section[data-testid="stMain"], div[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ---------- Thanh bên ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0369a1 0%, #075985 55%, #0c4a6e 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 4px 0 24px rgba(12, 74, 110, 0.18) !important;
}
.sidebar-header {
    font-size: 1.7rem !important;
    letter-spacing: -0.02em !important;
}
.user-card {
    background: rgba(255, 255, 255, 0.10) !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 16px !important;
}
.made-by-minh {
    font-size: 1.25rem !important;
    border-radius: 999px !important;
    box-shadow: 0 6px 20px rgba(250, 204, 21, 0.35) !important;
    letter-spacing: -0.01em !important;
}

/* Menu: mục thường phẳng, mục đang chọn là viên thuốc màu vàng phát sáng nhẹ */
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    transform: translateX(3px) !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #fde047 0%, #facc15 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 18px rgba(250, 204, 21, 0.40) !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover:not(:disabled) {
    box-shadow: 0 8px 22px rgba(250, 204, 21, 0.50) !important;
}
section[data-testid="stSidebar"] div.st-key-btn_logout_bottom div.stButton > button[kind] {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div.st-key-btn_logout_bottom div.stButton > button[kind]:hover:not(:disabled) {
    background: rgba(239, 68, 68, 0.85) !important;
    border-color: transparent !important;
    transform: none !important;
}

/* ---------- Nút trong trang: phẳng, bo tròn, bóng mềm ---------- */
div.stButton > button,
div.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 12px !important;
    min-height: 48px !important;
    transition: transform 0.15s ease, box-shadow 0.2s ease, background 0.2s ease, border-color 0.2s ease !important;
}
div.stButton > button *,
div.stDownloadButton > button *,
div[data-testid="stFormSubmitButton"] > button * {
    font-size: 1.02rem !important;
    font-weight: 700 !important;
    letter-spacing: 0 !important;
}
.stMain div.stButton > button[kind="primary"],
.main div.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button,
div.stDownloadButton > button {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(22, 163, 74, 0.30) !important;
}
.stMain div.stButton > button[kind="primary"]:hover:not(:disabled),
.main div.stButton > button[kind="primary"]:hover:not(:disabled),
div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled),
div.stDownloadButton > button:hover:not(:disabled) {
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
    box-shadow: 0 8px 22px rgba(22, 163, 74, 0.38) !important;
    transform: translateY(-2px) !important;
}
.stMain div.stButton > button[kind="secondary"],
.main div.stButton > button[kind="secondary"] {
    background: __SURFACE__ !important;
    border: 1px solid __SURFACE_BORDER__ !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08) !important;
}
.stMain div.stButton > button[kind="secondary"]:hover:not(:disabled),
.main div.stButton > button[kind="secondary"]:hover:not(:disabled) {
    border-color: #0ea5e9 !important;
    box-shadow: 0 6px 16px rgba(14, 165, 233, 0.18) !important;
    transform: translateY(-2px) !important;
}
div.stButton > button:active:not(:disabled),
div.stDownloadButton > button:active:not(:disabled),
div[data-testid="stFormSubmitButton"] > button:active:not(:disabled) {
    transform: scale(0.97) !important;
}
/* Nút xóa: nền đỏ nhạt, chữ đỏ; rê chuột thì đỏ đậm */
__DANGER_SEL__ {
    background: __DANGER_SOFT__ !important;
    border: 1px solid rgba(220, 38, 38, 0.35) !important;
    box-shadow: none !important;
}
__DANGER_SEL_HOVER__ {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    border-color: transparent !important;
    box-shadow: 0 8px 20px rgba(220, 38, 38, 0.30) !important;
}

/* ---------- Tiêu đề ---------- */
.main-title {
    font-size: 2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    border-bottom: none !important;
    padding-bottom: 14px !important;
    position: relative;
}
.main-title::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: 0;
    width: 120px;
    height: 4px;
    transform: translateX(-50%);
    border-radius: 999px;
    background: linear-gradient(90deg, #0ea5e9, #22c55e, #facc15);
}
.big-table-title {
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}
.stApp h3 {
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}

/* ---------- Thẻ (form, khung mở rộng, bảng) ---------- */
div[data-testid="stForm"] {
    background: __SURFACE__ !important;
    border: 1px solid __SURFACE_BORDER__ !important;
    border-radius: 18px !important;
    padding: 22px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06) !important;
}
div[data-testid="stExpander"] details {
    background: __SURFACE__ !important;
    border: 1px solid __SURFACE_BORDER__ !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05) !important;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    background: transparent !important;
    padding: 14px 18px !important;
}
div[data-testid="stExpander"] summary:hover {
    background: __HOVER_TINT__ !important;
}
div[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid __SURFACE_BORDER__ !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05) !important;
}
div[data-testid="stDataFrame"] th,
div[data-testid="stTable"] th {
    font-size: 1rem !important;
    font-weight: 700 !important;
}
div[data-testid="stDataFrame"] td,
div[data-testid="stTable"] td,
div[data-testid="stDataFrame"] [role="gridcell"] {
    font-size: 1rem !important;
    font-weight: 500 !important;
}
hr {
    border-color: __SURFACE_BORDER__ !important;
    opacity: 0.8;
}

/* ---------- Ô nhập liệu ----------
   Khung ngoài (data-baseweb="input") là "hộp" hiển thị: nền, viền, bo góc.
   Bên trong (ô gõ chữ, nút con mắt) để trong suốt → không bị viền đôi, nút con mắt nằm gọn trong hộp. */
:root {
    color-scheme: __SCHEME__;
}
div[data-testid="stTextInputRootElement"],
div[data-testid="stTextAreaRootElement"],
div[data-testid="stNumberInputContainer"],
div[data-testid="stDateInputField"],
div[data-testid="stSelectbox"] div:has(> input),
div[data-testid="stMultiSelect"] div:has(> input),
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background-color: __INPUT_BG__ !important;
    border: 1.5px solid __INPUT_BORDER__ !important;
    border-radius: 12px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-testid="stTextInputRootElement"]:hover,
div[data-testid="stTextAreaRootElement"]:hover,
div[data-testid="stNumberInputContainer"]:hover,
div[data-testid="stDateInputField"]:hover,
div[data-testid="stSelectbox"] div:has(> input):hover,
div[data-testid="stMultiSelect"] div:has(> input):hover,
div[data-baseweb="input"]:hover,
div[data-baseweb="textarea"]:hover {
    border-color: __INPUT_BORDER_HOVER__ !important;
}
div[data-testid="stTextInputRootElement"]:focus-within,
div[data-testid="stTextAreaRootElement"]:focus-within,
div[data-testid="stNumberInputContainer"]:focus-within,
div[data-testid="stDateInputField"]:focus-within,
div[data-testid="stSelectbox"] div:has(> input):focus-within,
div[data-testid="stMultiSelect"] div:has(> input):focus-within,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.18) !important;
}
div[data-testid="stTextInputRootElement"] *,
div[data-testid="stTextAreaRootElement"] *,
div[data-testid="stNumberInputContainer"] *,
div[data-testid="stDateInputField"] *,
div[data-testid="stSelectbox"] div:has(> input) *,
div[data-testid="stMultiSelect"] div:has(> input) *,
div[data-baseweb="input"] *,
div[data-baseweb="textarea"] * {
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
}
/* Ô nhập nằm trong ô khác (ví dụ ô số): không vẽ hộp lồng nhau */
div[data-testid="stTextInputRootElement"] div[data-baseweb="input"],
div[data-testid="stTextAreaRootElement"] div[data-baseweb="input"],
div[data-testid="stNumberInputContainer"] div[data-baseweb="input"],
div[data-testid="stDateInputField"] div[data-baseweb="input"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.stApp input, .stApp textarea {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
    caret-color: #0ea5e9 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
}
.stApp input::placeholder, .stApp textarea::placeholder {
    color: __PLACEHOLDER__ !important;
    -webkit-text-fill-color: __PLACEHOLDER__ !important;
    opacity: 1 !important;
}
div[data-testid="stSelectbox"] div:has(> input) *,
div[data-baseweb="select"] * {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
}
/* Trình duyệt tự điền (autofill): giữ đúng màu nền và màu chữ của app */
.stApp input:-webkit-autofill,
.stApp input:-webkit-autofill:hover,
.stApp input:-webkit-autofill:focus {
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
    -webkit-box-shadow: 0 0 0 1000px __INPUT_BG__ inset !important;
    box-shadow: 0 0 0 1000px __INPUT_BG__ inset !important;
    transition: background-color 99999s ease-out 0s;
}

/* Biểu tượng trong ô nhập: con mắt (hiện mật khẩu), mũi tên chọn, nút +/- */
div[data-testid="stTextInputRootElement"] button,
div[data-baseweb="input"] button,
div[data-testid="stNumberInputContainer"] button {
    background: transparent !important;
    border: none !important;
    color: __ICON__ !important;
    opacity: 1 !important;
    padding: 0 12px !important;
    min-height: 0 !important;
}
div[data-testid="stTextInputRootElement"] button svg,
div[data-baseweb="input"] button svg,
div[data-testid="stNumberInputContainer"] button svg,
div[data-testid="stSelectbox"] svg,
div[data-testid="stMultiSelect"] svg,
div[data-baseweb="select"] svg {
    color: __ICON__ !important;
    fill: __ICON__ !important;
    width: 22px !important;
    height: 22px !important;
    opacity: 1 !important;
}
div[data-testid="stTextInputRootElement"] button:hover svg,
div[data-baseweb="input"] button:hover svg,
div[data-testid="stNumberInputContainer"] button:hover svg {
    color: #0ea5e9 !important;
    fill: #0ea5e9 !important;
}

div[data-testid="stTextInputRootElement"] button span,
div[data-testid="stTextInputRootElement"] button i {
    font-size: 22px !important;
    color: __ICON__ !important;
    opacity: 1 !important;
}
div[data-testid="stDateInputField"] *,
div[data-testid="stDateInputField"] input {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
    opacity: 1 !important;
}

/* ---------- 🪪 Thẻ tài khoản dưới menu ---------- */
.profile-card {
    margin: 14px 0 12px 0;
    padding: 14px 14px 10px 14px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #ffffff;
}
.profile-card * { color: #ffffff; }
.pc-top {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 10px;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
.pc-avatar {
    flex: 0 0 44px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #fde047, #facc15);
    color: #0c4a6e !important;
    font-weight: 800;
    font-size: 1.05rem;
    box-shadow: 0 4px 12px rgba(250, 204, 21, 0.35);
}
.pc-id { min-width: 0; }
.pc-name {
    font-weight: 800;
    font-size: 1.05rem;
    line-height: 1.25;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.pc-status { font-size: 0.8rem; color: #86efac !important; }
.pc-status span { color: rgba(255, 255, 255, 0.75) !important; }
.pc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 5px 0;
    font-size: 0.9rem;
}
.pc-label { color: rgba(255, 255, 255, 0.70) !important; white-space: nowrap; }
.pc-val {
    font-weight: 700;
    text-align: right;
    overflow-wrap: anywhere;
}
.pc-role {
    font-weight: 800;
    font-size: 0.85rem;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(250, 204, 21, 0.18);
    border: 1px solid rgba(250, 204, 21, 0.55);
    color: #fde047 !important;
    white-space: nowrap;
}
/* Menu gọn hơn một chút để thẻ tài khoản hiện ra mà không phải cuộn */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

/* ---------- Công tắc bật/tắt (toggle): rõ ràng ở cả trạng thái Tắt và Bật ---------- */
label:has(> span > input[role="switch"]) > div:not([data-testid]) {
    background: __TOGGLE_OFF__ !important;
    border: 2px solid __TOGGLE_OFF_BORDER__ !important;
    box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.25) !important;
    opacity: 1 !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
}
label:has(> span > input[role="switch"]) > div:not([data-testid]) > div {
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.45) !important;
    opacity: 1 !important;
}
label:has(> span > input[role="switch"]:checked) > div:not([data-testid]) {
    background: #0ea5e9 !important;
    border-color: #0284c7 !important;
}
label:has(> span > input[role="switch"]:focus-visible) > div:not([data-testid]) {
    outline: 3px solid rgba(14, 165, 233, 0.45) !important;
    outline-offset: 2px !important;
}
label:has(> span > input[role="switch"]:disabled) {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* ---------- 🌐 Chọn chủ đề + ngôn ngữ trong Cài đặt: nút xanh, chữ trắng, mũi tên trắng ---------- */
html body .st-key-w_ui_theme,
html body .st-key-w_ui_lang {
    width: auto !important;
}
html body .st-key-w_ui_theme div[data-testid="stSelectbox"] div:has(> input),
html body .st-key-w_ui_lang div[data-testid="stSelectbox"] div:has(> input),
html body .st-key-w_ui_theme div[data-baseweb="select"] > div,
html body .st-key-w_ui_lang div[data-baseweb="select"] > div {
    background: #4f8ef7 !important;
    background-color: #4f8ef7 !important;
    border: none !important;
    border-radius: 8px !important;
    min-height: 38px !important;
    width: fit-content !important;
    min-width: 170px !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
    cursor: pointer !important;
}
html body .st-key-w_ui_theme div[data-testid="stSelectbox"] div:has(> input):hover,
html body .st-key-w_ui_lang div[data-testid="stSelectbox"] div:has(> input):hover {
    background: #3b7cf0 !important;
    background-color: #3b7cf0 !important;
}
html body .st-key-w_ui_theme div[data-testid="stSelectbox"] div:has(> input) *,
html body .st-key-w_ui_lang div[data-testid="stSelectbox"] div:has(> input) *,
html body .st-key-w_ui_theme div[data-baseweb="select"] *,
html body .st-key-w_ui_lang div[data-baseweb="select"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
    caret-color: transparent !important;
}
html body .st-key-w_ui_theme div[data-testid="stSelectbox"] svg,
html body .st-key-w_ui_lang div[data-testid="stSelectbox"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* ---------- 🌐 Nút ngôn ngữ: ô vuông xanh, quả địa cầu trắng + mũi tên ---------- */
section[data-testid="stSidebar"] .st-key-pop_lang [data-testid="stPopover"] button,
section[data-testid="stSidebar"] .st-key-pop_lang button {
    background: #4f8ef7 !important;
    border: none !important;
    border-radius: 8px !important;
    min-height: 34px !important;
    height: 34px !important;
    min-width: 0 !important;
    width: auto !important;
    padding: 0 8px 0 10px !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35) !important;
    gap: 2px !important;
}
section[data-testid="stSidebar"] .st-key-pop_lang [data-testid="stPopover"] button:hover,
section[data-testid="stSidebar"] .st-key-pop_lang button:hover {
    background: #3b7cf0 !important;
}
section[data-testid="stSidebar"] .st-key-pop_lang button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}
section[data-testid="stSidebar"] .st-key-pop_lang [data-testid="stIconMaterial"] {
    font-size: 22px !important;
}
section[data-testid="stSidebar"] .st-key-pop_lang button::after {
    display: none !important;
}

/* ---------- 📲 Chọn thiết bị: 2 ô lớn thay cho nút tròn nhỏ ---------- */
.st-key-device_mode_login,
.st-key-w_device_mode {
    width: 100% !important;
}
.st-key-device_mode_login [data-testid="stRadioGroup"],
.st-key-w_device_mode [data-testid="stRadioGroup"] {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 12px !important;
    width: 100% !important;
}
.st-key-device_mode_login [data-testid="stRadioGroup"] > div,
.st-key-w_device_mode [data-testid="stRadioGroup"] > div {
    width: 100% !important;
    margin: 0 !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"],
.st-key-w_device_mode label[data-testid="stRadioOption"] {
    position: relative;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 64px !important;
    padding: 12px 10px !important;
    margin: 0 !important;
    border-radius: 16px !important;
    border: 2px solid __INPUT_BORDER__ !important;
    background: __SURFACE__ !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06) !important;
    cursor: pointer !important;
    transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"]:hover,
.st-key-w_device_mode label[data-testid="stRadioOption"]:hover {
    border-color: #0ea5e9 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(14, 165, 233, 0.18) !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"][data-selected="true"],
.st-key-w_device_mode label[data-testid="stRadioOption"][data-selected="true"] {
    border-color: #0ea5e9 !important;
    background: __SELECTED_BG__ !important;
    box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.18), 0 6px 16px rgba(14, 165, 233, 0.20) !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"][data-selected="true"]::after,
.st-key-w_device_mode label[data-testid="stRadioOption"][data-selected="true"]::after {
    content: "✓";
    position: absolute;
    top: -9px;
    right: -9px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #0ea5e9;
    color: #ffffff;
    font-size: 14px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(2, 132, 199, 0.4);
}
/* Ẩn nút tròn nhỏ, chỉ giữ chữ */
.st-key-device_mode_login label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]),
.st-key-w_device_mode label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) {
    display: none !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"] p,
.st-key-w_device_mode label[data-testid="stRadioOption"] p {
    font-size: 1.2rem !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
    margin: 0 !important;
}
.st-key-device_mode_login label[data-testid="stRadioOption"]:has(input:focus-visible),
.st-key-w_device_mode label[data-testid="stRadioOption"]:has(input:focus-visible) {
    outline: 3px solid rgba(14, 165, 233, 0.5) !important;
    outline-offset: 2px !important;
}
/* Trong bảng Cài đặt: nhỏ gọn hơn một chút */
.st-key-w_device_mode label[data-testid="stRadioOption"] {
    min-height: 50px !important;
    border-radius: 12px !important;
}
.st-key-w_device_mode label[data-testid="stRadioOption"] p {
    font-size: 1.02rem !important;
}

/* ---------- ⚙️ Nút Cài đặt trên thanh bên ---------- */
section[data-testid="stSidebar"] [data-testid="stPopover"] button {
    background: rgba(255, 255, 255, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 999px !important;
    min-height: 34px !important;
    height: 34px !important;
    padding: 0 14px !important;
    width: auto !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}
section[data-testid="stSidebar"] [data-testid="stPopover"] button:hover {
    background: rgba(255, 255, 255, 0.24) !important;
}
section[data-testid="stSidebar"] [data-testid="stPopover"] button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
/* Bảng cài đặt bật ra */
div[data-testid="stPopoverBody"] {
    background: __SURFACE__ !important;
    border: 1px solid __SURFACE_BORDER__ !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.25) !important;
    padding: 18px !important;
    min-width: 260px !important;
}
div[data-testid="stPopoverBody"] * {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
}
div[data-testid="stPopoverBody"] [data-testid="stWidgetLabel"] p {
    font-weight: 700 !important;
    font-size: 1rem !important;
}

/* ---------- Nút mở / đóng thanh bên (») và («) ---------- */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] button {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    border-radius: 12px !important;
    width: 44px !important;
    height: 44px !important;
    box-shadow: 0 6px 16px rgba(3, 105, 161, 0.35) !important;
    opacity: 1 !important;
}
[data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapsedControl"] button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    font-size: 26px !important;
    opacity: 1 !important;
}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background: rgba(255, 255, 255, 0.14) !important;
    border-radius: 10px !important;
    width: 40px !important;
    height: 40px !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    font-size: 24px !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: rgba(255, 255, 255, 0.28) !important;
}
/* Nút ⋮ và Deploy ở góc trên */
header[data-testid="stHeader"] button {
    color: __INPUT_TEXT__ !important;
}
/* Vệt sáng chỉ chạy trên mục menu đang chọn; mục thường nền trong suốt nên vệt sáng trông như vết lỗi */
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]::after,
section[data-testid="stSidebar"] [data-testid="stPopover"] button::after {
    display: none !important;
}

/* ---------- Thông báo: mỗi loại một màu, chữ vừa phải ---------- */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid transparent !important;
}
div[data-testid="stAlert"] * {
    font-size: 1rem !important;
    font-weight: 600 !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {
    background: __INFO_BG__ !important; border-color: rgba(14, 165, 233, 0.35) !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) * {
    color: __INFO_TX__ !important; -webkit-text-fill-color: __INFO_TX__ !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {
    background: __OK_BG__ !important; border-color: rgba(34, 197, 94, 0.35) !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) * {
    color: __OK_TX__ !important; -webkit-text-fill-color: __OK_TX__ !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {
    background: __WARN_BG__ !important; border-color: rgba(234, 179, 8, 0.45) !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) * {
    color: __WARN_TX__ !important; -webkit-text-fill-color: __WARN_TX__ !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {
    background: __ERR_BG__ !important; border-color: rgba(239, 68, 68, 0.40) !important;
}
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) * {
    color: __ERR_TX__ !important; -webkit-text-fill-color: __ERR_TX__ !important;
}

/* ---------- 💬 Khung tin nhắn ---------- */
.sc-chat {
    height: 420px;
    overflow-y: auto;
    display: flex;
    flex-direction: column-reverse;      /* tin mới nhất ở dưới, tự cuộn xuống cuối */
    gap: 10px;
    padding: 14px;
    border-radius: 16px;
    background: __SURFACE__;
    border: 1px solid __SURFACE_BORDER__;
    box-shadow: inset 0 1px 4px rgba(15, 23, 42, 0.05);
    margin-bottom: 10px;
}
.sc-chat-empty { margin: auto; color: __PLACEHOLDER__; font-weight: 600; text-align: center; }
.sc-msg { display: flex; flex-direction: column; max-width: 78%; }
.sc-mine { align-self: flex-end; align-items: flex-end; }
.sc-theirs { align-self: flex-start; align-items: flex-start; }
.sc-meta { font-size: 0.75rem; color: __PLACEHOLDER__; margin: 0 6px 3px 6px; }
.sc-bubble {
    padding: 9px 14px;
    border-radius: 18px;
    font-size: 1rem;
    line-height: 1.4;
    overflow-wrap: anywhere;
    animation: scFadeUp 0.2s ease-out both;
}
.sc-mine .sc-bubble {
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    color: #ffffff;
    border-bottom-right-radius: 6px;
}
.sc-theirs .sc-bubble {
    background: __BUBBLE_THEIRS__;
    color: __INPUT_TEXT__;
    border-bottom-left-radius: 6px;
}
[data-testid="stChatInput"] {
    border-radius: 16px !important;
}
/* Danh sách người trong Tin nhắn: chữ căn trái, gọn hơn */
div[class*="st-key-chat_open_"] div.stButton > button {
    justify-content: flex-start !important;
    min-height: 44px !important;
    margin-bottom: 2px !important;
}
div[class*="st-key-chat_open_"] div.stButton > button > div,
div[class*="st-key-chat_open_"] div.stButton > button p {
    justify-content: flex-start !important;
    text-align: left !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* ---------- Nút mở liên kết (Bắt đầu / Mở phòng họp): giống nút chính màu xanh ---------- */
div[data-testid="stLinkButton"] a {
    min-height: 48px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: transform 0.15s ease, box-shadow 0.2s ease !important;
}
div[data-testid="stLinkButton"] a[kind="primary"],
div[data-testid="stLinkButton"] a[data-testid="stBaseLinkButton-primary"] {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(22, 163, 74, 0.30) !important;
}
div[data-testid="stLinkButton"] a[kind="primary"] *,
div[data-testid="stLinkButton"] a[data-testid="stBaseLinkButton-primary"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
}
div[data-testid="stLinkButton"] a:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(22, 163, 74, 0.38) !important;
}
div[data-testid="stTimeInput"] div:has(> input),
div[data-testid="stTimeInput"] div[data-baseweb="select"] > div {
    background-color: __INPUT_BG__ !important;
    border: 1.5px solid __INPUT_BORDER__ !important;
    border-radius: 12px !important;
}
div[data-testid="stTimeInput"] input, div[data-testid="stTimeInput"] div[data-baseweb="select"] * {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
}

/* ---------- Ô chọn nhiều người: tên đã chọn hiện chữ đen trên nền xanh nhạt ---------- */
/* Hộp ngoài là khung nhập; vùng chứa tên bên trong trong suốt (không bị khung lồng khung) */
html body div[data-testid="stMultiSelect"] div:has(> div[data-testid="stMultiSelectTagsContainer"]) {
    background-color: __INPUT_BG__ !important;
    border: 1.5px solid __INPUT_BORDER__ !important;
    border-radius: 12px !important;
}
html body div[data-testid="stMultiSelect"] div:has(> div[data-testid="stMultiSelectTagsContainer"]):focus-within {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.18) !important;
}
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* Từng tên đã chọn */
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] > span > span,
html body div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background-color: __SELECTED_BG__ !important;
    border: 1px solid #0ea5e9 !important;
    border-radius: 14px !important;
    padding: 4px 4px 4px 10px !important;
}
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] > span > span *,
html body div[data-testid="stMultiSelect"] [data-baseweb="tag"] * {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
    background-color: transparent !important;
    font-weight: 600 !important;
}
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] > span > span svg,
html body div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
    fill: __INPUT_TEXT__ !important;
    color: __INPUT_TEXT__ !important;
    width: 14px !important;
    height: 14px !important;
}
/* Hiện đủ tên (xuống dòng nếu dài), không cắt thành "Minh ..." */
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] > span > span {
    max-width: 100% !important;
    height: auto !important;
}
html body div[data-testid="stMultiSelect"] div[data-testid="stMultiSelectTagsContainer"] > span > span > span {
    max-width: none !important;
    overflow: visible !important;
    text-overflow: clip !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}
/* Danh sách xổ xuống: chữ đen */
[data-baseweb="popover"] li, [data-baseweb="popover"] li * {
    color: __INPUT_TEXT__ !important;
    -webkit-text-fill-color: __INPUT_TEXT__ !important;
}

/* ---------- 🎥 Thẻ ID + mật khẩu phòng họp ---------- */
.sc-meet-card {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin: 6px 0 4px 0;
}
.sc-meet-card > div {
    flex: 1 1 160px;
    padding: 12px 16px;
    border-radius: 14px;
    background: __SELECTED_BG__;
    border: 2px dashed #0ea5e9;
}
.sc-meet-card span { display: block; font-size: 0.85rem; color: __PLACEHOLDER__; font-weight: 600; }
.sc-meet-card b { display: block; font-size: 1.7rem; letter-spacing: 0.08em; color: __INPUT_TEXT__; font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace !important; }
.sc-meet-card.sc-compact > div { padding: 8px 12px; }
.sc-meet-card.sc-compact b { font-size: 1.25rem; }

/* ================================================================
   🌊 MƯỢT MÀ HƠN
   ================================================================ */
html { scroll-behavior: smooth; }
body, .stApp {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}
/* Khi app đang xử lý, Streamlit làm mờ nội dung cũ (nhấp nháy) → giữ nguyên độ rõ */
[data-stale="true"], .stale-element {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}
/* Bỏ thanh màu nhấp nháy ở mép trên */
[data-testid="stDecoration"] { display: none !important; }
/* Thông báo, khung mở rộng, bảng cài đặt và danh sách chọn hiện ra nhẹ nhàng */
div[data-testid="stAlert"] { animation: scFadeUp 0.28s ease-out both; }
[data-testid="stExpanderDetails"] { animation: scFadeUp 0.25s ease-out both; }
div[data-testid="stPopoverBody"] { animation: scPop 0.18s cubic-bezier(0.2, 0.8, 0.2, 1) both; transform-origin: top left; }
[data-baseweb="popover"] ul[role="listbox"] { animation: scPop 0.15s ease-out both; transform-origin: top center; }
@keyframes scFadeUp {
    from { opacity: 0; transform: translate3d(0, 6px, 0); }
    to   { opacity: 1; transform: none; }
}
@keyframes scPop {
    from { opacity: 0; transform: scale(0.96) translate3d(0, -4px, 0); }
    to   { opacity: 1; transform: none; }
}
/* Đổi chủ đề / Sáng-Tối: màu chuyển dần thay vì đổi phụt */
section[data-testid="stSidebar"], div[data-testid="stForm"], div[data-testid="stExpander"] details,
div[data-testid="stAlert"], .profile-card, .main-title, .big-table-title, .stApp p, .stApp label {
    transition: background-color 0.35s ease, color 0.35s ease, border-color 0.35s ease, box-shadow 0.35s ease;
}
/* Nút chọn thiết bị, bảng, liên kết: chuyển trạng thái mượt */
a, label[data-testid="stRadioOption"], div[data-testid="stDataFrame"] {
    transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
/* Cuộn thanh bên mượt, không kéo theo cả trang */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    scroll-behavior: smooth;
    overscroll-behavior: contain;
}
@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    div[data-testid="stAlert"], [data-testid="stExpanderDetails"], div[data-testid="stPopoverBody"],
    [data-baseweb="popover"] ul[role="listbox"] { animation: none !important; }
}

/* ---------- Thanh cuộn mảnh ---------- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: rgba(100, 116, 139, 0.35); border-radius: 999px; }
::-webkit-scrollbar-track { background: transparent; }
'''

# Phần CSS thay đổi theo từng trang (ảnh nền) được tách riêng và rất nhỏ,
# để khi đổi trang trình duyệt không phải xử lý lại toàn bộ CSS lớn.
BG_CSS_TEMPLATE = r'''
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: __APP_BG__;
    background-size: cover;
    background-position: center;
    animation: __BG_ANIM__ 0.45s ease-out both;
    will-change: opacity;
}
@keyframes __BG_ANIM__ {
    from { opacity: 0.35; }
    to   { opacity: 1; }
}
'''


# ==========================================
# 🌐 BỘ DỊCH GIAO DIỆN (Tiếng Việt → English)
# ==========================================
VI_EN = {
    # --- Tiêu đề & menu ---
    "🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU": "🚢 SHIPCONTROL - SHIP WORK MANAGEMENT",
    "🔐 Xác Thực": "🔐 Sign In",
    "Vui lòng đăng nhập hoặc đăng ký để tiếp tục.": "Please sign in or register to continue.",
    "🧰 Bảng Công Việc": "🧰 Task Board",
    "➕ Thêm Công Việc": "➕ Add Task",
    "📋 Giao Việc": "📋 Assign Tasks",
    "👥 Team Của Tôi": "👥 My Team",
    "✏️ Chỉnh Sửa/Xóa": "✏️ Edit / Delete",
    "👥 Quản Lý Phân Quyền": "👥 Roles & Permissions",
    "🗑️ Thùng Rác": "🗑️ Trash",
    "📊 Báo Cáo & Khai Báo": "📊 Reports",
    "🔑 Đổi Mật Khẩu": "🔑 Change Password",
    "🚪 Đăng Xuất": "🚪 Log Out",
    "⚙️ Cài đặt": "⚙️ Settings",
    "📲 Thiết bị": "📲 Device",
    "📲 Bạn đang dùng:": "📲 You are using:",
    "💻 Máy tính": "💻 Computer",
    "📱 Điện thoại": "📱 Phone",
    "🎤 Bấm nút micro trong ô nhập chữ để nói thay vì gõ.": "🎤 Tap the microphone in a text box to speak instead of typing.",
    "🎤 Chế độ điện thoại: bấm nút micro trong ô Tên tài khoản để nói thay vì gõ.":
        "🎤 Phone mode: tap the microphone in the Username box to speak instead of typing.",
    "Trình duyệt này chưa hỗ trợ nhập bằng giọng nói. Hãy dùng Chrome (Android) hoặc Safari (iPhone).":
        "This browser doesn't support voice input yet. Please use Chrome (Android) or Safari (iPhone).",
    "Chưa được phép dùng micro. Hãy cho phép micro cho trang web này trong cài đặt trình duyệt.":
        "Microphone access is blocked. Please allow the microphone for this site in your browser settings.",
    "🏭 Workshop: xem danh sách / thêm / xóa": "🏭 Workshops: view / add / delete",
    "Chưa có Workshop nào. Hãy thêm Workshop đầu tiên bên dưới.": "No workshops yet. Add the first one below.",
    "#### ➕ Thêm Workshop Mới": "#### ➕ Add New Workshop",
    "Mã Workshop (Ví dụ: WOS_07):": "Workshop code (e.g. WOS_07):",
    "➕ THÊM WORKSHOP": "➕ ADD WORKSHOP",
    "Mã tối đa 20 ký tự, tên tối đa 80 ký tự!": "Code max 20 characters, name max 80 characters!",
    "#### 🗑️ Xóa Workshop": "#### 🗑️ Delete Workshop",
    "Chọn Workshop để xóa:": "Workshop to delete:",
    "🗑️ XÓA WORKSHOP": "🗑️ DELETE WORKSHOP",
    "Tên Workshop": "Workshop name",
    "Số tài khoản": "Accounts",
    "Số công việc": "Tasks",
    "🎨 Chủ đề": "🎨 Theme",
    "✨ Hiện đại (Modern)": "✨ Modern",
    "🚀 Tương lai (Futuristic)": "🚀 Futuristic",
    "🎈 Vui nhộn (Playful)": "🎈 Playful",
    "📜 Cổ điển (Old times)": "📜 Old times",
    "Chủ đề Tương lai luôn dùng nền tối.": "The Futuristic theme is always dark.",
    ">Tài khoản<": ">Account<",
    "🔒 Tài khoản của bạn vừa được mở ở một tab hoặc thiết bị khác, nên bạn đã bị đăng xuất khỏi trang này. ":
        "🔒 Your account was just opened in another tab or on another device, so you have been signed out here. ",
    "Nếu đó không phải bạn, hãy đăng nhập lại và đổi mật khẩu ngay.":
        "If that wasn't you, sign in again and change your password right away.",
    ">Vai trò<": ">Role<",
    ">Đang đăng nhập<": ">Signed in<",
    "🌙 Chế độ Tối (Dark)": "🌙 Dark mode",
    "🌐 Ngôn ngữ": "🌐 Language",

    # --- Tiêu đề trang ---
    "📋 Bảng Quản Lý Tiến Độ Công Việc": "📋 Task Progress Board",
    "➕ Thêm Công Việc Mới": "➕ Add New Task",
    "✏️ Chỉnh Sửa & Xóa Quản Lý": "✏️ Edit & Delete",
    "👥 Quản Lý & Cấp Quyền Tài Khoản (Role List)": "👥 Accounts & Roles (Role List)",
    "📊 Báo Cáo & Thống Kê Tiến Độ": "📊 Progress Reports & Statistics",
    "🗑️ Thùng Rác & Khôi Phục Tổng Hợp": "🗑️ Trash & Restore",
    "### ⚡ Cập Nhật Tiến Độ Công Việc Nhanh": "### ⚡ Quick Progress Update",
    "### 🏭 Thống Kê Theo Workshop": "### 🏭 Statistics by Workshop",
    "### 📈 Phân Bố Tiến Độ Công Việc": "### 📈 Task Progress Distribution",
    "### 📌 Giao Việc Cho Worker": "### 📌 Assign Tasks to Workers",
    "### 📥 Tải Báo Cáo Dữ Liệu": "### 📥 Download Report Data",
    "### 🔄 Thay Đổi Quyền Hạn Cho Tài Khoản": "### 🔄 Change Account Role",
    "#### ➕ Thêm Worker": "#### ➕ Add Workers",
    "#### ➖ Xóa Khỏi Team": "#### ➖ Remove from Team",
    "#### 👷 Thành Viên": "#### 👷 Members",
    "#### 🚪 Rời Team": "#### 🚪 Leave Team",

    # --- Đăng nhập / đăng ký ---
    "🔑 Đăng Nhập": "🔑 Sign In",
    "📝 Đăng Ký Tài Khoản": "📝 Register",
    "Tên tài khoản (Username):": "Username:",
    "Mật khẩu (Password):": "Password:",
    "🚀 ĐĂNG NHẬP": "🚀 SIGN IN",
    "✨ ĐĂNG KÝ NGAY": "✨ REGISTER NOW",
    "Họ và Tên:": "Full name:",
    "Tên đăng nhập mới (Username):": "New username:",
    "Xác nhận lại mật khẩu:": "Confirm password:",
    "Vui lòng nhập đầy đủ Username và Mật khẩu!": "Please enter both username and password!",
    "Sai tên tài khoản, mật khẩu hoặc tài khoản đã bị khóa/xóa!": "Wrong username or password, or the account is locked/deleted!",
    "⏳ Tài khoản của bạn đang chờ Admin / WOS Manager cấp Role. Vui lòng quay lại sau!": "⏳ Your account is waiting for an Admin / WOS Manager to assign a role. Please come back later!",
    "Chào mừng ": "Welcome ",
    ") đã quay trở lại!": ") is back!",
    "Vui lòng điền đầy đủ các thông tin!": "Please fill in all fields!",
    "Mật khẩu phải có ít nhất 8 ký tự!": "Password must be at least 8 characters!",
    "Username hoặc Họ tên quá dài!": "Username or full name is too long!",
    "Mật khẩu xác nhận không trùng khớp!": "Passwords do not match!",
    "Tên đăng nhập này đã tồn tại, vui lòng chọn tên khác!": "This username already exists, please choose another!",
    "🎉 Đăng ký thành công! Tài khoản đang chờ WOS Manager phê duyệt Role.": "🎉 Registered! Your account is waiting for a WOS Manager to approve a role.",

    # --- Bảng công việc ---
    "👷 Đây là các công việc được giao cho bạn.": "👷 These are the tasks assigned to you.",
    "Chỉ xem công việc của team tôi": "Show only my team's tasks",
    "Chưa có công việc nào để hiển thị.": "No tasks to show yet.",
    "Bạn chưa có công việc nào để cập nhật tiến độ.": "You have no tasks to update.",
    "Chọn công việc cần cập nhật tiến độ:": "Choose a task to update:",
    "Mức Tiến Độ Mới (%)": "New progress (%)",
    "Ghi Chú Thi Công (Remark):": "Work note (Remark):",
    "🚀 CẬP NHẬT TIẾN ĐỘ": "🚀 UPDATE PROGRESS",
    "Đã cập nhật tiến độ công việc thành công!": "Task progress updated!",
    " (Hiện tại: ": " (Current: ",

    # --- Thêm công việc ---
    "⚙️ Thêm / Xóa trong danh sách Block và WS Cost Code": "⚙️ Add / Remove Blocks and WS Cost Codes",
    "Block mới (Ví dụ: 170150):": "New block (e.g. 170150):",
    "➕ THÊM BLOCK": "➕ ADD BLOCK",
    "Vui lòng nhập tên Block!": "Please enter a block name!",
    "Đã thêm Block **": "Added block **",
    "Chọn Block để xóa:": "Block to delete:",
    "🗑️ XÓA BLOCK": "🗑️ DELETE BLOCK",
    "Đã xóa Block **": "Deleted block **",
    "Danh sách Block đang trống.": "The block list is empty.",
    "Mã (Ví dụ: WOS_07):": "Code (e.g. WOS_07):",
    "Tên Workshop / Phòng ban:": "Workshop / department name:",
    "➕ THÊM COST CODE": "➕ ADD COST CODE",
    "Vui lòng nhập cả Mã và Tên!": "Please enter both code and name!",
    "Chọn Cost Code để xóa:": "Cost code to delete:",
    "🗑️ XÓA COST CODE": "🗑️ DELETE COST CODE",
    "Danh sách Cost Code đang trống.": "The cost code list is empty.",
    "Không thể xóa: còn **": "Can't delete: **",
    "** tài khoản thuộc workshop này. Hãy chuyển họ sang workshop khác ở 👥 Quản Lý Phân Quyền trước.":
        "** account(s) still belong to this workshop. Move them to another workshop in 👥 Roles & Permissions first.",
    "** khỏi danh sách. Công việc cũ vẫn giữ nguyên.": "** from the list. Existing tasks are kept.",
    "** đã có trong danh sách!": "** is already in the list!",
    "Mã **": "Code **",
    "Đã thêm **": "Added **",
    "Đã xóa **": "Deleted **",
    "Description (Mô tả công việc):": "Description:",
    "Initial By (Người khởi tạo):": "Initial By:",
    "Initial Date (Ngày tạo):": "Initial Date:",
    "In Charge By (Người phụ trách):": "In Charge By:",
    "Remark (Ghi chú):": "Remark:",
    "— Không chọn —": "— None —",
    "📌 Công việc này sẽ thuộc team của bạn. Vào 📋 Giao Việc để giao cho Worker.":
        "📌 This task will belong to your team. Go to 📋 Assign Tasks to give it to a worker.",
    "💾 LƯU CÔNG VIỆC MỚI": "💾 SAVE NEW TASK",
    "Vui lòng điền đầy đủ thông tin bắt buộc: Task ID và Task Name!": "Please fill in the required fields: Task ID and Task Name!",
    "Plan Finish Date không được trước Plan Start Date!": "Plan Finish Date can't be before Plan Start Date!",
    "** đã tồn tại (có thể đang trong Thùng Rác). Vui lòng dùng ID khác!": "** already exists (it may be in the Trash). Please use another ID!",
    "Đã lưu thành công công việc **": "Saved task **",
    "⚠️ CHƯA CÓ WS COST CODE: Foreman / WOS Manager hãy thêm Cost Code ở mục ⚙️ phía trên trước khi thêm công việc!":
        "⚠️ NO WS COST CODE YET: a Foreman / WOS Manager must add one in the ⚙️ section above before adding tasks!",

    # --- Giao việc ---
    "👑 Chọn công việc và giao cho một **Team Leader** hoặc **Foreman**. Họ sẽ giao tiếp cho Worker trong team.":
        "👑 Choose a task and assign it to a **Team Leader** or **Foreman**. They will pass it on to workers in their team.",
    "Chưa có công việc nào. Vào ➕ Thêm Công Việc để tạo.": "No tasks yet. Go to ➕ Add Task to create one.",
    "Chưa có Team Leader / Foreman nào. Vào 👥 Quản Lý Phân Quyền để cấp role trước.":
        "No Team Leaders / Foremen yet. Assign roles in 👥 Roles & Permissions first.",
    "Chỉ hiện công việc chưa giao": "Show only unassigned tasks",
    "Tất cả công việc đã được giao!": "All tasks have been assigned!",
    "Chọn công việc:": "Choose a task:",
    "Giao cho Team Leader / Foreman:": "Assign to Team Leader / Foreman:",
    "Giao cho Worker:": "Assign to worker:",
    "— Chưa giao —": "— Unassigned —",
    "Chưa giao": "Unassigned",
    "💾 LƯU GIAO VIỆC": "💾 SAVE ASSIGNMENT",
    "Đã giao công việc cho **": "Task assigned to **",
    "Team của bạn chưa có Worker nào. Vào 👥 Team Của Tôi để tạo team và thêm Worker.":
        "Your team has no workers yet. Go to 👥 My Team to create a team and add workers.",
    "Bạn chưa được giao công việc nào.": "You haven't been given any tasks yet.",
    "Cần có Worker trong team trước khi giao việc.": "You need workers in your team before assigning tasks.",
    "(chưa đặt tên)": "(unnamed)",

    # --- Team ---
    "⚠️ Tài khoản của bạn chưa được gán Workshop. Nhờ WOS Manager gán Workshop trước khi lập team.":
        "⚠️ Your account has no workshop yet. Ask a WOS Manager to assign one before creating a team.",
    "Bạn chưa có team. Hãy đặt tên để tạo team.": "You don't have a team yet. Give it a name to create one.",
    "Tên Team *": "Team name *",
    "Ví dụ: Team Hàn Block 170": "e.g. Welding Team Block 170",
    "➕ TẠO TEAM": "➕ CREATE TEAM",
    "Vui lòng nhập tên team!": "Please enter a team name!",
    "Tên team tối đa 60 ký tự!": "Team name can be at most 60 characters!",
    "Đã tạo team **": "Created team **",
    "✏️ Đổi tên team": "✏️ Rename team",
    "Tên team mới:": "New team name:",
    "💾 LƯU TÊN": "💾 SAVE NAME",
    "Tên team không hợp lệ (1–60 ký tự)!": "Invalid team name (1–60 characters)!",
    "Đã đổi tên team!": "Team renamed!",
    "🗑️ Xóa team": "🗑️ Delete team",
    "Khi xóa team: tất cả Worker sẽ rời team, và các công việc đang giao cho họ sẽ trở về trạng thái chưa giao. Công việc vẫn thuộc về bạn, bạn có thể tạo team mới sau.":
        "Deleting the team: all workers leave the team and their tasks become unassigned. The tasks stay with you, and you can create a new team later.",
    "Tôi chắc chắn muốn xóa team này": "I'm sure I want to delete this team",
    "🗑️ XÓA TEAM": "🗑️ DELETE TEAM",
    "Đã xóa team.": "Team deleted.",
    "Team chưa có Worker nào.": "The team has no workers yet.",
    "Không còn Worker nào trong workshop ": "No workers left in workshop ",
    " chưa có team.": " without a team.",
    "Chọn Worker (cùng workshop, chưa có team):": "Choose workers (same workshop, no team yet):",
    "➕ THÊM VÀO TEAM": "➕ ADD TO TEAM",
    "Hãy chọn ít nhất 1 Worker!": "Choose at least 1 worker!",
    " Worker vào team!": " worker(s) to the team!",
    "Đã thêm ": "Added ",
    "Chưa có thành viên để xóa.": "No members to remove.",
    "Chọn Worker:": "Choose a worker:",
    "➖ XÓA KHỎI TEAM": "➖ REMOVE FROM TEAM",
    "Đã xóa Worker khỏi team. Các việc của team giao cho người này đã được bỏ giao.":
        "Worker removed from the team. Their team tasks are now unassigned.",
    "Bạn chưa thuộc team nào. Team Leader / Foreman trong workshop của bạn có thể thêm bạn vào team.":
        "You're not in a team yet. A Team Leader / Foreman in your workshop can add you.",
    "(Team chưa đặt tên)": "(Unnamed team)",
    "**Trưởng team:** ": "**Team leader:** ",
    "Khi rời team, các công việc của team đang giao cho bạn sẽ trở về trạng thái chưa giao.":
        "When you leave, the team tasks assigned to you become unassigned.",
    "Tôi chắc chắn muốn rời team này": "I'm sure I want to leave this team",
    "🚪 RỜI TEAM": "🚪 LEAVE TEAM",
    "Bạn đã rời team.": "You left the team.",

    # --- Chỉnh sửa / xóa ---
    "🧰 Xóa Tạm Công Việc": "🧰 Move Tasks to Trash",
    "👤 Xóa Tạm Tài Khoản Người Dùng": "👤 Lock User Accounts",
    "Hiện không có công việc nào để chỉnh sửa hoặc xóa.": "There are no tasks to edit or delete.",
    "Chọn công việc cần chuyển vào Thùng Rác:": "Task to move to Trash:",
    "🗑️ Chuyển Công Việc Vào Thùng Rác": "🗑️ Move Task to Trash",
    "Đã chuyển công việc vào Thùng Rác thành công!": "Task moved to Trash!",
    "Không có tài khoản khác khả dụng để xóa.": "No other accounts available to delete.",
    "Chọn tài khoản muốn khóa/xóa tạm:": "Account to lock:",
    "🗑️ Khóa/Xóa Tạm Tài Khoản Này": "🗑️ Lock This Account",
    "Đã khóa/chuyển tài khoản vào Thùng Rác thành công!": "Account locked and moved to Trash!",

    # --- Phân quyền ---
    "🛡️ Admin chỉ cấp quyền **WOS Manager** và chọn **Workshop** mà Manager đó phụ trách. Các role Worker / Team Leader / Foreman do WOS Manager cấp.":
        "🛡️ The Admin only grants the **WOS Manager** role and chooses the **Workshop** that manager runs. Worker / Team Leader / Foreman roles are given by WOS Managers.",
    "👑 Bạn có thể cấp **Worker / Team Leader / Foreman**, chọn **Workshop**, và xếp Worker vào **team** của một Team Leader / Foreman.":
        "👑 You can give **Worker / Team Leader / Foreman** roles, choose the **Workshop**, and put workers into a Team Leader / Foreman's **team**.",
    "Không có tài khoản nào để cấp quyền.": "No accounts to assign roles to.",
    "Chọn tài khoản cần chuyển đổi Role:": "Account to change:",
    "Chọn thao tác:": "Action:",
    "👑 Cấp quyền WOS Manager": "👑 Make WOS Manager",
    "⛔ Thu hồi quyền (về Pending)": "⛔ Revoke role (back to Pending)",
    "Workshop mà Manager này phụ trách:": "Workshop this manager runs:",
    "⚠️ Chưa có Workshop nào. Vào ➕ Thêm Công Việc → ⚙️ Thêm / Xóa trong danh sách để thêm.":
        "⚠️ No workshops yet. Add them in ➕ Add Task → ⚙️ Add / Remove.",
    "💾 LƯU THAY ĐỔI ROLE": "💾 SAVE ROLE",
    "💾 LƯU THAY ĐỔI": "💾 SAVE CHANGES",
    "Đã cấp **WOS Manager** cho workshop **": "Made **WOS Manager** of workshop **",
    "Đã thu hồi quyền, tài khoản trở về trạng thái Pending.": "Role revoked, the account is back to Pending.",
    "Chọn Role Mới:": "New role:",
    "Thuộc team của (Team Leader / Foreman):": "Team of (Team Leader / Foreman):",
    "— Chưa xếp team —": "— No team —",
    "Workshop này chưa có Team Leader / Foreman nào.": "This workshop has no Team Leader / Foreman yet.",
    "Đã cập nhật: **": "Updated: **",
    "Họ và Tên": "Full name",
    "Vai Trò (Role)": "Role",
    "Team của": "Team of",

    # --- Thùng rác ---
    "🧰 Thùng Rác Công Việc": "🧰 Task Trash",
    "👤 Thùng Rác Tài Khoản": "👤 Account Trash",
    "Thùng rác công việc đang trống.": "The task trash is empty.",
    "Thùng rác tài khoản đang trống.": "The account trash is empty.",
    "Chọn công việc để xử lý:": "Choose a task:",
    "♻️ KHÔI PHỤC CÔNG VIỆC": "♻️ RESTORE TASK",
    "💥 XÓA VĨNH VIỄN CÔNG VIỆC": "💥 DELETE TASK FOREVER",
    "Đã khôi phục công việc!": "Task restored!",
    "Đã xóa vĩnh viễn công việc!": "Task permanently deleted!",
    "Chọn tài khoản để xử lý:": "Choose an account:",
    "♻️ MỞ KHÓA / KHÔI PHỤC TÀI KHOẢN": "♻️ UNLOCK / RESTORE ACCOUNT",
    "💥 XÓA VĨNH VIỄN TÀI KHOẢN": "💥 DELETE ACCOUNT FOREVER",
    "Đã khôi phục tài khoản người dùng!": "Account restored!",
    "Đã xóa vĩnh viễn tài khoản khỏi cơ sở dữ liệu!": "Account permanently deleted from the database!",

    # --- Báo cáo ---
    "Chưa có dữ liệu công việc để tạo báo cáo. Vui lòng thêm công việc trước!": "No task data for a report yet. Please add tasks first!",
    "Tổng Số Công Việc": "Total tasks",
    "Tổng Công Việc": "Total tasks",
    "Tiến Độ Trung Bình (%)": "Average progress (%)",
    "Tiến Độ Trung Bình": "Average progress",
    "Đã Hoàn Thành (100%)": "Completed (100%)",
    "Đang Thực Hiện": "In progress",
    "Số Lượng Công Việc": "Number of tasks",
    "Trạng Thái": "Status",
    "📥 Tải Báo Cáo Bảng Công Việc (File CSV/Excel)": "📥 Download Task Report (CSV/Excel)",

    # --- Đổi mật khẩu ---
    "Mật khẩu hiện tại:": "Current password:",
    "Mật khẩu mới (ít nhất 8 ký tự):": "New password (at least 8 characters):",
    "Nhập lại mật khẩu mới:": "Repeat new password:",
    "💾 ĐỔI MẬT KHẨU": "💾 CHANGE PASSWORD",
    "Mật khẩu hiện tại không đúng!": "Current password is wrong!",
    "Mật khẩu mới phải có ít nhất 8 ký tự!": "New password must be at least 8 characters!",
    "Không được dùng lại mật khẩu mặc định!": "You can't reuse the default password!",
    "✅ Đã đổi mật khẩu thành công! Các thiết bị khác đã bị đăng xuất.": "✅ Password changed! Other devices have been logged out.",
    "⚠️ Tài khoản này vẫn dùng mật khẩu mặc định 'admin123'. Vào mục 🔑 Đổi Mật Khẩu và đổi NGAY!":
        "⚠️ This account still uses the default password 'admin123'. Go to 🔑 Change Password and change it NOW!",
    # --- Biểu đồ ---
    "Chưa bắt đầu (0%)": "Not started (0%)",
    "Đang làm (1-50%)": "In progress (1-50%)",
    "Sắp xong (51-99%)": "Almost done (51-99%)",
    "Hoàn thành (100%)": "Done (100%)",
    "Số Lượng": "Count",
    "Mật khẩu mới:": "New password:",
    "💬 Tin Nhắn": "💬 Messages",
    "📢 Kênh chung": "📢 General chat",
    "#### 👥 Mọi người": "#### 👥 People",
    "🔎 Tìm tài khoản": "🔎 Find account",
    "Không tìm thấy tài khoản.": "No account found.",
    "Mọi người trong app đều thấy kênh này.": "Everyone in the app can see this channel.",
    "Tin nhắn riêng với ": "Private chat with ",
    "Nhập tin nhắn...": "Type a message...",
    "➕ Tạo nhóm chat": "➕ Create group chat",
    "Tên nhóm": "Group name",
    "Ví dụ: Tổ hàn Block 170": "e.g. Welding crew Block 170",
    "Thêm người vào nhóm": "Add people to the group",
    "✨ TẠO NHÓM": "✨ CREATE GROUP",
    "Vui lòng đặt tên nhóm!": "Please name the group!",
    "Hãy chọn ít nhất 1 người!": "Choose at least 1 person!",
    "Đã tạo nhóm **": "Created group **",
    "#### 💬 Nhóm chat": "#### 💬 Group chats",
    "⚙️ Thành viên nhóm": "⚙️ Group members",
    "➕ THÊM VÀO NHÓM": "➕ ADD TO GROUP",
    " người vào nhóm!": " people to the group!",
    "Xóa khỏi nhóm": "Remove from group",
    "➖ XÓA KHỎI NHÓM": "➖ REMOVE FROM GROUP",
    "Đã xóa khỏi nhóm.": "Removed from the group.",
    "🗑️ XÓA NHÓM": "🗑️ DELETE GROUP",
    "Chỉ người tạo nhóm mới thêm / xóa được thành viên.": "Only the group creator can add / remove members.",
    "🚪 RỜI NHÓM": "🚪 LEAVE GROUP",
    "🎥 Họp Online": "🎥 Online Meetings",
    "### 🔑 Vào cuộc họp": "### 🔑 Join a meeting",
    "ID phòng họp": "Meeting room ID",
    "Mật khẩu phòng": "Room password",
    "🎥 VÀO PHÒNG": "🎥 JOIN",
    "Bạn đã nhập sai quá nhiều lần. Hãy tải lại trang và thử lại sau.": "Too many wrong attempts. Reload the page and try again later.",
    "Sai ID phòng hoặc mật khẩu, hoặc cuộc họp đã kết thúc!": "Wrong room ID or password, or the meeting has ended!",
    "✅ Đúng mã phòng: **": "✅ Room found: **",
    "Chủ phòng": "Host",
    "🎥 MỞ PHÒNG HỌP (camera + micro)": "🎥 OPEN MEETING (camera + mic)",
    "Phòng họp mở trong tab mới. Lần đầu, trình duyệt sẽ hỏi quyền dùng camera và micro — hãy bấm Cho phép.": "The meeting opens in a new tab. The first time, your browser will ask to use the camera and microphone — tap Allow.",
    "### ➕ Tạo cuộc họp mới": "### ➕ Create a new meeting",
    "Tên cuộc họp *": "Meeting name *",
    "Ví dụ: Họp giao ca sáng": "e.g. Morning shift handover",
    "Ngày họp": "Date",
    "Giờ họp": "Time",
    "Mời người (gửi ID + mật khẩu qua 💬 Tin Nhắn)": "Invite people (sends ID + password via 💬 Messages)",
    "📢 Thông báo vào Kênh chung": "📢 Announce in General chat",
    "🎥 TẠO CUỘC HỌP": "🎥 CREATE MEETING",
    "Vui lòng nhập tên cuộc họp!": "Please enter a meeting name!",
    "🎥 Mời họp": "🎥 Meeting invite",
    "🕒 Thời gian": "🕒 Time",
    "🔢 ID phòng": "🔢 Room ID",
    "🔑 Mật khẩu": "🔑 Password",
    "👉 Vào mục 🎥 Họp Online để tham gia.": "👉 Go to 🎥 Online Meetings to join.",
    "🎉 Đã tạo cuộc họp **": "🎉 Created meeting **",
    "### 📋 Cuộc họp của tôi": "### 📋 My meetings",
    "Bạn chưa có cuộc họp nào.": "You have no meetings yet.",
    "▶️ BẮT ĐẦU": "▶️ START",
    "⛔ KẾT THÚC": "⛔ END",
    "Chỉ Foreman và Team Leader mới tạo được cuộc họp. Bạn có thể vào họp khi có ID phòng và mật khẩu.": "Only Foremen and Team Leaders can create meetings. You can join with a room ID and password.",
    "Chọn người...": "Choose people...",
    "👑 Quản trị nhóm": "👑 Group admin",
    "🗑️ Xóa tin nhắn (quản trị)": "🗑️ Delete messages (admin)",
    "Chưa có tin nhắn để xóa.": "No messages to delete.",
    "Chọn tin nhắn để xóa": "Message to delete",
    "🗑️ XÓA TIN NHẮN": "🗑️ DELETE MESSAGE",
    "Đã xóa tin nhắn.": "Message deleted.",
    "Tôi chắc chắn muốn xóa toàn bộ tin nhắn": "I'm sure I want to delete all messages",
    "🧹 XÓA TOÀN BỘ TIN NHẮN": "🧹 DELETE ALL MESSAGES",
    "Đã xóa toàn bộ tin nhắn.": "All messages deleted.",
    "Mời người (họ sẽ thấy lời mời trong 🎥 Họp Online)": "Invite people (they'll see the invite in 🎥 Online Meetings)",
    "### 📨 Lời mời họp của bạn": "### 📨 Your meeting invites",
    "🎥 VÀO HỌP": "🎥 JOIN MEETING",
    "💬 Tin Nhắn & Họp": "💬 Messages & Meetings",
}

# 🌏 Bản dịch Trung / Nhật / Hàn: cùng thứ tự với VI_EN (mỗi dòng khớp một câu tiếng Việt)
_ZH_LIST = [
    "🚢 SHIPCONTROL - 船舶工作管理",
    "🔐 登录",
    "请登录或注册以继续。",
    "🧰 任务看板",
    "➕ 添加任务",
    "📋 分配任务",
    "👥 我的团队",
    "✏️ 编辑 / 删除",
    "👥 角色与权限",
    "🗑️ 回收站",
    "📊 报告",
    "🔑 修改密码",
    "🚪 退出登录",
    "⚙️ 设置",
    "📲 设备",
    "📲 您正在使用：",
    "💻 电脑",
    "📱 手机",
    "🎤 点击文本框中的麦克风，用说话代替打字。",
    "🎤 手机模式：点击用户名框中的麦克风，用说话代替打字。",
    "此浏览器暂不支持语音输入。请使用 Chrome（安卓）或 Safari（iPhone）。",
    "麦克风权限被阻止。请在浏览器设置中允许本网站使用麦克风。",
    "🏭 车间：查看 / 添加 / 删除",
    "还没有车间。请在下方添加第一个。",
    "#### ➕ 添加新车间",
    "车间代码（例如 WOS_07）：",
    "➕ 添加车间",
    "代码最多 20 个字符，名称最多 80 个字符！",
    "#### 🗑️ 删除车间",
    "要删除的车间：",
    "🗑️ 删除车间",
    "车间名称",
    "账号数",
    "任务数",
    "🎨 主题",
    "✨ 现代",
    "🚀 未来",
    "🎈 活泼",
    "📜 复古",
    "未来主题始终为深色。",
    ">账号<",
    "🔒 您的账号刚在另一个标签页或设备上打开，因此您已在此处退出。",
    "如果不是您本人，请重新登录并立即修改密码。",
    ">角色<",
    ">已登录<",
    "🌙 深色模式",
    "🌐 语言",
    "📋 任务进度看板",
    "➕ 添加新任务",
    "✏️ 编辑与删除",
    "👥 账号与角色（角色列表）",
    "📊 进度报告与统计",
    "🗑️ 回收站与恢复",
    "### ⚡ 快速更新进度",
    "### 🏭 按车间统计",
    "### 📈 任务进度分布",
    "### 📌 给工人分配任务",
    "### 📥 下载报告数据",
    "### 🔄 更改账号角色",
    "#### ➕ 添加工人",
    "#### ➖ 移出团队",
    "#### 👷 成员",
    "#### 🚪 退出团队",
    "🔑 登录",
    "📝 注册",
    "用户名：",
    "密码：",
    "🚀 登录",
    "✨ 立即注册",
    "姓名：",
    "新用户名：",
    "确认密码：",
    "请输入用户名和密码！",
    "用户名或密码错误，或账号已被锁定/删除！",
    "⏳ 您的账号正在等待管理员 / WOS Manager 分配角色。请稍后再来！",
    "欢迎 ",
    "）回来了！",
    "请填写所有信息！",
    "密码至少需要 8 个字符！",
    "用户名或姓名太长！",
    "两次输入的密码不一致！",
    "该用户名已存在，请换一个！",
    "🎉 注册成功！您的账号正在等待 WOS Manager 批准角色。",
    "👷 这些是分配给您的任务。",
    "只显示我团队的任务",
    "暂无可显示的任务。",
    "您没有需要更新的任务。",
    "选择要更新的任务：",
    "新进度 (%)",
    "施工备注：",
    "🚀 更新进度",
    "任务进度已更新！",
    "（当前：",
    "⚙️ 添加 / 删除分段和 WS 成本代码",
    "新分段（例如 170150）：",
    "➕ 添加分段",
    "请输入分段名称！",
    "已添加分段 **",
    "要删除的分段：",
    "🗑️ 删除分段",
    "已删除分段 **",
    "分段列表为空。",
    "代码（例如 WOS_07）：",
    "车间 / 部门名称：",
    "➕ 添加成本代码",
    "请输入代码和名称！",
    "要删除的成本代码：",
    "🗑️ 删除成本代码",
    "成本代码列表为空。",
    "无法删除：还有 **",
    "** 个账号属于此车间。请先在 👥 角色与权限 中将他们移到其他车间。",
    "** 已从列表中删除。现有任务保持不变。",
    "** 已在列表中！",
    "代码 **",
    "已添加 **",
    "已删除 **",
    "描述：",
    "创建人：",
    "创建日期：",
    "负责人：",
    "备注：",
    "— 无 —",
    "📌 此任务将属于您的团队。前往 📋 分配任务 把它交给工人。",
    "💾 保存新任务",
    "请填写必填项：Task ID 和 Task Name！",
    "计划完成日期不能早于计划开始日期！",
    "** 已存在（可能在回收站中）。请使用其他 ID！",
    "已保存任务 **",
    "⚠️ 还没有 WS 成本代码：Foreman / WOS Manager 需先在上方 ⚙️ 部分添加！",
    "👑 选择一个任务并分配给 **Team Leader** 或 **Foreman**。他们会再分配给团队中的工人。",
    "还没有任务。前往 ➕ 添加任务 创建。",
    "还没有 Team Leader / Foreman。请先在 👥 角色与权限 中分配角色。",
    "只显示未分配的任务",
    "所有任务都已分配！",
    "选择任务：",
    "分配给 Team Leader / Foreman：",
    "分配给工人：",
    "— 未分配 —",
    "未分配",
    "💾 保存分配",
    "任务已分配给 **",
    "您的团队还没有工人。前往 👥 我的团队 创建团队并添加工人。",
    "您还没有被分配任何任务。",
    "分配任务前，团队中需要有工人。",
    "（未命名）",
    "⚠️ 您的账号还没有车间。请先让 WOS Manager 分配车间再创建团队。",
    "您还没有团队。请起个名字来创建团队。",
    "团队名称 *",
    "例如：170 分段焊接队",
    "➕ 创建团队",
    "请输入团队名称！",
    "团队名称最多 60 个字符！",
    "已创建团队 **",
    "✏️ 重命名团队",
    "新团队名称：",
    "💾 保存名称",
    "团队名称无效（1–60 个字符）！",
    "团队已重命名！",
    "🗑️ 删除团队",
    "删除团队后：所有工人将离开团队，他们的任务变为未分配。任务仍归您所有，之后可以创建新团队。",
    "我确定要删除这个团队",
    "🗑️ 删除团队",
    "团队已删除。",
    "团队还没有工人。",
    "车间 ",
    " 中已没有未加入团队的工人。",
    "选择工人（同一车间，尚无团队）：",
    "➕ 加入团队",
    "请至少选择 1 名工人！",
    " 名工人加入团队！",
    "已将 ",
    "没有可移除的成员。",
    "选择工人：",
    "➖ 移出团队",
    "已将工人移出团队。其团队任务现为未分配。",
    "您还没有加入团队。您车间的 Team Leader / Foreman 可以把您加入团队。",
    "（未命名团队）",
    "**队长：** ",
    "离开后，分配给您的团队任务将变为未分配。",
    "我确定要离开这个团队",
    "🚪 离开团队",
    "您已离开团队。",
    "🧰 将任务移到回收站",
    "👤 锁定用户账号",
    "没有可编辑或删除的任务。",
    "要移到回收站的任务：",
    "🗑️ 将任务移到回收站",
    "任务已移到回收站！",
    "没有其他可删除的账号。",
    "要锁定的账号：",
    "🗑️ 锁定此账号",
    "账号已锁定并移到回收站！",
    "🛡️ 管理员只授予 **WOS Manager** 角色并选择其负责的 **车间**。Worker / Team Leader / Foreman 角色由 WOS Manager 分配。",
    "👑 您可以分配 **Worker / Team Leader / Foreman** 角色、选择 **车间**，并把工人加入 Team Leader / Foreman 的 **团队**。",
    "没有可分配角色的账号。",
    "要更改的账号：",
    "操作：",
    "👑 设为 WOS Manager",
    "⛔ 撤销角色（恢复为待审核）",
    "该经理负责的车间：",
    "⚠️ 还没有车间。请在 ➕ 添加任务 → ⚙️ 添加 / 删除 中添加。",
    "💾 保存角色",
    "💾 保存更改",
    "已设为 **WOS Manager**，车间 **",
    "角色已撤销，账号恢复为待审核。",
    "新角色：",
    "所属团队（Team Leader / Foreman）：",
    "— 无团队 —",
    "该车间还没有 Team Leader / Foreman。",
    "已更新：**",
    "姓名",
    "角色",
    "所属团队",
    "🧰 任务回收站",
    "👤 账号回收站",
    "任务回收站为空。",
    "账号回收站为空。",
    "选择任务：",
    "♻️ 恢复任务",
    "💥 永久删除任务",
    "任务已恢复！",
    "任务已永久删除！",
    "选择账号：",
    "♻️ 解锁 / 恢复账号",
    "💥 永久删除账号",
    "账号已恢复！",
    "账号已从数据库中永久删除！",
    "还没有可生成报告的任务数据。请先添加任务！",
    "任务总数",
    "任务总数",
    "平均进度 (%)",
    "平均进度",
    "已完成 (100%)",
    "进行中",
    "任务数量",
    "状态",
    "📥 下载任务报告（CSV/Excel）",
    "当前密码：",
    "新密码（至少 8 个字符）：",
    "再次输入新密码：",
    "💾 修改密码",
    "当前密码错误！",
    "新密码至少需要 8 个字符！",
    "不能再次使用默认密码！",
    "✅ 密码已修改！其他设备已退出登录。",
    "⚠️ 此账号仍在使用默认密码 'admin123'。请立即前往 🔑 修改密码 进行修改！",
    "未开始 (0%)",
    "进行中 (1-50%)",
    "即将完成 (51-99%)",
    "已完成 (100%)",
    "数量",
    "新密码：",
    "💬 消息",
    "📢 公共频道",
    "#### 👥 成员",
    "🔎 查找账号",
    "未找到账号。",
    "应用中的所有人都能看到此频道。",
    "私聊：",
    "输入消息...",
    "➕ 创建群聊",
    "群名称",
    "例如：170 分段焊接组",
    "添加成员",
    "✨ 创建群组",
    "请为群组命名！",
    "请至少选择 1 人！",
    "已创建群组 **",
    "#### 💬 群聊",
    "⚙️ 群成员",
    "➕ 加入群组",
    " 人加入群组！",
    "移出群组",
    "➖ 移出群组",
    "已移出群组。",
    "🗑️ 删除群组",
    "只有群主可以添加 / 移除成员。",
    "🚪 退出群组",
    "🎥 在线会议",
    "### 🔑 加入会议",
    "会议室 ID",
    "会议密码",
    "🎥 加入",
    "输入错误次数过多。请刷新页面后再试。",
    "会议室 ID 或密码错误，或会议已结束！",
    "✅ 已找到会议：**",
    "主持人",
    "🎥 打开会议（摄像头 + 麦克风）",
    "会议将在新标签页中打开。首次使用时，浏览器会请求摄像头和麦克风权限——请点击允许。",
    "### ➕ 创建新会议",
    "会议名称 *",
    "例如：早班交接会",
    "日期",
    "时间",
    "邀请成员（通过 💬 消息发送 ID 和密码）",
    "📢 在公共频道通知",
    "🎥 创建会议",
    "请输入会议名称！",
    "🎥 会议邀请",
    "🕒 时间",
    "🔢 会议室 ID",
    "🔑 密码",
    "👉 前往 🎥 在线会议 加入。",
    "🎉 已创建会议 **",
    "### 📋 我的会议",
    "您还没有会议。",
    "▶️ 开始",
    "⛔ 结束",
    "只有 Foreman 和 Team Leader 可以创建会议。有会议室 ID 和密码即可加入。",
    "选择成员...",
    "👑 群管理员",
    "🗑️ 删除消息（管理员）",
    "没有可删除的消息。",
    "选择要删除的消息",
    "🗑️ 删除消息",
    "消息已删除。",
    "我确定要删除所有消息",
    "🧹 删除所有消息",
    "已删除所有消息。",
    "邀请成员（他们会在 🎥 在线会议 中看到邀请）",
    "### 📨 您的会议邀请",
    "🎥 加入会议",
    "💬 消息与会议",
]
_JA_LIST = [
    "🚢 SHIPCONTROL - 船舶作業管理",
    "🔐 ログイン",
    "続けるにはログインまたは登録してください。",
    "🧰 タスクボード",
    "➕ タスク追加",
    "📋 タスク割り当て",
    "👥 マイチーム",
    "✏️ 編集 / 削除",
    "👥 役割と権限",
    "🗑️ ゴミ箱",
    "📊 レポート",
    "🔑 パスワード変更",
    "🚪 ログアウト",
    "⚙️ 設定",
    "📲 デバイス",
    "📲 使用中のデバイス：",
    "💻 パソコン",
    "📱 スマホ",
    "🎤 入力欄のマイクをタップすると、入力の代わりに話せます。",
    "🎤 スマホモード：ユーザー名欄のマイクをタップすると、入力の代わりに話せます。",
    "このブラウザは音声入力に対応していません。Chrome（Android）または Safari（iPhone）をご利用ください。",
    "マイクへのアクセスがブロックされています。ブラウザの設定でこのサイトのマイクを許可してください。",
    "🏭 ワークショップ：一覧 / 追加 / 削除",
    "ワークショップがまだありません。下から最初の1つを追加してください。",
    "#### ➕ 新しいワークショップを追加",
    "ワークショップコード（例：WOS_07）：",
    "➕ ワークショップを追加",
    "コードは最大20文字、名前は最大80文字です！",
    "#### 🗑️ ワークショップを削除",
    "削除するワークショップ：",
    "🗑️ ワークショップを削除",
    "ワークショップ名",
    "アカウント数",
    "タスク数",
    "🎨 テーマ",
    "✨ モダン",
    "🚀 フューチャー",
    "🎈 ポップ",
    "📜 レトロ",
    "フューチャーテーマは常にダークです。",
    ">アカウント<",
    "🔒 別のタブまたは端末でこのアカウントが開かれたため、ここではログアウトしました。",
    "心当たりがない場合は、再度ログインしてすぐにパスワードを変更してください。",
    ">役割<",
    ">ログイン中<",
    "🌙 ダークモード",
    "🌐 言語",
    "📋 タスク進捗ボード",
    "➕ 新しいタスクを追加",
    "✏️ 編集と削除",
    "👥 アカウントと役割（役割一覧）",
    "📊 進捗レポートと統計",
    "🗑️ ゴミ箱と復元",
    "### ⚡ 進捗をすばやく更新",
    "### 🏭 ワークショップ別の統計",
    "### 📈 タスク進捗の分布",
    "### 📌 作業員にタスクを割り当て",
    "### 📥 レポートデータをダウンロード",
    "### 🔄 アカウントの役割を変更",
    "#### ➕ 作業員を追加",
    "#### ➖ チームから外す",
    "#### 👷 メンバー",
    "#### 🚪 チームを抜ける",
    "🔑 ログイン",
    "📝 新規登録",
    "ユーザー名：",
    "パスワード：",
    "🚀 ログイン",
    "✨ 今すぐ登録",
    "氏名：",
    "新しいユーザー名：",
    "パスワード（確認）：",
    "ユーザー名とパスワードを入力してください！",
    "ユーザー名かパスワードが違うか、アカウントがロック/削除されています！",
    "⏳ アカウントは Admin / WOS Manager による役割の割り当てを待っています。後でもう一度お試しください！",
    "ようこそ ",
    "）さん、おかえりなさい！",
    "すべての項目を入力してください！",
    "パスワードは8文字以上にしてください！",
    "ユーザー名または氏名が長すぎます！",
    "パスワードが一致しません！",
    "このユーザー名は既に使われています。別の名前を選んでください！",
    "🎉 登録完了！アカウントは WOS Manager による役割の承認を待っています。",
    "👷 あなたに割り当てられたタスクです。",
    "自分のチームのタスクのみ表示",
    "表示するタスクはまだありません。",
    "更新できるタスクがありません。",
    "更新するタスクを選択：",
    "新しい進捗 (%)",
    "作業メモ（Remark）：",
    "🚀 進捗を更新",
    "タスクの進捗を更新しました！",
    "（現在：",
    "⚙️ ブロックと WS コストコードの追加 / 削除",
    "新しいブロック（例：170150）：",
    "➕ ブロックを追加",
    "ブロック名を入力してください！",
    "ブロックを追加しました **",
    "削除するブロック：",
    "🗑️ ブロックを削除",
    "ブロックを削除しました **",
    "ブロック一覧は空です。",
    "コード（例：WOS_07）：",
    "ワークショップ / 部署名：",
    "➕ コストコードを追加",
    "コードと名前の両方を入力してください！",
    "削除するコストコード：",
    "🗑️ コストコードを削除",
    "コストコード一覧は空です。",
    "削除できません：まだ **",
    "** 件のアカウントがこのワークショップに所属しています。先に 👥 役割と権限 で別のワークショップへ移してください。",
    "** を一覧から削除しました。既存のタスクはそのままです。",
    "** は既に一覧にあります！",
    "コード **",
    "追加しました **",
    "削除しました **",
    "説明：",
    "作成者：",
    "作成日：",
    "担当者：",
    "備考：",
    "— なし —",
    "📌 このタスクはあなたのチームのものになります。📋 タスク割り当て で作業員に渡してください。",
    "💾 新しいタスクを保存",
    "必須項目を入力してください：Task ID と Task Name！",
    "計画完了日を計画開始日より前にはできません！",
    "** は既に存在します（ゴミ箱にある可能性があります）。別の ID を使ってください！",
    "タスクを保存しました **",
    "⚠️ WS コストコードがまだありません：Foreman / WOS Manager が上の ⚙️ で追加してください！",
    "👑 タスクを選んで **Team Leader** または **Foreman** に割り当てます。その人がチームの作業員に割り振ります。",
    "タスクがまだありません。➕ タスク追加 で作成してください。",
    "Team Leader / Foreman がまだいません。先に 👥 役割と権限 で役割を割り当ててください。",
    "未割り当てのタスクのみ表示",
    "すべてのタスクが割り当て済みです！",
    "タスクを選択：",
    "Team Leader / Foreman に割り当て：",
    "作業員に割り当て：",
    "— 未割り当て —",
    "未割り当て",
    "💾 割り当てを保存",
    "タスクを割り当てました **",
    "チームに作業員がいません。👥 マイチーム でチームを作り、作業員を追加してください。",
    "まだタスクが割り当てられていません。",
    "タスクを割り当てる前に、チームに作業員が必要です。",
    "（名前なし）",
    "⚠️ アカウントにワークショップがありません。チームを作る前に WOS Manager に割り当ててもらってください。",
    "まだチームがありません。名前を付けてチームを作成してください。",
    "チーム名 *",
    "例：ブロック170 溶接チーム",
    "➕ チームを作成",
    "チーム名を入力してください！",
    "チーム名は最大60文字です！",
    "チームを作成しました **",
    "✏️ チーム名を変更",
    "新しいチーム名：",
    "💾 名前を保存",
    "チーム名が無効です（1〜60文字）！",
    "チーム名を変更しました！",
    "🗑️ チームを削除",
    "チームを削除すると、作業員は全員チームを抜け、割り当て中のタスクは未割り当てになります。タスクはあなたに残り、後で新しいチームを作れます。",
    "このチームを削除します",
    "🗑️ チームを削除",
    "チームを削除しました。",
    "チームにはまだ作業員がいません。",
    "ワークショップ ",
    " にはチーム未所属の作業員がいません。",
    "作業員を選択（同じワークショップ、チーム未所属）：",
    "➕ チームに追加",
    "作業員を1人以上選んでください！",
    " 人の作業員をチームに追加しました！",
    "",
    "外せるメンバーがいません。",
    "作業員を選択：",
    "➖ チームから外す",
    "作業員をチームから外しました。その人のチームタスクは未割り当てになりました。",
    "まだチームに入っていません。同じワークショップの Team Leader / Foreman が追加できます。",
    "（名前のないチーム）",
    "**チームリーダー：** ",
    "チームを抜けると、あなたに割り当てられたチームタスクは未割り当てになります。",
    "このチームを抜けます",
    "🚪 チームを抜ける",
    "チームを抜けました。",
    "🧰 タスクをゴミ箱へ",
    "👤 ユーザーアカウントをロック",
    "編集・削除できるタスクがありません。",
    "ゴミ箱へ移すタスク：",
    "🗑️ タスクをゴミ箱へ移す",
    "タスクをゴミ箱へ移しました！",
    "削除できる他のアカウントがありません。",
    "ロックするアカウント：",
    "🗑️ このアカウントをロック",
    "アカウントをロックしてゴミ箱へ移しました！",
    "🛡️ Admin は **WOS Manager** の役割を付与し、担当する **ワークショップ** を選ぶだけです。Worker / Team Leader / Foreman の役割は WOS Manager が付与します。",
    "👑 **Worker / Team Leader / Foreman** の役割付与、**ワークショップ** の選択、Team Leader / Foreman の **チーム** への作業員配置ができます。",
    "役割を割り当てるアカウントがありません。",
    "変更するアカウント：",
    "操作：",
    "👑 WOS Manager にする",
    "⛔ 役割を取り消す（承認待ちに戻す）",
    "このマネージャーが担当するワークショップ：",
    "⚠️ ワークショップがまだありません。➕ タスク追加 → ⚙️ 追加 / 削除 で追加してください。",
    "💾 役割を保存",
    "💾 変更を保存",
    "**WOS Manager** に設定しました。ワークショップ **",
    "役割を取り消し、アカウントは承認待ちに戻りました。",
    "新しい役割：",
    "所属チーム（Team Leader / Foreman）：",
    "— チームなし —",
    "このワークショップには Team Leader / Foreman がまだいません。",
    "更新しました：**",
    "氏名",
    "役割",
    "所属チーム",
    "🧰 タスクのゴミ箱",
    "👤 アカウントのゴミ箱",
    "タスクのゴミ箱は空です。",
    "アカウントのゴミ箱は空です。",
    "タスクを選択：",
    "♻️ タスクを復元",
    "💥 タスクを完全に削除",
    "タスクを復元しました！",
    "タスクを完全に削除しました！",
    "アカウントを選択：",
    "♻️ アカウントのロック解除 / 復元",
    "💥 アカウントを完全に削除",
    "アカウントを復元しました！",
    "アカウントをデータベースから完全に削除しました！",
    "レポートを作るタスクデータがまだありません。先にタスクを追加してください！",
    "タスク総数",
    "タスク総数",
    "平均進捗 (%)",
    "平均進捗",
    "完了 (100%)",
    "進行中",
    "タスク数",
    "状態",
    "📥 タスクレポートをダウンロード（CSV/Excel）",
    "現在のパスワード：",
    "新しいパスワード（8文字以上）：",
    "新しいパスワード（再入力）：",
    "💾 パスワードを変更",
    "現在のパスワードが違います！",
    "新しいパスワードは8文字以上にしてください！",
    "初期パスワードは再利用できません！",
    "✅ パスワードを変更しました！他の端末はログアウトされました。",
    "⚠️ このアカウントはまだ初期パスワード 'admin123' を使っています。今すぐ 🔑 パスワード変更 で変更してください！",
    "未着手 (0%)",
    "作業中 (1-50%)",
    "もうすぐ完了 (51-99%)",
    "完了 (100%)",
    "件数",
    "新しいパスワード：",
    "💬 メッセージ",
    "📢 全体チャット",
    "#### 👥 メンバー",
    "🔎 アカウント検索",
    "アカウントが見つかりません。",
    "アプリの全員がこのチャンネルを見られます。",
    "個別チャット：",
    "メッセージを入力...",
    "➕ グループチャットを作成",
    "グループ名",
    "例：ブロック170 溶接班",
    "メンバーを追加",
    "✨ グループを作成",
    "グループ名を入力してください！",
    "1人以上選んでください！",
    "グループを作成しました **",
    "#### 💬 グループチャット",
    "⚙️ グループメンバー",
    "➕ グループに追加",
    " 人をグループに追加しました！",
    "グループから外す",
    "➖ グループから外す",
    "グループから外しました。",
    "🗑️ グループを削除",
    "メンバーの追加 / 削除はグループ作成者だけができます。",
    "🚪 グループを抜ける",
    "🎥 オンライン会議",
    "### 🔑 会議に参加",
    "会議室 ID",
    "会議パスワード",
    "🎥 参加",
    "入力ミスが多すぎます。ページを再読み込みして後でもう一度お試しください。",
    "会議室 ID またはパスワードが違うか、会議は終了しています！",
    "✅ 会議が見つかりました：**",
    "主催者",
    "🎥 会議を開く（カメラ + マイク）",
    "会議は新しいタブで開きます。初回はブラウザがカメラとマイクの使用許可を求めるので「許可」をタップしてください。",
    "### ➕ 新しい会議を作成",
    "会議名 *",
    "例：朝の引き継ぎ会議",
    "日付",
    "時刻",
    "参加者を招待（💬 メッセージで ID とパスワードを送信）",
    "📢 全体チャットでお知らせ",
    "🎥 会議を作成",
    "会議名を入力してください！",
    "🎥 会議の招待",
    "🕒 日時",
    "🔢 会議室 ID",
    "🔑 パスワード",
    "👉 🎥 オンライン会議 から参加してください。",
    "🎉 会議を作成しました **",
    "### 📋 自分の会議",
    "まだ会議はありません。",
    "▶️ 開始",
    "⛔ 終了",
    "会議を作成できるのは Foreman と Team Leader だけです。会議室 ID とパスワードがあれば参加できます。",
    "メンバーを選択...",
    "👑 グループ管理者",
    "🗑️ メッセージ削除（管理者）",
    "削除できるメッセージはありません。",
    "削除するメッセージ",
    "🗑️ メッセージを削除",
    "メッセージを削除しました。",
    "すべてのメッセージを削除します",
    "🧹 すべてのメッセージを削除",
    "すべてのメッセージを削除しました。",
    "参加者を招待（🎥 オンライン会議 に招待が表示されます）",
    "### 📨 あなたへの会議の招待",
    "🎥 会議に参加",
    "💬 メッセージと会議",
]
_KO_LIST = [
    "🚢 SHIPCONTROL - 선박 작업 관리",
    "🔐 로그인",
    "계속하려면 로그인하거나 회원가입하세요.",
    "🧰 작업 보드",
    "➕ 작업 추가",
    "📋 작업 배정",
    "👥 내 팀",
    "✏️ 편집 / 삭제",
    "👥 역할 및 권한",
    "🗑️ 휴지통",
    "📊 보고서",
    "🔑 비밀번호 변경",
    "🚪 로그아웃",
    "⚙️ 설정",
    "📲 기기",
    "📲 사용 중인 기기:",
    "💻 컴퓨터",
    "📱 휴대폰",
    "🎤 입력창의 마이크를 누르면 타이핑 대신 말로 입력할 수 있습니다.",
    "🎤 휴대폰 모드: 사용자 이름 칸의 마이크를 누르면 타이핑 대신 말로 입력할 수 있습니다.",
    "이 브라우저는 아직 음성 입력을 지원하지 않습니다. Chrome(안드로이드) 또는 Safari(iPhone)를 사용하세요.",
    "마이크 접근이 차단되었습니다. 브라우저 설정에서 이 사이트의 마이크를 허용하세요.",
    "🏭 작업장: 보기 / 추가 / 삭제",
    "아직 작업장이 없습니다. 아래에서 첫 작업장을 추가하세요.",
    "#### ➕ 새 작업장 추가",
    "작업장 코드 (예: WOS_07):",
    "➕ 작업장 추가",
    "코드는 최대 20자, 이름은 최대 80자입니다!",
    "#### 🗑️ 작업장 삭제",
    "삭제할 작업장:",
    "🗑️ 작업장 삭제",
    "작업장 이름",
    "계정 수",
    "작업 수",
    "🎨 테마",
    "✨ 모던",
    "🚀 퓨처리스틱",
    "🎈 플레이풀",
    "📜 레트로",
    "퓨처리스틱 테마는 항상 어두운 모드입니다.",
    ">계정<",
    "🔒 다른 탭이나 기기에서 계정이 열려 이곳에서는 로그아웃되었습니다. ",
    "본인이 아니라면 다시 로그인하여 즉시 비밀번호를 변경하세요.",
    ">역할<",
    ">로그인됨<",
    "🌙 다크 모드",
    "🌐 언어",
    "📋 작업 진행 보드",
    "➕ 새 작업 추가",
    "✏️ 편집 및 삭제",
    "👥 계정 및 역할 (역할 목록)",
    "📊 진행 보고서 및 통계",
    "🗑️ 휴지통 및 복원",
    "### ⚡ 빠른 진행 상황 업데이트",
    "### 🏭 작업장별 통계",
    "### 📈 작업 진행 분포",
    "### 📌 작업자에게 작업 배정",
    "### 📥 보고서 데이터 다운로드",
    "### 🔄 계정 역할 변경",
    "#### ➕ 작업자 추가",
    "#### ➖ 팀에서 제외",
    "#### 👷 팀원",
    "#### 🚪 팀 나가기",
    "🔑 로그인",
    "📝 회원가입",
    "사용자 이름:",
    "비밀번호:",
    "🚀 로그인",
    "✨ 지금 가입",
    "이름:",
    "새 사용자 이름:",
    "비밀번호 확인:",
    "사용자 이름과 비밀번호를 모두 입력하세요!",
    "사용자 이름 또는 비밀번호가 틀렸거나 계정이 잠김/삭제되었습니다!",
    "⏳ 계정이 Admin / WOS Manager의 역할 배정을 기다리고 있습니다. 나중에 다시 오세요!",
    "환영합니다 ",
    ")님, 다시 오셨네요!",
    "모든 항목을 입력하세요!",
    "비밀번호는 8자 이상이어야 합니다!",
    "사용자 이름 또는 이름이 너무 깁니다!",
    "비밀번호가 일치하지 않습니다!",
    "이미 사용 중인 사용자 이름입니다. 다른 이름을 선택하세요!",
    "🎉 가입 완료! 계정이 WOS Manager의 역할 승인을 기다리고 있습니다.",
    "👷 나에게 배정된 작업입니다.",
    "내 팀의 작업만 보기",
    "표시할 작업이 없습니다.",
    "업데이트할 작업이 없습니다.",
    "업데이트할 작업 선택:",
    "새 진행률 (%)",
    "작업 메모 (Remark):",
    "🚀 진행률 업데이트",
    "작업 진행률이 업데이트되었습니다!",
    " (현재: ",
    "⚙️ 블록 및 WS 원가 코드 추가 / 삭제",
    "새 블록 (예: 170150):",
    "➕ 블록 추가",
    "블록 이름을 입력하세요!",
    "블록을 추가했습니다 **",
    "삭제할 블록:",
    "🗑️ 블록 삭제",
    "블록을 삭제했습니다 **",
    "블록 목록이 비어 있습니다.",
    "코드 (예: WOS_07):",
    "작업장 / 부서 이름:",
    "➕ 원가 코드 추가",
    "코드와 이름을 모두 입력하세요!",
    "삭제할 원가 코드:",
    "🗑️ 원가 코드 삭제",
    "원가 코드 목록이 비어 있습니다.",
    "삭제할 수 없습니다: 아직 **",
    "**개의 계정이 이 작업장에 속해 있습니다. 먼저 👥 역할 및 권한에서 다른 작업장으로 옮기세요.",
    "** 을(를) 목록에서 삭제했습니다. 기존 작업은 유지됩니다.",
    "** 은(는) 이미 목록에 있습니다!",
    "코드 **",
    "추가했습니다 **",
    "삭제했습니다 **",
    "설명:",
    "작성자:",
    "작성일:",
    "담당자:",
    "비고:",
    "— 없음 —",
    "📌 이 작업은 내 팀에 속합니다. 📋 작업 배정에서 작업자에게 넘기세요.",
    "💾 새 작업 저장",
    "필수 항목을 입력하세요: Task ID와 Task Name!",
    "계획 완료일은 계획 시작일보다 빠를 수 없습니다!",
    "** 은(는) 이미 존재합니다(휴지통에 있을 수 있음). 다른 ID를 사용하세요!",
    "작업을 저장했습니다 **",
    "⚠️ 아직 WS 원가 코드가 없습니다: Foreman / WOS Manager가 위의 ⚙️ 에서 먼저 추가해야 합니다!",
    "👑 작업을 골라 **Team Leader** 또는 **Foreman**에게 배정하세요. 그들이 팀의 작업자에게 나눠 줍니다.",
    "아직 작업이 없습니다. ➕ 작업 추가에서 만드세요.",
    "아직 Team Leader / Foreman이 없습니다. 먼저 👥 역할 및 권한에서 역할을 배정하세요.",
    "미배정 작업만 보기",
    "모든 작업이 배정되었습니다!",
    "작업 선택:",
    "Team Leader / Foreman에게 배정:",
    "작업자에게 배정:",
    "— 미배정 —",
    "미배정",
    "💾 배정 저장",
    "작업을 배정했습니다 **",
    "팀에 작업자가 없습니다. 👥 내 팀에서 팀을 만들고 작업자를 추가하세요.",
    "아직 배정된 작업이 없습니다.",
    "작업을 배정하려면 팀에 작업자가 있어야 합니다.",
    "(이름 없음)",
    "⚠️ 계정에 작업장이 없습니다. 팀을 만들기 전에 WOS Manager에게 작업장 배정을 요청하세요.",
    "아직 팀이 없습니다. 이름을 정해 팀을 만드세요.",
    "팀 이름 *",
    "예: 170블록 용접팀",
    "➕ 팀 만들기",
    "팀 이름을 입력하세요!",
    "팀 이름은 최대 60자입니다!",
    "팀을 만들었습니다 **",
    "✏️ 팀 이름 변경",
    "새 팀 이름:",
    "💾 이름 저장",
    "팀 이름이 올바르지 않습니다 (1–60자)!",
    "팀 이름을 변경했습니다!",
    "🗑️ 팀 삭제",
    "팀을 삭제하면 모든 작업자가 팀에서 나가고 그들의 작업은 미배정이 됩니다. 작업은 그대로 내게 남으며 나중에 새 팀을 만들 수 있습니다.",
    "이 팀을 삭제하겠습니다",
    "🗑️ 팀 삭제",
    "팀을 삭제했습니다.",
    "팀에 아직 작업자가 없습니다.",
    "작업장 ",
    "에는 팀이 없는 작업자가 더 이상 없습니다.",
    "작업자 선택 (같은 작업장, 팀 없음):",
    "➕ 팀에 추가",
    "작업자를 1명 이상 선택하세요!",
    "명의 작업자를 팀에 추가했습니다!",
    "",
    "제외할 팀원이 없습니다.",
    "작업자 선택:",
    "➖ 팀에서 제외",
    "작업자를 팀에서 제외했습니다. 그 작업자의 팀 작업은 미배정이 되었습니다.",
    "아직 팀에 속해 있지 않습니다. 같은 작업장의 Team Leader / Foreman이 추가할 수 있습니다.",
    "(이름 없는 팀)",
    "**팀장:** ",
    "팀을 나가면 나에게 배정된 팀 작업은 미배정이 됩니다.",
    "이 팀에서 나가겠습니다",
    "🚪 팀 나가기",
    "팀에서 나갔습니다.",
    "🧰 작업을 휴지통으로",
    "👤 사용자 계정 잠금",
    "편집하거나 삭제할 작업이 없습니다.",
    "휴지통으로 옮길 작업:",
    "🗑️ 작업을 휴지통으로 옮기기",
    "작업을 휴지통으로 옮겼습니다!",
    "삭제할 수 있는 다른 계정이 없습니다.",
    "잠글 계정:",
    "🗑️ 이 계정 잠그기",
    "계정을 잠그고 휴지통으로 옮겼습니다!",
    "🛡️ Admin은 **WOS Manager** 역할을 부여하고 담당 **작업장**만 선택합니다. Worker / Team Leader / Foreman 역할은 WOS Manager가 부여합니다.",
    "👑 **Worker / Team Leader / Foreman** 역할 부여, **작업장** 선택, Team Leader / Foreman의 **팀**에 작업자 배치를 할 수 있습니다.",
    "역할을 배정할 계정이 없습니다.",
    "변경할 계정:",
    "작업:",
    "👑 WOS Manager로 지정",
    "⛔ 역할 회수 (대기 상태로)",
    "이 매니저가 담당하는 작업장:",
    "⚠️ 아직 작업장이 없습니다. ➕ 작업 추가 → ⚙️ 추가 / 삭제에서 추가하세요.",
    "💾 역할 저장",
    "💾 변경 사항 저장",
    "**WOS Manager**로 지정했습니다. 작업장 **",
    "역할을 회수했고 계정이 대기 상태로 돌아갔습니다.",
    "새 역할:",
    "소속 팀 (Team Leader / Foreman):",
    "— 팀 없음 —",
    "이 작업장에는 아직 Team Leader / Foreman이 없습니다.",
    "업데이트됨: **",
    "이름",
    "역할",
    "소속 팀",
    "🧰 작업 휴지통",
    "👤 계정 휴지통",
    "작업 휴지통이 비어 있습니다.",
    "계정 휴지통이 비어 있습니다.",
    "작업 선택:",
    "♻️ 작업 복원",
    "💥 작업 영구 삭제",
    "작업을 복원했습니다!",
    "작업을 영구 삭제했습니다!",
    "계정 선택:",
    "♻️ 계정 잠금 해제 / 복원",
    "💥 계정 영구 삭제",
    "계정을 복원했습니다!",
    "계정을 데이터베이스에서 영구 삭제했습니다!",
    "보고서를 만들 작업 데이터가 없습니다. 먼저 작업을 추가하세요!",
    "전체 작업 수",
    "전체 작업 수",
    "평균 진행률 (%)",
    "평균 진행률",
    "완료 (100%)",
    "진행 중",
    "작업 수",
    "상태",
    "📥 작업 보고서 다운로드 (CSV/Excel)",
    "현재 비밀번호:",
    "새 비밀번호 (8자 이상):",
    "새 비밀번호 다시 입력:",
    "💾 비밀번호 변경",
    "현재 비밀번호가 틀렸습니다!",
    "새 비밀번호는 8자 이상이어야 합니다!",
    "기본 비밀번호는 다시 사용할 수 없습니다!",
    "✅ 비밀번호를 변경했습니다! 다른 기기는 로그아웃되었습니다.",
    "⚠️ 이 계정은 아직 기본 비밀번호 'admin123'을 사용 중입니다. 지금 바로 🔑 비밀번호 변경에서 변경하세요!",
    "시작 전 (0%)",
    "진행 중 (1-50%)",
    "거의 완료 (51-99%)",
    "완료 (100%)",
    "개수",
    "새 비밀번호:",
    "💬 메시지",
    "📢 전체 채팅",
    "#### 👥 사람들",
    "🔎 계정 찾기",
    "계정을 찾을 수 없습니다.",
    "앱의 모든 사람이 이 채널을 볼 수 있습니다.",
    "개인 채팅: ",
    "메시지를 입력하세요...",
    "➕ 그룹 채팅 만들기",
    "그룹 이름",
    "예: 170블록 용접조",
    "그룹에 사람 추가",
    "✨ 그룹 만들기",
    "그룹 이름을 입력하세요!",
    "1명 이상 선택하세요!",
    "그룹을 만들었습니다 **",
    "#### 💬 그룹 채팅",
    "⚙️ 그룹 멤버",
    "➕ 그룹에 추가",
    "명을 그룹에 추가했습니다!",
    "그룹에서 제외",
    "➖ 그룹에서 제외",
    "그룹에서 제외했습니다.",
    "🗑️ 그룹 삭제",
    "그룹을 만든 사람만 멤버를 추가 / 제외할 수 있습니다.",
    "🚪 그룹 나가기",
    "🎥 온라인 회의",
    "### 🔑 회의 참가",
    "회의실 ID",
    "회의실 비밀번호",
    "🎥 참가",
    "잘못 입력한 횟수가 너무 많습니다. 페이지를 새로고침하고 나중에 다시 시도하세요.",
    "회의실 ID 또는 비밀번호가 틀렸거나 회의가 종료되었습니다!",
    "✅ 회의를 찾았습니다: **",
    "호스트",
    "🎥 회의 열기 (카메라 + 마이크)",
    "회의는 새 탭에서 열립니다. 처음에는 브라우저가 카메라와 마이크 사용 권한을 요청하니 허용을 누르세요.",
    "### ➕ 새 회의 만들기",
    "회의 이름 *",
    "예: 아침 교대 회의",
    "날짜",
    "시간",
    "사람 초대 (💬 메시지로 ID와 비밀번호 전송)",
    "📢 전체 채팅에 알리기",
    "🎥 회의 만들기",
    "회의 이름을 입력하세요!",
    "🎥 회의 초대",
    "🕒 시간",
    "🔢 회의실 ID",
    "🔑 비밀번호",
    "👉 🎥 온라인 회의에서 참가하세요.",
    "🎉 회의를 만들었습니다 **",
    "### 📋 내 회의",
    "아직 회의가 없습니다.",
    "▶️ 시작",
    "⛔ 종료",
    "Foreman과 Team Leader만 회의를 만들 수 있습니다. 회의실 ID와 비밀번호가 있으면 참가할 수 있습니다.",
    "사람 선택...",
    "👑 그룹 관리자",
    "🗑️ 메시지 삭제 (관리자)",
    "삭제할 메시지가 없습니다.",
    "삭제할 메시지",
    "🗑️ 메시지 삭제",
    "메시지를 삭제했습니다.",
    "모든 메시지를 삭제하겠습니다",
    "🧹 모든 메시지 삭제",
    "모든 메시지를 삭제했습니다.",
    "사람 초대 (🎥 온라인 회의에서 초대를 보게 됩니다)",
    "### 📨 나의 회의 초대",
    "🎥 회의 참가",
    "💬 메시지 및 회의",
]

_VI_KEYS = list(VI_EN.keys())
TRANSLATIONS = {
    "en": VI_EN,
    "zh": dict(zip(_VI_KEYS, _ZH_LIST)),
    "ja": dict(zip(_VI_KEYS, _JA_LIST)),
    "ko": dict(zip(_VI_KEYS, _KO_LIST)),
}
LANG_OPTIONS = ["vi", "en", "zh", "ja", "ko"]
LANG_LABELS = {"vi": "🇻🇳 Tiếng Việt", "en": "🇬🇧 English", "zh": "🇨🇳 中文", "ja": "🇯🇵 日本語", "ko": "🇰🇷 한국어"}
SPEECH_LANG = {"vi": "vi-VN", "en": "en-US", "zh": "zh-CN", "ja": "ja-JP", "ko": "ko-KR"}


import re as _re
import functools as _functools
from streamlit.delta_generator import DeltaGenerator as _DG

_VI_EN_RX = _re.compile("|".join(_re.escape(k) for k in sorted(VI_EN, key=len, reverse=True)))
LANG_COOKIE = "shipcontrol_lang"


def ui_lang():
    return st.session_state.get("ui_lang", "vi")


def tr(text):
    """Dịch một đoạn chữ sang ngôn ngữ đang chọn (giữ nguyên nếu là Tiếng Việt)."""
    lang = ui_lang()
    if not isinstance(text, str) or not text or lang == "vi" or lang not in TRANSLATIONS:
        return text
    if text.lstrip().startswith("<style"):
        return text
    table = TRANSLATIONS[lang]
    return _VI_EN_RX.sub(lambda m: table.get(m.group(0), VI_EN[m.group(0)]), text)


def _tr_data(data):
    if ui_lang() != "vi" and isinstance(data, pd.DataFrame):
        return data.rename(columns=lambda c: tr(c) if isinstance(c, str) else c)
    return data


def _install_translator():
    """Tự động dịch chữ hiển thị của các thành phần Streamlit.
    Chỉ đổi phần HIỂN THỊ; giá trị trả về và logic của app giữ nguyên tiếng Việt."""
    # Giữ bản gốc của markdown (không dịch) để hiện nội dung người dùng viết, ví dụ tin nhắn
    if not hasattr(_DG, "_sc_orig_markdown"):
        _DG._sc_orig_markdown = getattr(_DG.markdown, "__wrapped__", _DG.markdown)

    def text_first(fn):
        @_functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            if ui_lang() != "vi":
                if args and isinstance(args[0], str):
                    args = (tr(args[0]),) + args[1:]
                for k in ("label", "body", "placeholder", "help"):
                    if isinstance(kwargs.get(k), str):
                        kwargs[k] = tr(kwargs[k])
            return fn(self, *args, **kwargs)
        return wrapper

    def with_options(fn):
        @_functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            if ui_lang() != "vi":
                if args and isinstance(args[0], str):
                    args = (tr(args[0]),) + args[1:]
                for k in ("label", "placeholder", "help"):
                    if isinstance(kwargs.get(k), str):
                        kwargs[k] = tr(kwargs[k])
                _ff = kwargs.get("format_func") or str
                kwargs["format_func"] = lambda o, _ff=_ff: tr(_ff(o))
            return fn(self, *args, **kwargs)
        return wrapper

    def data_first(fn):
        @_functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            if args:
                args = (_tr_data(args[0]),) + args[1:]
            elif "data" in kwargs:
                kwargs["data"] = _tr_data(kwargs["data"])
            return fn(self, *args, **kwargs)
        return wrapper

    def tabs_first(fn):
        @_functools.wraps(fn)
        def wrapper(self, tabs, *args, **kwargs):
            return fn(self, [tr(t) for t in tabs], *args, **kwargs)
        return wrapper

    groups = {
        text_first: ["markdown", "caption", "info", "success", "warning", "error", "title", "header",
                     "subheader", "text", "button", "form_submit_button", "download_button", "text_input",
                     "text_area", "number_input", "date_input", "time_input", "checkbox", "toggle",
                     "expander", "popover", "metric", "slider", "chat_input", "link_button"],
        with_options: ["selectbox", "radio", "multiselect", "select_slider"],
        data_first: ["dataframe", "table"],
        tabs_first: ["tabs"],
    }
    for wrap, names in groups.items():
        for name in names:
            fn = getattr(_DG, name, None)
            if fn is None or getattr(fn, "_sc_wrapped", False):
                continue                      # đã gắn bộ dịch rồi (app chạy lại) → bỏ qua
            wrapped = wrap(fn)
            wrapped._sc_wrapped = True
            setattr(_DG, name, wrapped)


_install_translator()
# st.button, st.markdown... được gắn sẵn vào khung chính lúc import → gắn lại để dùng bản đã dịch
for _name in ["markdown", "caption", "info", "success", "warning", "error", "title", "header", "subheader",
              "text", "button", "form_submit_button", "download_button", "text_input", "text_area",
              "number_input", "date_input", "time_input", "checkbox", "toggle", "expander", "popover",
              "metric", "slider", "selectbox", "radio", "multiselect", "select_slider", "dataframe",
              "table", "tabs", "chat_input", "link_button"]:
    if hasattr(st, _name) and hasattr(st._main, _name):
        setattr(st, _name, getattr(st._main, _name))


# ==========================================
# 🎨 CHỦ ĐỀ GIAO DIỆN (Futuristic / Playful / Modern / Old times)
#    Mỗi chủ đề là một lớp CSS phủ lên giao diện Modern.
#    Dùng "html body ..." để luôn ưu tiên hơn các kiểu gốc.
# ==========================================
THEME_OPTIONS = ["modern", "futuristic", "playful", "oldtimes"]
THEME_LABELS = {
    "modern": "✨ Hiện đại (Modern)",
    "futuristic": "🚀 Tương lai (Futuristic)",
    "playful": "🎈 Vui nhộn (Playful)",
    "oldtimes": "📜 Cổ điển (Old times)",
}

_THEME_FUTURISTIC = r'''
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;500;600;700;800&display=swap');
html body .stApp, html body .stApp p, html body .stApp label, html body .stApp input, html body .stApp textarea,
html body .stApp button, html body .stApp h1, html body .stApp h2, html body .stApp h3, html body .stApp li,
html body .stApp span:not([data-testid="stIconMaterial"]) {
    font-family: 'Twemoji Country Flags', 'Exo 2', system-ui, sans-serif !important;
}
html body .stApp { background: #03060f !important; }
html body .stApp::before {
    background:
        linear-gradient(rgba(34,211,238,0.07) 1px, transparent 1px) 0 0 / 44px 44px,
        linear-gradient(90deg, rgba(34,211,238,0.07) 1px, transparent 1px) 0 0 / 44px 44px,
        radial-gradient(900px 500px at 85% 0%, rgba(232,121,249,0.18), transparent 60%),
        linear-gradient(180deg, rgba(3,6,15,0.70) 0%, rgba(3,6,15,0.90) 50%, rgba(3,6,15,0.96) 100%),
        url('__BG_URL__') center / cover no-repeat !important;
}
html body section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050816 0%, #0a1030 100%) !important;
    border-right: 1px solid rgba(34,211,238,0.45) !important;
    box-shadow: 0 0 30px rgba(34,211,238,0.18) !important;
}
html body .sidebar-header, html body .main-title, html body .big-table-title {
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #67e8f9 !important;
    text-shadow: 0 0 12px rgba(34,211,238,0.65) !important;
}
html body .main-title::after { background: linear-gradient(90deg, #22d3ee, #e879f9) !important; box-shadow: 0 0 14px #22d3ee; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: rgba(34,211,238,0.10) !important;
    border: 1px solid #22d3ee !important;
    border-radius: 6px !important;
    box-shadow: 0 0 16px rgba(34,211,238,0.55), inset 0 0 12px rgba(34,211,238,0.25) !important;
}
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * { color: #a5f3fc !important; -webkit-text-fill-color: #a5f3fc !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] { border-radius: 6px !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover:not(:disabled) {
    background: rgba(232,121,249,0.10) !important; border-color: rgba(232,121,249,0.6) !important;
}
html body .stMain div.stButton > button[kind="primary"],
html body div[data-testid="stFormSubmitButton"] > button,
html body div.stDownloadButton > button {
    background: linear-gradient(90deg, #06b6d4, #a855f7) !important;
    border: 1px solid #67e8f9 !important;
    border-radius: 6px !important;
    box-shadow: 0 0 18px rgba(34,211,238,0.45) !important;
    text-transform: uppercase;
}
html body .stMain div.stButton > button[kind="primary"]:hover:not(:disabled),
html body div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) {
    box-shadow: 0 0 28px rgba(232,121,249,0.7) !important;
}
html body .stMain div.stButton > button[kind="secondary"] {
    background: rgba(8,16,40,0.85) !important;
    border: 1px solid rgba(34,211,238,0.6) !important;
    border-radius: 6px !important;
}
html body .stMain div.stButton > button[kind="secondary"] * { color: #a5f3fc !important; -webkit-text-fill-color: #a5f3fc !important; }
html body div[data-testid="stPopoverBody"] { background: #070c1f !important; }
html body div[data-testid="stForm"], html body div[data-testid="stExpander"] details,
html body div[data-testid="stDataFrame"] {
    background: rgba(8,14,34,0.88) !important;
    border: 1px solid rgba(34,211,238,0.45) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 22px rgba(34,211,238,0.15), inset 0 0 20px rgba(34,211,238,0.05) !important;
}
html body .profile-card { border-color: rgba(34,211,238,0.5) !important; border-radius: 8px !important; box-shadow: 0 0 16px rgba(34,211,238,0.2); }
html body .pc-avatar { background: linear-gradient(135deg, #22d3ee, #a855f7) !important; color: #fff !important; }
html body .made-by-minh { background: linear-gradient(90deg, #22d3ee, #e879f9) !important; border-radius: 6px !important; }
'''

_THEME_PLAYFUL = r'''
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&display=swap');
html body .stApp, html body .stApp p, html body .stApp label, html body .stApp input, html body .stApp textarea,
html body .stApp button, html body .stApp h1, html body .stApp h2, html body .stApp h3, html body .stApp li,
html body .stApp span:not([data-testid="stIconMaterial"]) {
    font-family: 'Twemoji Country Flags', 'Baloo 2', 'Comic Sans MS', system-ui, sans-serif !important;
}
html body .stApp::before {
    background:
        radial-gradient(circle at 12% 18%, rgba(251,191,36,__DOT__) 0 70px, transparent 71px),
        radial-gradient(circle at 88% 12%, rgba(244,114,182,__DOT__) 0 90px, transparent 91px),
        radial-gradient(circle at 80% 85%, rgba(52,211,153,__DOT__) 0 80px, transparent 81px),
        __PLAY_OVERLAY__,
        url('__BG_URL__') center / cover no-repeat !important;
}
html body section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ec4899 0%, #a855f7 55%, #6366f1 100%) !important;
}
html body .sidebar-header { color: #fef08a !important; transform: rotate(-2deg); }
html body .main-title { color: __PLAY_TITLE__ !important; }
html body .main-title::after {
    height: 8px !important; width: 180px !important;
    background: repeating-linear-gradient(90deg, #f472b6 0 20px, #facc15 20px 40px, #34d399 40px 60px, #60a5fa 60px 80px) !important;
}
html body .big-table-title { color: #db2777 !important; }
html body section[data-testid="stSidebar"] div.stButton > button { border-radius: 999px !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #ffffff !important;
    box-shadow: 4px 4px 0 #facc15 !important;
    transform: rotate(-1deg);
}
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * { color: #a21caf !important; -webkit-text-fill-color: #a21caf !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover:not(:disabled) {
    transform: scale(1.04) rotate(-1deg) !important;
}
html body div.stButton > button, html body div[data-testid="stFormSubmitButton"] > button, html body div.stDownloadButton > button {
    border-radius: 999px !important;
    transition: transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.18s ease !important;
}
html body .stMain div.stButton > button[kind="primary"],
html body div[data-testid="stFormSubmitButton"] > button,
html body div.stDownloadButton > button {
    background: linear-gradient(135deg, #fb923c, #ec4899) !important;
    border: 3px solid #1e1b4b !important;
    box-shadow: 5px 5px 0 #1e1b4b !important;
}
html body .stMain div.stButton > button[kind="primary"]:hover:not(:disabled),
html body div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) {
    transform: translate(-2px, -2px) rotate(-1deg) scale(1.03) !important;
    box-shadow: 7px 7px 0 #1e1b4b !important;
}
html body .stMain div.stButton > button[kind="secondary"] {
    border: 3px solid #1e1b4b !important;
    box-shadow: 4px 4px 0 #a855f7 !important;
}
html body div.stButton > button:active:not(:disabled),
html body div[data-testid="stFormSubmitButton"] > button:active:not(:disabled) {
    transform: translate(3px, 3px) !important; box-shadow: 1px 1px 0 #1e1b4b !important;
}
html body div[data-testid="stForm"], html body div[data-testid="stExpander"] details,
html body div[data-testid="stDataFrame"], html body div[data-testid="stPopoverBody"] {
    border: 3px solid #1e1b4b !important;
    border-radius: 24px !important;
    box-shadow: 8px 8px 0 #f472b6 !important;
}
html body div[data-testid="stAlert"] { border: 3px solid #1e1b4b !important; border-radius: 20px !important; }
html body .profile-card { border-radius: 24px !important; border: 3px solid rgba(255,255,255,0.6) !important; }
html body .pc-avatar { background: #fef08a !important; color: #a21caf !important; transform: rotate(-6deg); }
html body .made-by-minh { transform: rotate(-2deg); box-shadow: 4px 4px 0 #1e1b4b !important; }
'''

_THEME_OLDTIMES = r'''
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Playfair+Display:wght@700;800;900&display=swap');
html body .stApp, html body .stApp p, html body .stApp label, html body .stApp input, html body .stApp textarea,
html body .stApp button, html body .stApp li, html body .stApp span:not([data-testid="stIconMaterial"]) {
    font-family: 'Twemoji Country Flags', 'Lora', Georgia, 'Times New Roman', serif !important;
}
html body .stApp h1, html body .stApp h2, html body .stApp h3, html body .main-title,
html body .big-table-title, html body .sidebar-header {
    font-family: 'Twemoji Country Flags', 'Playfair Display', Georgia, serif !important;
    letter-spacing: 0.01em !important;
}
html body .stApp { background: __OLD_PAPER__ !important; }
html body .stApp::before {
    filter: sepia(0.85) contrast(0.95) brightness(__OLD_BRIGHT__);
    background:
        repeating-linear-gradient(0deg, rgba(120,90,50,0.035) 0 2px, transparent 2px 4px),
        __OLD_OVERLAY__,
        url('__BG_URL__') center / cover no-repeat !important;
}
html body section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3b2716 0%, #4e3420 60%, #2e1e10 100%) !important;
    border-right: 4px double #c9a227 !important;
}
html body .sidebar-header { color: #e6c35c !important; }
html body .main-title, html body .big-table-title, html body .stApp h3 { color: __OLD_INK__ !important; }
html body .main-title { border-bottom: 3px double __OLD_INK__ !important; }
html body .main-title::after { display: none !important; }
html body .stMain [data-testid="stWidgetLabel"] p, html body .stMain p { color: __OLD_INK__ !important; -webkit-text-fill-color: __OLD_INK__ !important; }
html body section[data-testid="stSidebar"] div.stButton > button { border-radius: 3px !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #e6c35c, #c9a227) !important;
    border: 1px solid #8a6d12 !important;
    box-shadow: inset 0 0 0 2px rgba(255,255,255,0.35), 0 2px 0 #6b520c !important;
}
html body section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * { color: #2e1e10 !important; -webkit-text-fill-color: #2e1e10 !important; }
html body section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] * { color: #f3e6c4 !important; -webkit-text-fill-color: #f3e6c4 !important; }
html body div.stButton > button, html body div[data-testid="stFormSubmitButton"] > button, html body div.stDownloadButton > button {
    border-radius: 3px !important;
}
html body .stMain div.stButton > button[kind="primary"],
html body div[data-testid="stFormSubmitButton"] > button,
html body div.stDownloadButton > button {
    background: linear-gradient(180deg, #6b4a2b, #4e3420) !important;
    border: 3px double #c9a227 !important;
    box-shadow: 0 3px 0 #2e1e10 !important;
}
html body .stMain div.stButton > button[kind="primary"] *,
html body div[data-testid="stFormSubmitButton"] > button * { color: #f3e6c4 !important; -webkit-text-fill-color: #f3e6c4 !important; }
html body .stMain div.stButton > button[kind="secondary"] {
    background: __OLD_CARD__ !important;
    border: 2px solid #8b6b3d !important;
    box-shadow: 0 2px 0 #8b6b3d !important;
}
html body .stMain div.stButton > button[kind="secondary"] * { color: __OLD_INK__ !important; -webkit-text-fill-color: __OLD_INK__ !important; }
html body div[data-testid="stForm"], html body div[data-testid="stExpander"] details,
html body div[data-testid="stDataFrame"], html body div[data-testid="stPopoverBody"] {
    background: __OLD_CARD__ !important;
    border: 3px double #8b6b3d !important;
    border-radius: 4px !important;
    box-shadow: 0 6px 18px rgba(62,44,28,0.25) !important;
}
html body div[data-testid="stTextInputRootElement"], html body div[data-testid="stTextAreaRootElement"],
html body div[data-testid="stNumberInputContainer"], html body div[data-testid="stDateInputField"],
html body div[data-testid="stSelectbox"] div:has(> input) {
    background-color: __OLD_INPUT__ !important;
    border: 1px solid #8b6b3d !important;
    border-radius: 3px !important;
}
html body .stApp input, html body .stApp textarea, html body div[data-testid="stSelectbox"] div:has(> input) * {
    color: __OLD_INK__ !important; -webkit-text-fill-color: __OLD_INK__ !important;
}
html body .profile-card { border: 1px solid #c9a227 !important; border-radius: 4px !important; }
html body .pc-avatar { background: #c9a227 !important; color: #2e1e10 !important; border: 2px solid #f3e6c4; }
html body .made-by-minh { border-radius: 3px !important; background: linear-gradient(180deg, #e6c35c, #c9a227) !important; }
'''


def build_theme_css(theme, dark, bg_url):
    if theme == "futuristic":
        css = _THEME_FUTURISTIC
        tokens = {}
    elif theme == "playful":
        css = _THEME_PLAYFUL
        tokens = {
            "__DOT__": "0.22" if dark else "0.35",
            "__PLAY_OVERLAY__": ("linear-gradient(180deg, rgba(30,27,75,0.72) 0%, rgba(30,27,75,0.88) 50%, rgba(30,27,75,0.94) 100%)"
                                 if dark else
                                 "linear-gradient(180deg, rgba(255,247,237,0.45) 0%, rgba(255,247,237,0.78) 45%, rgba(253,242,248,0.9) 100%)"),
            "__PLAY_TITLE__": "#fde68a" if dark else "#7c3aed",
        }
    elif theme == "oldtimes":
        css = _THEME_OLDTIMES
        tokens = {
            "__OLD_PAPER__": "#1f160d" if dark else "#efe4c8",
            "__OLD_OVERLAY__": ("linear-gradient(180deg, rgba(31,22,13,0.70) 0%, rgba(31,22,13,0.88) 50%, rgba(31,22,13,0.94) 100%)"
                                if dark else
                                "linear-gradient(180deg, rgba(244,236,216,0.45) 0%, rgba(244,236,216,0.78) 45%, rgba(244,236,216,0.9) 100%)"),
            "__OLD_BRIGHT__": "0.9" if dark else "1",
            "__OLD_INK__": "#f3e6c4" if dark else "#3e2c1c",
            "__OLD_CARD__": "#2b1f13" if dark else "#fbf5e6",
            "__OLD_INPUT__": "#1f160d" if dark else "#fffaf0",
        }
    else:
        return ""
    tokens["__BG_URL__"] = bg_url
    for k, v in tokens.items():
        css = css.replace(k, v)
    return css


# ==========================================
# 🎤 NHẬP BẰNG GIỌNG NÓI (chế độ Điện thoại)
#    Gắn nút 🎤 vào mọi ô nhập chữ. Bấm → nói → chữ tự điền vào ô.
#    Dùng Web Speech API của trình duyệt (miễn phí, không cần API key).
# ==========================================
import streamlit.components.v1 as _components

_VOICE_JS = r"""
<script>
(function () {
  const win = window.parent, doc = win.document;
  const LANG = "__LANG__";
  const MSG_NOSUPPORT = "__MSG_NOSUPPORT__";
  const MSG_DENIED = "__MSG_DENIED__";
  const SR = win.SpeechRecognition || win.webkitSpeechRecognition;

  // Tắt bản cũ (nếu có) trước khi gắn bản mới
  if (win.__scVoice && win.__scVoice.cleanup) { try { win.__scVoice.cleanup(); } catch (e) {} }
  // Gỡ các nút cũ còn sót (của lần tải trước) để gắn lại nút mới hoạt động được
  doc.querySelectorAll(".sc-mic").forEach((b) => b.remove());
  doc.querySelectorAll("[data-sc-mic]").forEach((el) => el.removeAttribute("data-sc-mic"));

  if (!doc.getElementById("sc-mic-style")) {
    const st = doc.createElement("style");
    st.id = "sc-mic-style";
    st.textContent = `
      html body div .sc-mic { position:absolute !important; right:6px !important; top:50% !important;
        transform:translateY(-50%) !important; z-index:5 !important;
        width:38px !important; height:38px !important; min-height:0 !important; border-radius:50% !important;
        border:none !important; cursor:pointer; padding:0 !important; margin:0 !important;
        background:linear-gradient(135deg,#0ea5e9,#0284c7) !important; background-color:#0284c7 !important;
        color:#fff !important; font-size:18px !important; line-height:1 !important;
        box-shadow:0 3px 10px rgba(2,132,199,.4) !important; display:flex !important;
        align-items:center !important; justify-content:center !important; }
      html body div .sc-mic.sc-area { top:auto !important; bottom:8px !important; transform:none !important; }
      html body div .sc-mic.sc-chatmic { right:52px !important; width:34px !important; height:34px !important; }
      [data-testid="stChatInput"].sc-has-mic textarea { padding-right:96px !important; }
      html body div .sc-mic.sc-rec { background:linear-gradient(135deg,#ef4444,#dc2626) !important;
        background-color:#dc2626 !important; animation:scPulse 1s infinite; }
      @keyframes scPulse { 0%{box-shadow:0 0 0 0 rgba(239,68,68,.6)} 100%{box-shadow:0 0 0 14px rgba(239,68,68,0)} }
      .sc-has-mic input, .sc-has-mic textarea { padding-right:50px !important; }
    `;
    doc.head.appendChild(st);
  }

  let active = null;

  function setValue(el, value) {
    const proto = el.tagName === "TEXTAREA" ? win.HTMLTextAreaElement.prototype : win.HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, "value").set.call(el, value);
    el.dispatchEvent(new win.Event("input", { bubbles: true }));
  }
  function commit(el) {
    // Báo cho Streamlit là đã nhập xong (giống như bấm ra ngoài ô)
    el.dispatchEvent(new win.FocusEvent("focusout", { bubbles: true }));
    el.dispatchEvent(new win.FocusEvent("blur"));
  }

  function listen(el, btn) {
    if (!SR) { win.alert(MSG_NOSUPPORT); return; }
    if (active) { active.stop(); return; }
    const rec = new SR();
    rec.lang = LANG; rec.interimResults = true; rec.continuous = false; rec.maxAlternatives = 1;
    const base = el.value ? el.value.replace(/\s+$/, "") + " " : "";
    rec.onresult = (ev) => {
      let text = "";
      for (let i = 0; i < ev.results.length; i++) text += ev.results[i][0].transcript;
      setValue(el, base + text.trim());
    };
    rec.onerror = (ev) => {
      if (ev.error === "not-allowed" || ev.error === "service-not-allowed") win.alert(MSG_DENIED);
    };
    rec.onend = () => { btn.classList.remove("sc-rec"); btn.textContent = "🎤"; active = null; commit(el); };
    active = rec;
    btn.classList.add("sc-rec"); btn.textContent = "⏹";
    try { rec.start(); } catch (e) { active = null; btn.classList.remove("sc-rec"); btn.textContent = "🎤"; }
  }

  function attach(el) {
    if (el.dataset.scMic) return;
    const wrap = el.closest('[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stChatInput"]');
    if (!wrap) return;
    if (el.type === "password") return;              // không gắn vào ô mật khẩu
    el.dataset.scMic = "1";
    wrap.style.position = "relative";
    wrap.classList.add("sc-has-mic");
    const btn = doc.createElement("button");
    btn.type = "button";
    const isChat = !!el.closest('[data-testid="stChatInput"]');
    btn.className = "sc-mic" + (isChat ? " sc-chatmic" : (el.tagName === "TEXTAREA" ? " sc-area" : ""));
    btn.textContent = "🎤";
    btn.setAttribute("aria-label", "Voice input");
    btn.addEventListener("mousedown", (e) => e.preventDefault());   // giữ nguyên con trỏ trong ô
    btn.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); listen(el, btn); });
    wrap.appendChild(btn);
  }

  function scan() {
    doc.querySelectorAll('[data-testid="stTextInputRootElement"] input, [data-testid="stTextAreaRootElement"] textarea, [data-testid="stChatInput"] textarea')
       .forEach(attach);
  }

  scan();
  const obs = new win.MutationObserver(() => scan());
  obs.observe(doc.body, { childList: true, subtree: true });

  win.__scVoice = {
    cleanup() {
      obs.disconnect();
      if (active) { try { active.abort(); } catch (e) {} }
      doc.querySelectorAll(".sc-mic").forEach((b) => b.remove());
      doc.querySelectorAll("[data-sc-mic]").forEach((el) => { delete el.dataset.scMic; });
      doc.querySelectorAll(".sc-has-mic").forEach((w) => w.classList.remove("sc-has-mic"));
    }
  };
})();
</script>
"""

_VOICE_OFF_JS = r"""
<script>
(function () {
  const win = window.parent, doc = win.document;
  if (win.__scVoice && win.__scVoice.cleanup) { try { win.__scVoice.cleanup(); } catch (e) {} }
  win.__scVoice = null;
  // Tự dọn luôn (phòng khi bản cũ đã bị tắt trước): gỡ nút micro và các đánh dấu
  doc.querySelectorAll(".sc-mic").forEach((b) => b.remove());
  doc.querySelectorAll("[data-sc-mic]").forEach((el) => el.removeAttribute("data-sc-mic"));
  doc.querySelectorAll(".sc-has-mic").forEach((w) => w.classList.remove("sc-has-mic"));
})();
</script>
"""


def render_voice_input(enabled):
    """Bật (điện thoại) hoặc tắt (máy tính) nút micro trong các ô nhập chữ."""
    if enabled:
        js = (_VOICE_JS
              .replace("__LANG__", SPEECH_LANG.get(ui_lang(), "vi-VN"))
              .replace("__MSG_NOSUPPORT__", tr("Trình duyệt này chưa hỗ trợ nhập bằng giọng nói. Hãy dùng Chrome (Android) hoặc Safari (iPhone).").replace('"', "'"))
              .replace("__MSG_DENIED__", tr("Chưa được phép dùng micro. Hãy cho phép micro cho trang web này trong cài đặt trình duyệt.").replace('"', "'")))
    else:
        js = _VOICE_OFF_JS
    with st.sidebar:
        _components.html(js, height=0)


DEVICE_OPTIONS = ["desktop", "mobile"]
DEVICE_LABELS = {"desktop": "💻 Máy tính", "mobile": "📱 Điện thoại"}
DEVICE_COOKIE = "shipcontrol_device"


def _guess_device():
    """Đoán thiết bị từ trình duyệt (người dùng vẫn đổi lại được)."""
    try:
        ua = st.context.headers.get("User-Agent", "") or ""
    except Exception:
        ua = ""
    return "mobile" if any(k in ua for k in ("Mobi", "Android", "iPhone", "iPad")) else "desktop"


# ==========================================
# 💬 TIN NHẮN (kênh chung + nhắn riêng)
# ==========================================
CHAT_MENU = "💬 Tin Nhắn"
CONNECT_MENU = "💬 Tin Nhắn & Họp"      # 1 nút menu gộp Tin nhắn + Họp online
CHAT_ROLE_ICONS = {"Admin": "🛡️", "WOS Manager": "👑", "Foreman": "👔", "Team Leader": "🧢", "Worker": "👷"}
_YOU_LABEL = {"vi": "Bạn", "en": "You", "zh": "我", "ja": "自分", "ko": "나"}
_EMPTY_CHAT = {
    "vi": "Chưa có tin nhắn nào. Hãy gửi lời chào đầu tiên! 👋",
    "en": "No messages yet. Say hi! 👋",
    "zh": "还没有消息。来打个招呼吧！👋",
    "ja": "まだメッセージはありません。最初のあいさつを送りましょう！👋",
    "ko": "아직 메시지가 없습니다. 먼저 인사해 보세요! 👋",
}


def dm_conv_id(a, b):
    a, b = int(a), int(b)
    return f"dm:{min(a, b)}:{max(a, b)}"


def dm_other_id(conv, me):
    _, a, b = conv.split(":")
    return int(b) if int(a) == int(me) else int(a)


def chat_unread_by_conv(me):
    """Số tin chưa đọc theo từng cuộc trò chuyện (chỉ những cuộc mình được xem)."""
    rows = cursor.execute("""
        SELECT m.conv, COUNT(*) FROM chat_messages m
        LEFT JOIN chat_reads r ON r.user_id = ? AND r.conv = m.conv
        WHERE m.sender_id != ? AND m.id > COALESCE(r.last_read_id, 0)
          AND (m.conv = 'general'
               OR m.conv IN (SELECT 'group:' || group_id FROM chat_group_members WHERE user_id = ?))
        GROUP BY m.conv
    """, (me, me, me)).fetchall()
    return {c: n for c, n in rows}


def mark_chat_read(me, conv, last_id):
    try:
        cursor.execute("""
            INSERT INTO chat_reads (user_id, conv, last_read_id) VALUES (?, ?, ?)
            ON CONFLICT(user_id, conv) DO UPDATE SET last_read_id = MAX(last_read_id, excluded.last_read_id)
        """, (me, conv, last_id))
    except sqlite3.OperationalError:
        pass


def _chat_time(iso):
    try:
        t = datetime.fromisoformat(iso)
    except Exception:
        return ""
    return t.strftime("%H:%M") if t.date() == datetime.now().date() else t.strftime("%d/%m %H:%M")


def render_chat_messages(msgs, me):
    """Vẽ khung tin nhắn (tin của mình bên phải màu xanh, của người khác bên trái).
    Nội dung tin nhắn KHÔNG đi qua bộ dịch, để giữ đúng chữ người gửi viết."""
    lang = ui_lang()
    if not msgs:
        inner = f"<div class='sc-chat-empty'>{html.escape(_EMPTY_CHAT.get(lang, _EMPTY_CHAT['vi']))}</div>"
    else:
        parts = []
        for mid, sid, body, created, fname, uname, role in msgs:   # mới nhất trước (khung xếp ngược)
            mine = (sid == me)
            name = _YOU_LABEL.get(lang, "Bạn") if mine else (fname or uname or "?")
            icon = "" if mine else CHAT_ROLE_ICONS.get(role, "👤") + " "
            text = html.escape(body or "").replace("\n", "<br>")
            parts.append(
                f"<div class='sc-msg {'sc-mine' if mine else 'sc-theirs'}'>"
                f"<div class='sc-meta'>{html.escape(icon + name)} · {_chat_time(created)}</div>"
                f"<div class='sc-bubble'>{text}</div></div>")
        inner = "".join(parts)
    _DG._sc_orig_markdown(st._main, f"<div class='sc-chat'>{inner}</div>", unsafe_allow_html=True)


def get_secret(key, default=None):
    """Đọc cấu hình bí mật từ .streamlit/secrets.toml (hoặc Secrets trên Streamlit Cloud)."""
    try:
        return st.secrets[key]
    except Exception:
        return default


# 📍 1. ĐƯỜNG LINK TRANG WEB (đặt APP_URL trong Secrets)
APP_URL = get_secret("APP_URL", "https://your-app.streamlit.app")

# ==========================================
# 💬 NHÓM CHAT + 🎥 HỌP ONLINE
# ==========================================
MEETING_MENU = "🎥 Họp Online"
MEETING_HOST_ROLES = ["Foreman", "Team Leader"]
# Máy chủ họp video (Jitsi Meet). Có thể đổi trong Secrets: MEETING_SERVER = "https://..."
MEETING_SERVER = str(get_secret("MEETING_SERVER", "https://meet.jit.si")).rstrip("/")


def is_chat_admin(conv, uid, role):
    """Quản trị của cuộc trò chuyện: nhóm → người tạo nhóm; kênh chung → Admin / WOS Manager."""
    if conv.startswith("group:"):
        row = cursor.execute("SELECT created_by FROM chat_groups WHERE id = ?", (int(conv.split(":")[1]),)).fetchone()
        return bool(row and row[0] == uid)
    if conv == "general":
        return role in ("Admin", "WOS Manager")
    return False


def post_chat_message(conv, sender_id, body):
    cursor.execute("INSERT INTO chat_messages (conv, sender_id, body, created_at) VALUES (?, ?, ?, ?)",
                   (conv, sender_id, str(body).strip()[:2000], datetime.now().isoformat(timespec="seconds")))


def create_chat_group(name, owner_id, member_ids):
    cursor.execute("INSERT INTO chat_groups (name, created_by, created_at) VALUES (?, ?, ?)",
                   (name, owner_id, datetime.now().isoformat(timespec="seconds")))
    gid = cursor.lastrowid
    for uid in set([owner_id] + list(member_ids)):
        cursor.execute("INSERT OR IGNORE INTO chat_group_members (group_id, user_id) VALUES (?, ?)", (gid, uid))
    return gid


def user_chat_groups(me):
    return cursor.execute("""
        SELECT g.id, g.name, g.created_by,
               (SELECT COUNT(*) FROM chat_group_members x WHERE x.group_id = g.id) AS n
        FROM chat_groups g JOIN chat_group_members m ON m.group_id = g.id
        WHERE m.user_id = ? ORDER BY g.name COLLATE NOCASE
    """, (me,)).fetchall()


def is_group_member(gid, uid):
    return cursor.execute("SELECT 1 FROM chat_group_members WHERE group_id = ? AND user_id = ?", (gid, uid)).fetchone() is not None


def group_members(gid):
    return cursor.execute("""
        SELECT u.id, u.username, u.fullname, u.role FROM chat_group_members m
        JOIN users u ON u.id = m.user_id WHERE m.group_id = ? AND u.is_deleted = 0
        ORDER BY u.fullname COLLATE NOCASE
    """, (gid,)).fetchall()


def delete_chat_group(gid):
    cursor.execute("DELETE FROM chat_group_members WHERE group_id = ?", (gid,))
    cursor.execute("DELETE FROM chat_messages WHERE conv = ?", (f"group:{gid}",))
    cursor.execute("DELETE FROM chat_reads WHERE conv = ?", (f"group:{gid}",))
    cursor.execute("DELETE FROM chat_groups WHERE id = ?", (gid,))


def leave_chat_group(gid, uid):
    cursor.execute("DELETE FROM chat_group_members WHERE group_id = ? AND user_id = ?", (gid, uid))
    left = cursor.execute("SELECT user_id FROM chat_group_members WHERE group_id = ? ORDER BY user_id LIMIT 1", (gid,)).fetchone()
    if not left:
        delete_chat_group(gid)                      # không còn ai → xóa nhóm
    else:
        owner = cursor.execute("SELECT created_by FROM chat_groups WHERE id = ?", (gid,)).fetchone()
        if owner and owner[0] == uid:               # chủ nhóm rời → chuyển quyền cho người khác
            cursor.execute("UPDATE chat_groups SET created_by = ? WHERE id = ?", (left[0], gid))


def format_room_id(room_id):
    d = "".join(ch for ch in str(room_id) if ch.isdigit())
    return " ".join(d[i:i + 3] for i in range(0, len(d), 3))


def create_meeting(title, host_id, start_at):
    while True:
        room_id = str(secrets.randbelow(900_000_000) + 100_000_000)          # 9 chữ số, giống Zoom
        if not cursor.execute("SELECT 1 FROM meetings WHERE room_id = ?", (room_id,)).fetchone():
            break
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"                           # bỏ các ký tự dễ nhầm (0/O, 1/I)
    password = "".join(secrets.choice(alphabet) for _ in range(6))
    video_room = "ShipControl" + secrets.token_hex(10)                      # tên phòng video bí mật, không đoán được
    cursor.execute("""INSERT INTO meetings (room_id, password, title, host_id, video_room, start_at, created_at, is_active)
                      VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
                   (room_id, password, title, host_id, video_room, start_at, datetime.now().isoformat(timespec="seconds")))
    return room_id, password


def find_meeting(room_input, password_input):
    rid = "".join(ch for ch in str(room_input or "") if ch.isdigit())
    pw = str(password_input or "").strip().upper()
    if not rid or not pw:
        return None
    row = cursor.execute("SELECT id, password FROM meetings WHERE room_id = ? AND is_active = 1", (rid,)).fetchone()
    if row and hmac.compare_digest(row[1].upper(), pw):
        return row
    return None


def meeting_url(video_room, display_name):
    from urllib.parse import quote
    return f"{MEETING_SERVER}/{video_room}#userInfo.displayName=%22{quote(str(display_name))}%22"


def meeting_code_card(room_id, password, compact=False):
    lab_id, lab_pw = html.escape(tr("🔢 ID phòng")), html.escape(tr("🔑 Mật khẩu"))
    return (f"<div class='sc-meet-card{' sc-compact' if compact else ''}'>"
            f"<div><span>{lab_id}</span><b>{html.escape(format_room_id(room_id))}</b></div>"
            f"<div><span>{lab_pw}</span><b>{html.escape(password)}</b></div></div>")


# CẤU HÌNH GIAO DIỆN
st.set_page_config(
    page_title="ShipControl - Quản Lý Công Việc Tàu",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="auto"
)

# KHỞI TẠO COOKIE MANAGER
cookie_manager = stx.CookieManager(key="shipcontrol_cookie_mgr")
SESSION_COOKIE = "shipcontrol_session"
SESSION_DAYS = 30

# 2. KẾT NỐI CƠ SỞ DỮ LIỆU SQLITE & AUTO-MIGRATION
# 🗄️ KẾT NỐI DATABASE
#   - isolation_level=None (tự lưu từng lệnh): không còn "giao dịch treo" khi một lượt chạy bị ngắt giữa chừng
#     (đây là nguyên nhân lỗi "database is locked" khi nhiều người / nhiều tab dùng cùng lúc)
#   - timeout 30s + WAL: nhiều người đọc/ghi cùng lúc thì chờ nhau thay vì báo lỗi
conn = sqlite3.connect("ship_control.db", check_same_thread=False, timeout=30, isolation_level=None)
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA synchronous=NORMAL")
except sqlite3.OperationalError:
    pass

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        fullname TEXT,
        role TEXT DEFAULT 'Pending',
        is_deleted INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_cost_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        description TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

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
        progress INTEGER DEFAULT 0,
        remark TEXT,
        image_path TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

# AUTO-MIGRATION
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Pending'")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_deleted INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

tasks_schema_updates = {
    "task_cost_code": "TEXT", "block": "TEXT", "description": "TEXT",
    "initial_by": "TEXT", "initial_date": "TEXT", "area": "TEXT",
    "deck": "TEXT", "frame": "TEXT", "in_charge_by": "TEXT",
    "plan_start_date": "TEXT", "plan_finish_date": "TEXT",
    "progress": "INTEGER DEFAULT 0", "remark": "TEXT",
    "image_path": "TEXT", "is_deleted": "INTEGER DEFAULT 0"
}
cursor.execute("PRAGMA table_info(tasks)")
existing_cols = [col[1] for col in cursor.fetchall()]
for col_name, col_type in tasks_schema_updates.items():
    if col_name not in existing_cols:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass


# 🏭 CỘT WORKSHOP CHO NGƯỜI DÙNG (mỗi tài khoản thuộc 1 workshop / phòng ban)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN workshop TEXT")
except sqlite3.OperationalError:
    pass

# 👥 TEAM & GIAO VIỆC
#   users.leader_id          : Worker thuộc team của Team Leader / Foreman nào
#   tasks.assigned_leader_id : WOS Manager giao việc cho Team Leader / Foreman nào
#   tasks.assigned_worker_id : Team Leader / Foreman giao việc cho Worker nào
for _sql in ["ALTER TABLE users ADD COLUMN leader_id INTEGER",
             "ALTER TABLE users ADD COLUMN team_name TEXT",
             "ALTER TABLE tasks ADD COLUMN assigned_leader_id INTEGER",
             "ALTER TABLE tasks ADD COLUMN assigned_worker_id INTEGER"]:
    try:
        cursor.execute(_sql)
    except sqlite3.OperationalError:
        pass

LEADER_ROLES = ["Team Leader", "Foreman"]

def remove_worker_from_team(worker_id, leader_id):
    """Đưa Worker ra khỏi team và bỏ giao các việc của team đó cho Worker này."""
    cursor.execute("UPDATE users SET leader_id = NULL WHERE id = ? AND leader_id = ?", (worker_id, leader_id))
    cursor.execute("UPDATE tasks SET assigned_worker_id = NULL WHERE assigned_worker_id = ? AND assigned_leader_id = ?",
                   (worker_id, leader_id))
    conn.commit()

# 🏭 DANH SÁCH WORKSHOP / PHÒNG BAN MẶC ĐỊNH (theo bảng Excel)
DEFAULT_WORKSHOPS = [
    ("WOS_01", "Fabrication WS"),
    ("WOS_02", "Hull WS 02"),
    ("WOS_03", "Hull WS 03"),
    ("WOS_04", "Outfitting WS"),
    ("WOS_05", "Piping WS"),
    ("WOS_06", "Painting WS"),
    ("DEP_01", "Technical Dept"),
    ("DEP_02", "QA QC Department"),
    ("DEP_03", "Safety Department"),
    ("DEP_04", "Planing Department"),
    ("DEP_05", "Project Department"),
    ("DEP_06", "Finance Department"),
    ("DEP_07", "HR Department"),
    ("DEP_08", "Security Department"),
]
# Danh sách trên chỉ được tạo sẵn MỘT LẦN khi database còn mới.
# Sau đó thêm / xóa WS Cost Code ngay trong trang ➕ Thêm Công Việc.
cursor.execute("CREATE TABLE IF NOT EXISTS app_flags (name TEXT PRIMARY KEY)")
if not cursor.execute("SELECT 1 FROM app_flags WHERE name = 'workshops_seeded'").fetchone():
    for ws_code, ws_name in DEFAULT_WORKSHOPS:
        cursor.execute("INSERT OR IGNORE INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, '', 0)",
                       (ws_code, ws_name))
    cursor.execute("INSERT INTO app_flags (name) VALUES ('workshops_seeded')")

# 🧱 DANH SÁCH BLOCK
cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        is_deleted INTEGER DEFAULT 0
    )
''')
if not cursor.execute("SELECT 1 FROM app_flags WHERE name = 'blocks_seeded'").fetchone():
    # Lấy các Block đã dùng trong công việc cũ làm danh sách ban đầu
    for (b,) in cursor.execute("SELECT DISTINCT TRIM(block) FROM tasks WHERE block IS NOT NULL AND TRIM(block) != ''").fetchall():
        cursor.execute("INSERT OR IGNORE INTO blocks (name, is_deleted) VALUES (?, 0)", (b,))
    cursor.execute("INSERT INTO app_flags (name) VALUES ('blocks_seeded')")

# 💬 BẢNG TIN NHẮN
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conv TEXT NOT NULL,
        sender_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
''')
cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_conv ON chat_messages (conv, id)")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_reads (
        user_id INTEGER NOT NULL,
        conv TEXT NOT NULL,
        last_read_id INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (user_id, conv)
    )
''')

# 💬 NHÓM CHAT + 🎥 CUỘC HỌP
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_group_members (
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (group_id, user_id)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        title TEXT NOT NULL,
        host_id INTEGER NOT NULL,
        video_room TEXT NOT NULL,
        start_at TEXT,
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS meeting_invites (
        meeting_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (meeting_id, user_id)
    )
''')

# 🔐 BẢNG PHIÊN ĐĂNG NHẬP (cookie chỉ chứa token ngẫu nhiên, không chứa username)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        expires_at TEXT
    )
''')


# ==========================================
# 🔑 HÀM BẢO MẬT MẬT KHẨU
# ==========================================
PBKDF2_ITERATIONS = 200_000

def hash_password(password):
    """Băm mật khẩu bằng PBKDF2-SHA256 có salt ngẫu nhiên."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"

def verify_password(password, stored):
    """Kiểm tra mật khẩu. Hỗ trợ cả hash SHA-256 kiểu cũ để người dùng cũ vẫn đăng nhập được."""
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, iters, salt_hex, digest_hex = stored.split("$")
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iters))
            return hmac.compare_digest(digest.hex(), digest_hex)
        except Exception:
            return False
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)

def is_legacy_hash(stored):
    return bool(stored) and not stored.startswith("pbkdf2$")

LEGACY_DEFAULT_ADMIN_HASH = hashlib.sha256("admin123".encode()).hexdigest()


# ==========================================
# 🎫 HÀM QUẢN LÝ PHIÊN ĐĂNG NHẬP
# ==========================================
def create_session(user_id):
    """Tạo phiên đăng nhập mới. Mỗi tài khoản chỉ được đăng nhập ở MỘT nơi:
    đăng nhập ở máy mới thì phiên ở máy cũ bị xóa (máy cũ sẽ tự đăng xuất)."""
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(days=SESSION_DAYS)).isoformat()
    cursor.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires))
    conn.commit()
    return token

def session_is_valid(token):
    return cursor.execute("SELECT 1 FROM sessions WHERE token = ? AND expires_at > ?",
                          (token, datetime.now().isoformat())).fetchone() is not None

def get_user_by_session(token):
    row = cursor.execute("""
        SELECT u.id, u.username, u.fullname, u.role, u.workshop
        FROM sessions s JOIN users u ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > ? AND u.is_deleted = 0
    """, (token, datetime.now().isoformat())).fetchone()
    return row

def delete_session(token):
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()

def delete_user_sessions(user_id):
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()

# Dọn các phiên đã hết hạn (việc dọn dẹp, lỡ database đang bận thì bỏ qua, lần sau dọn)
try:
    cursor.execute("DELETE FROM sessions WHERE expires_at <= ?", (datetime.now().isoformat(),))
except sqlite3.OperationalError:
    pass


# TẠO TÀI KHOẢN WOS MANAGER MẶC ĐỊNH (mật khẩu lấy từ Secrets, KHÔNG hardcode)
admin_exists = cursor.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
if not admin_exists:
    initial_admin_pw = get_secret("ADMIN_PASSWORD")
    if not initial_admin_pw:
        initial_admin_pw = secrets.token_urlsafe(12)
        print("=" * 60)
        print(f"[ShipControl] Mật khẩu admin tạm thời: {initial_admin_pw}")
        print("Hãy đăng nhập và đổi mật khẩu ngay, hoặc đặt ADMIN_PASSWORD trong Secrets.")
        print("=" * 60)
    cursor.execute("INSERT INTO users (username, password, fullname, role, is_deleted) VALUES (?, ?, ?, ?, 0)",
                   ('admin', hash_password(initial_admin_pw), 'System Admin', 'Admin'))

# Tài khoản 'admin' luôn là Admin hệ thống (chỉ cấp quyền WOS Manager + workshop)
if cursor.execute("SELECT 1 FROM users WHERE username = 'admin' AND (role IS NULL OR role != 'Admin')").fetchone():
    cursor.execute("UPDATE users SET role = 'Admin' WHERE username = 'admin'")

# 🆘 KHÔI PHỤC TÀI KHOẢN ADMIN: đặt RESET_ADMIN_PASSWORD trong Secrets để đặt lại mật khẩu admin.
# Sau khi đăng nhập được, hãy XÓA dòng RESET_ADMIN_PASSWORD khỏi Secrets.
reset_admin_pw = get_secret("RESET_ADMIN_PASSWORD")

@st.cache_resource(show_spinner=False)
def _apply_admin_reset(pw):
    """Chỉ đặt lại mật khẩu admin MỘT LẦN mỗi khi app khởi động (không phải mỗi lần bấm nút)."""
    c = sqlite3.connect("ship_control.db", timeout=30, isolation_level=None)
    c.execute("UPDATE users SET password = ?, role = 'Admin', is_deleted = 0 WHERE username = 'admin'",
              (hash_password(str(pw)),))
    c.close()
    return True

if reset_admin_pw:
    try:
        _apply_admin_reset(str(reset_admin_pw))
    except sqlite3.OperationalError:
        pass

conn.commit()


# 📧 HÀM GỬI EMAIL THÔNG BÁO CÓ NGƯỜI ĐĂNG KÝ MỚI
# Email chỉ thông báo. Việc cấp Role phải làm trong app bằng tài khoản WOS Manager,
# nên không ai có thể tự cấp quyền cho mình bằng cách sửa đường link.
def send_new_user_email(target_username, target_fullname):
    sender_email = get_secret("SMTP_EMAIL")
    sender_password = get_secret("SMTP_APP_PASSWORD")
    receiver_email = get_secret("ADMIN_EMAIL", sender_email)
    if not sender_email or not sender_password or not receiver_email:
        print("[ShipControl] Chưa cấu hình SMTP trong Secrets - bỏ qua gửi email.")
        return False

    safe_user = html.escape(target_username)
    safe_name = html.escape(target_fullname)
    subject = f"🔔 [ShipControl] Tài khoản mới chờ duyệt: {target_username}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <h2 style="color: #0284c7;">🚢 CÓ TÀI KHOẢN ĐĂNG KÝ MỚI</h2>
        <p>Có người dùng vừa đăng ký trên hệ thống <b>ShipControl</b>:</p>
        <hr>
        <p><b>Họ và Tên:</b> {safe_name}</p>
        <p><b>Tên đăng nhập (Username):</b> {safe_user}</p>
        <hr>
        <p>Đăng nhập bằng tài khoản <b>Admin</b> hoặc <b>WOS Manager</b>, vào mục <b>👥 Quản Lý Phân Quyền</b> để cấp Role.</p>
        <a href="{APP_URL}" style="display: inline-block; background-color: #16a34a; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold;">👉 Mở ShipControl</a>
    </div>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Lỗi gửi email:", e)
        return False

# --- KHỞI TẠO STATE THEME, AUTH & SUB-TABS ---
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if "auth_tab" not in st.session_state:
    st.session_state["auth_tab"] = "login"

if "current_menu" not in st.session_state:
    st.session_state["current_menu"] = "🧰 Bảng Công Việc"

if "edit_sub_tab" not in st.session_state:
    st.session_state["edit_sub_tab"] = "task"

if "trash_sub_tab" not in st.session_state:
    st.session_state["trash_sub_tab"] = "task"

# --- ⚙️ NÚT CÀI ĐẶT (Chế độ Tối + Ngôn ngữ) ---
# Chỗ đặt nút được giữ sẵn ở đầu thanh bên; nút thật được vẽ sau khi đọc cookie (để nhớ ngôn ngữ đã chọn).
st.sidebar.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
_settings_slot = st.sidebar.container()
dark_mode_on = st.session_state.get("dark_toggle", st.session_state["theme_mode"] == "Dark")
st.session_state["theme_mode"] = "Dark" if dark_mode_on else "Light"

ui_theme = st.session_state.get("ui_theme", "modern")
if ui_theme not in THEME_OPTIONS:
    ui_theme = "modern"
# Chủ đề Tương lai luôn dùng nền tối
is_dark = st.session_state["theme_mode"] == "Dark" or ui_theme == "futuristic"

main_bg = "#0f172a" if is_dark else "#f8f9fa"
text_color = "#ffffff" if is_dark else "#000000"
input_bg = "#1e293b" if is_dark else "#ffffff"
input_text = "#ffffff" if is_dark else "#000000"
border_color = "#334155" if is_dark else "#cbd5e1"
sec_bg = "#1e293b" if is_dark else "#ffffff"
sec_border = "#475569" if is_dark else "#cbd5e1"
sec_text = "#f1f5f9" if is_dark else "#0f172a"
danger_bg = "#1e293b" if is_dark else "#ffffff"

# ✨ VỆT SÁNG NGẪU NHIÊN: mỗi nút có nhịp riêng (2,4–4,4 giây) và bắt đầu lệch nhau,
#    nên các nút không bao giờ sáng cùng lúc. Giá trị ngẫu nhiên được giữ cố định trong 1 phiên
#    để vệt sáng không bị "giật" mỗi khi bấm nút.
import random as _random
if "shine_seed" not in st.session_state:
    st.session_state["shine_seed"] = _random.randint(1, 10**9)
_rng = _random.Random(st.session_state["shine_seed"])
_shine_rules = []
_CONTAINER = 'div[data-testid="stElementContainer"]'
_BTN_AFTER = [" div.stButton > button::after", " div.stDownloadButton > button::after",
              ' div[data-testid="stFormSubmitButton"] > button::after']
for _k in range(5):   # nhịp lặp: 5 giá trị khác nhau
    _sel = ", ".join(f"{_CONTAINER}:nth-child(5n+{_k}){b}" for b in _BTN_AFTER)
    _shine_rules.append(f"{_sel} {{ animation-duration: {_rng.uniform(2.4, 4.4):.2f}s; }}")
for _k in range(7):   # thời điểm bắt đầu: 7 giá trị khác nhau (5 x 7 = 35 tổ hợp)
    _sel = ", ".join(f"{_CONTAINER}:nth-child(7n+{_k}){b}" for b in _BTN_AFTER)
    _shine_rules.append(f"{_sel} {{ animation-delay: -{_rng.uniform(0, 4.4):.2f}s; }}")
shine_css = "\n    ".join(_shine_rules)

# 🚢 ẢNH NỀN TÀU: mỗi trang một ảnh (ảnh miễn phí từ Unsplash, giấy phép Unsplash License)
def _ship_photo(photo_id):
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1600&q=65"

SHIP_BACKGROUNDS = {
    "login":                   _ship_photo("photo-1605745341075-1b7460b99df8"),
    "🧰 Bảng Công Việc":       _ship_photo("photo-1605745341112-85968b19335b"),
    "➕ Thêm Công Việc":       _ship_photo("photo-1634638022845-1ab614a94128"),
    "📋 Giao Việc":            _ship_photo("photo-1585713181935-d5f622cc2415"),
    "👥 Team Của Tôi":         _ship_photo("photo-1604506522146-316c8bedd874"),
    "✏️ Chỉnh Sửa/Xóa":        _ship_photo("photo-1670121180530-cfcba4438038"),
    "👥 Quản Lý Phân Quyền":   _ship_photo("photo-1691591765923-3bd6f12f4209"),
    "🗑️ Thùng Rác":            _ship_photo("photo-1617952739760-1dcae19a1d93"),
    "📊 Báo Cáo & Khai Báo":   _ship_photo("photo-1724597500306-a4cbb7d1324e"),
    "🔑 Đổi Mật Khẩu":         _ship_photo("photo-1594110336951-5bc8c12d6b27"),
}
_bg_key = st.session_state.get("current_menu") if st.session_state.get("logged_in") else "login"
page_bg_url = SHIP_BACKGROUNDS.get(_bg_key, SHIP_BACKGROUNDS["🧰 Bảng Công Việc"])

# 🎨 GIAO DIỆN HIỆN ĐẠI: bảng màu theo chế độ Sáng / Tối
_danger_keys = ["btn_del_block", "btn_del_cc", "btn_role_del_ws", "chat_del_msg_btn", "chat_clear_btn", "btn_delete_team", "btn_leave_team", "btn_perm_del_task",
                "btn_perm_del_user", "btn_remove_team_member", "btn_soft_delete_task", "btn_soft_delete_user"]
_modern_tokens = {
    "__APP_BG__": (
        # Lớp phủ màu để chữ vẫn dễ đọc, ảnh tàu nhìn xuyên qua phía dưới
        ("linear-gradient(180deg, rgba(8,15,30,0.58) 0%, rgba(8,15,30,0.78) 45%, rgba(8,15,30,0.88) 100%), "
         if is_dark else
         "linear-gradient(180deg, rgba(244,247,251,0.38) 0%, rgba(244,247,251,0.70) 40%, rgba(244,247,251,0.86) 100%), ")
        + f"url('{page_bg_url}') center / cover no-repeat"
    ),
    "__BASE_BG__": "#0b1220" if is_dark else "#f4f7fb",
    "__BG_ANIM__": "bgFade_" + str(abs(hash(_bg_key)) % 100000),
    "__PRELOAD__": " ".join(f"url('{u}')" for u in SHIP_BACKGROUNDS.values()),
    "__SURFACE__": "#111a2e" if is_dark else "#ffffff",
    "__SURFACE_BORDER__": "#22304d" if is_dark else "#e3e8f0",
    "__INPUT_BG__": "#0a1222" if is_dark else "#fbfcfe",
    "__INPUT_BORDER__": "#33466b" if is_dark else "#d5dce8",
    "__INPUT_BORDER_HOVER__": "#4a6190" if is_dark else "#aab6c8",
    "__INPUT_TEXT__": "#f1f5f9" if is_dark else "#0f172a",
    "__PLACEHOLDER__": "#7c8aa5" if is_dark else "#94a3b8",
    "__ICON__": "#cbd5e1" if is_dark else "#475569",
    "__SCHEME__": "dark" if is_dark else "light",
    "__BUBBLE_THEIRS__": "#1e293b" if is_dark else "#eef2f7",
    "__SELECTED_BG__": "rgba(14,165,233,0.18)" if is_dark else "#e0f2fe",
    "__TOGGLE_OFF__": "#475569" if is_dark else "#94a3b8",
    "__TOGGLE_OFF_BORDER__": "#64748b" if is_dark else "#64748b",
    "__HOVER_TINT__": "rgba(255,255,255,0.04)" if is_dark else "#f8fafc",
    "__DANGER_SOFT__": "rgba(239,68,68,0.10)" if is_dark else "#fef2f2",
    "__INFO_BG__": "rgba(14,165,233,0.12)" if is_dark else "#f0f9ff",
    "__INFO_TX__": "#7dd3fc" if is_dark else "#075985",
    "__OK_BG__": "rgba(34,197,94,0.12)" if is_dark else "#f0fdf4",
    "__OK_TX__": "#86efac" if is_dark else "#166534",
    "__WARN_BG__": "rgba(234,179,8,0.12)" if is_dark else "#fefce8",
    "__WARN_TX__": "#fde047" if is_dark else "#854d0e",
    "__ERR_BG__": "rgba(239,68,68,0.12)" if is_dark else "#fef2f2",
    "__ERR_TX__": "#fca5a5" if is_dark else "#991b1b",
    "__DANGER_SEL_HOVER__": ",\n".join(f"div.st-key-{k} div.stButton > button[kind]:hover:not(:disabled)" for k in _danger_keys),
    "__DANGER_SEL__": ",\n".join(f"div.st-key-{k} div.stButton > button[kind]" for k in _danger_keys),
}
modern_css = MODERN_CSS_TEMPLATE
for _tok, _val in _modern_tokens.items():
    modern_css = modern_css.replace(_tok, _val)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    .stApp, .main {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: #0284c7 !important;
        width: 330px !important;
    }}
    
    .sidebar-header {{
        font-size: 2rem;
        font-weight: 800;
        color: #facc15;
        text-align: center;
        padding: 10px 0;
        margin-bottom: 10px;
    }}

    .made-by-minh {{
        background-color: #facc15;
        color: #0369a1;
        font-size: 1.5rem;
        font-weight: 900;
        font-style: italic;
        text-align: center;
        padding: 10px;
        border-radius: 12px;
        margin-top: 15px;
    }}

    .user-card {{
        background-color: rgba(255, 255, 255, 0.15);
        padding: 12px;
        border-radius: 12px;
        margin-top: 15px;
        text-align: center;
        color: white;
    }}

    /* ================= NÚT BẤM =================
       Nút to, dễ bấm trên điện thoại (kể cả khi đeo găng tay),
       có "đế" phía dưới giống nút bấm vật lý: nhấn vào thì lún xuống. */
    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {{
        width: 100% !important;
        min-height: 52px !important;
        padding: 10px 18px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        background-image: none !important;
        transition: transform 0.08s ease, box-shadow 0.08s ease, background-color 0.15s ease, border-color 0.15s ease !important;
    }}
    div.stButton > button *,
    div.stDownloadButton > button *,
    div[data-testid="stFormSubmitButton"] > button * {{
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em !important;
        opacity: 1 !important;
    }}

    /* Nút chính (xanh lá): Lưu, Thêm, Đăng nhập... */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"],
    div.stButton > button[data-testid="stBaseButton-primary"],
    div[data-testid="stFormSubmitButton"] > button,
    div.stDownloadButton > button {{
        background-color: #16a34a !important;
        border: 1px solid #15803d !important;
        box-shadow: 0 4px 0 #166534, 0 6px 14px rgba(22, 101, 52, 0.25) !important;
    }}
    div.stButton > button[kind="primary"] *,
    div.stButton > button[data-testid="baseButton-primary"] *,
    div.stButton > button[data-testid="stBaseButton-primary"] *,
    div[data-testid="stFormSubmitButton"] > button *,
    div.stDownloadButton > button * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    div.stButton > button[kind="primary"]:hover:not(:disabled),
    div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled),
    div.stDownloadButton > button:hover:not(:disabled) {{
        background-color: #15803d !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 0 #166534, 0 8px 18px rgba(22, 101, 52, 0.3) !important;
    }}

    /* Nút phụ: nền sáng, viền rõ */
    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="baseButton-secondary"],
    div.stButton > button[data-testid="stBaseButton-secondary"] {{
        background-color: {sec_bg} !important;
        border: 1px solid {sec_border} !important;
        box-shadow: 0 4px 0 {sec_border} !important;
    }}
    div.stButton > button[kind="secondary"] *,
    div.stButton > button[data-testid="baseButton-secondary"] *,
    div.stButton > button[data-testid="stBaseButton-secondary"] * {{
        color: {sec_text} !important;
        -webkit-text-fill-color: {sec_text} !important;
    }}
    div.stButton > button[kind="secondary"]:hover:not(:disabled) {{
        border-color: #0284c7 !important;
        box-shadow: 0 4px 0 #0284c7 !important;
        transform: translateY(-1px) !important;
    }}

    /* Nút xóa / rời team: đỏ, để không bấm nhầm */
    div.st-key-btn_del_block div.stButton > button[kind],
    div.st-key-btn_del_cc div.stButton > button[kind],
    div.st-key-btn_delete_team div.stButton > button[kind],
    div.st-key-btn_leave_team div.stButton > button[kind],
    div.st-key-btn_perm_del_task div.stButton > button[kind],
    div.st-key-btn_perm_del_user div.stButton > button[kind],
    div.st-key-btn_remove_team_member div.stButton > button[kind],
    div.st-key-btn_soft_delete_task div.stButton > button[kind],
    div.st-key-btn_soft_delete_user div.stButton > button[kind] {{
        background-color: {danger_bg} !important;
        border: 1px solid #dc2626 !important;
        box-shadow: 0 4px 0 #b91c1c !important;
    }}
    div.st-key-btn_del_block div.stButton > button[kind] *,
    div.st-key-btn_del_cc div.stButton > button[kind] *,
    div.st-key-btn_delete_team div.stButton > button[kind] *,
    div.st-key-btn_leave_team div.stButton > button[kind] *,
    div.st-key-btn_perm_del_task div.stButton > button[kind] *,
    div.st-key-btn_perm_del_user div.stButton > button[kind] *,
    div.st-key-btn_remove_team_member div.stButton > button[kind] *,
    div.st-key-btn_soft_delete_task div.stButton > button[kind] *,
    div.st-key-btn_soft_delete_user div.stButton > button[kind] * {{
        color: #dc2626 !important;
        -webkit-text-fill-color: #dc2626 !important;
    }}
    div.st-key-btn_del_block div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_del_cc div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_delete_team div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_leave_team div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_perm_del_task div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_perm_del_user div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_remove_team_member div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_soft_delete_task div.stButton > button[kind]:hover:not(:disabled),
    div.st-key-btn_soft_delete_user div.stButton > button[kind]:hover:not(:disabled) {{
        background-color: #dc2626 !important;
        box-shadow: 0 4px 0 #991b1b !important;
    }}
    div.st-key-btn_del_block div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_del_cc div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_delete_team div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_leave_team div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_perm_del_task div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_perm_del_user div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_remove_team_member div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_soft_delete_task div.stButton > button[kind]:hover:not(:disabled) *,
    div.st-key-btn_soft_delete_user div.stButton > button[kind]:hover:not(:disabled) * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* Nhấn xuống: nút lún vào đế */
    div.stButton > button:active:not(:disabled),
    div.stDownloadButton > button:active:not(:disabled),
    div[data-testid="stFormSubmitButton"] > button:active:not(:disabled) {{
        transform: translateY(3px) !important;
        box-shadow: 0 1px 0 rgba(0, 0, 0, 0.25) !important;
    }}

    /* Nút bị khóa (chưa tick xác nhận...) */
    div.stButton > button:disabled {{
        opacity: 0.45 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }}

    /* Viền khi dùng bàn phím (Tab) */
    div.stButton > button:focus-visible,
    div.stDownloadButton > button:focus-visible,
    div[data-testid="stFormSubmitButton"] > button:focus-visible {{
        outline: 3px solid #facc15 !important;
        outline-offset: 2px !important;
    }}

    /* ================= MENU BÊN TRÁI =================
       Mục chưa chọn: trong suốt trên nền xanh. Mục đang chọn: vàng, giống nhãn "Made by Minh". */
    section[data-testid="stSidebar"] div.stButton > button {{
        min-height: 48px !important;
        justify-content: flex-start !important;
        text-align: left !important;
        margin-bottom: 4px !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button > div,
    section[data-testid="stSidebar"] div.stButton > button p {{
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"],
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-secondary"],
    section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-secondary"] {{
        background-color: rgba(255, 255, 255, 0.10) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        box-shadow: none !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] *,
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-secondary"] *,
    section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-secondary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover:not(:disabled) {{
        background-color: rgba(255, 255, 255, 0.22) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: none !important;
        transform: translateX(3px) !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"],
    section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] {{
        background-color: #facc15 !important;
        border: 1px solid #eab308 !important;
        box-shadow: 0 4px 0 #a16207 !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] *,
    section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"] *,
    section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] * {{
        color: #0c4a6e !important;
        -webkit-text-fill-color: #0c4a6e !important;
        font-size: 1.05rem !important;
        font-weight: 900 !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover:not(:disabled) {{
        background-color: #fde047 !important;
        transform: none !important;
        box-shadow: 0 4px 0 #a16207 !important;
    }}
    /* Nút Đăng Xuất: viền trắng, căn giữa */
    section[data-testid="stSidebar"] div.st-key-btn_logout_bottom div.stButton > button[kind] {{
        justify-content: center !important;
        background-color: transparent !important;
        border: 2px solid rgba(255, 255, 255, 0.7) !important;
        margin-top: 12px !important;
    }}
    section[data-testid="stSidebar"] div.st-key-btn_logout_bottom div.stButton > button[kind] > div,
    section[data-testid="stSidebar"] div.st-key-btn_logout_bottom div.stButton > button[kind] p {{
        justify-content: center !important;
        text-align: center !important;
    }}

    /* ================= HIỆU ỨNG VỆT SÁNG TỰ ĐỘNG =================
       Vệt sáng tự lướt qua nút, mỗi nút một nhịp ngẫu nhiên (trung bình ~3 giây). */
    div.stButton > button,
    div.stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {{
        position: relative !important;
        overflow: hidden !important;
        isolation: isolate;
    }}
    div.stButton > button::after,
    div.stDownloadButton > button::after,
    div[data-testid="stFormSubmitButton"] > button::after {{
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 60%;
        background: linear-gradient(100deg,
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.55) 50%,
                    rgba(255, 255, 255, 0) 100%);
        transform: translateX(-130%) skewX(-20deg);
        will-change: transform;
        pointer-events: none;
        z-index: 1;
        animation: btnShine 3s cubic-bezier(0.45, 0, 0.35, 1) infinite;
    }}
    /* Lướt qua trong ~0,8 giây đầu, sau đó nghỉ đến hết 3 giây rồi lặp lại */
    @keyframes btnShine {{
        0%   {{ transform: translateX(-130%) skewX(-20deg); }}
        27%  {{ transform: translateX(260%) skewX(-20deg); }}
        100% {{ transform: translateX(260%) skewX(-20deg); }}
    }}
    /* Nhịp và thời điểm ngẫu nhiên cho từng nút */
    {shine_css}

    /* Nút đang bị khóa thì không có vệt sáng */
    div.stButton > button:disabled::after {{
        display: none;
    }}
    /* Nút trên nền trắng: vệt sáng màu xanh nhạt để nhìn thấy được */
    div.stButton > button[kind="secondary"]::after {{
        background: linear-gradient(100deg,
                    rgba(2, 132, 199, 0) 0%,
                    rgba(2, 132, 199, 0.22) 50%,
                    rgba(2, 132, 199, 0) 100%);
    }}
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]::after {{
        background: linear-gradient(100deg,
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.45) 50%,
                    rgba(255, 255, 255, 0) 100%);
    }}

    /* Mục menu vừa được chọn: nền vàng lướt vào từ trái */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
        animation: menuSlideIn 0.2s ease-out;
    }}
    @keyframes menuSlideIn {{
        from {{ background-position: 100% 0; transform: translateX(-6px); }}
        to   {{ background-position: 0 0;    transform: translateX(0); }}
    }}

    /* ================= CHUYỂN TRANG KIỂU LƯỚT =================
       Chọn mục bên dưới trong menu: trang mới lướt vào từ bên phải.
       Chọn mục bên trên: trang mới lướt vào từ bên trái. */
    section[data-testid="stMain"], .stMain, .main {{
        overflow-x: hidden !important;
    }}
    div[class*="st-key-pgR_"] {{
        animation: pageFromRight 0.26s cubic-bezier(0.2, 0.8, 0.2, 1) both;
        will-change: transform, opacity;
    }}
    div[class*="st-key-pgL_"] {{
        animation: pageFromLeft 0.26s cubic-bezier(0.2, 0.8, 0.2, 1) both;
        will-change: transform, opacity;
    }}
    @keyframes pageFromRight {{
        from {{ opacity: 0; transform: translate3d(32px, 0, 0); }}
        to   {{ opacity: 1; transform: translateX(0); }}
    }}
    @keyframes pageFromLeft {{
        from {{ opacity: 0; transform: translate3d(-32px, 0, 0); }}
        to   {{ opacity: 1; transform: translateX(0); }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        div.stButton > button::after,
        div.stDownloadButton > button::after,
        div[data-testid="stFormSubmitButton"] > button::after {{
            display: none;
        }}
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
        div[class*="st-key-pgR_"], div[class*="st-key-pgL_"] {{
            animation: none !important;
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        div.stButton > button, div.stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button {{
            transition: none !important;
            transform: none !important;
        }}
    }}

    .big-table-title {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: {text_color} !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }}

    div[data-testid="stDataFrame"] th, 
    div[data-testid="stTable"] th {{
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        padding: 12px 8px !important;
    }}

    div[data-testid="stDataFrame"] td, 
    div[data-testid="stTable"] td,
    div[data-testid="stDataFrame"] [role="gridcell"] {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 10px 8px !important;
    }}

    div[data-testid="stAlert"] {{
        background-color: #fef08a !important;
        border: 2px solid #eab308 !important;
        border-radius: 10px !important;
    }}
    
    div[data-testid="stAlert"] * {{
        color: #854d0e !important;
        -webkit-text-fill-color: #854d0e !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }}


    /* Chữ của nút chọn Role (radio), nhãn các ô nhập và số liệu báo cáo: luôn cùng màu chữ chính */
    .stRadio label, .stRadio label p, .stRadio div[role="radiogroup"] *,
    .stNumberInput label, .stNumberInput label p,
    .stCheckbox label, .stCheckbox label p,
    .stMain [data-testid="stWidgetLabel"], .stMain [data-testid="stWidgetLabel"] p,
    .main [data-testid="stWidgetLabel"], .main [data-testid="stWidgetLabel"] p,
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        opacity: 1 !important;
    }}
    .stRadio div[role="radiogroup"] p {{
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }}

    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label, .stSlider label {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    .main-title {{
        font-size: 2.3rem;
        color: {text_color} !important;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
        border-bottom: 3px solid #22c55e;
        margin-bottom: 25px;
    }}

    {modern_css}
    </style>
""", unsafe_allow_html=True)

_bg_css = BG_CSS_TEMPLATE
for _tok in ("__APP_BG__", "__BG_ANIM__"):
    _bg_css = _bg_css.replace(_tok, _modern_tokens[_tok])
st.markdown(f"<style>{_bg_css}</style>", unsafe_allow_html=True)

# 🎨 Lớp CSS của chủ đề đang chọn (Modern thì không cần thêm gì)
_theme_css = build_theme_css(ui_theme, is_dark, page_bg_url)
if _theme_css:
    st.markdown(f"<style>{_theme_css}</style>", unsafe_allow_html=True)

# --- TIÊU ĐỀ TRANG ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

# --- KHỞI TẠO KHỔI PHỤC ĐĂNG NHẬP CHUẨN ĐỒNG BỘ COOKIE ---
all_cookies = cookie_manager.get_all()

if all_cookies is None:
    st.stop()

saved_token = all_cookies.get(SESSION_COOKIE)

# Tab vừa bị đăng xuất vì tài khoản được mở ở nơi khác thì KHÔNG tự đăng nhập lại
# (nếu không, 2 tab sẽ đá nhau qua lại).
if not st.session_state["logged_in"] and saved_token and not st.session_state.get("_kicked"):
    user_db = get_user_by_session(saved_token)
    if user_db and user_db[3] and user_db[3] != 'Pending':
        # Chỉ 1 tab được dùng: tab mới mở nhận phiên MỚI, phiên cũ bị xóa → tab cũ tự đăng xuất
        new_token = create_session(user_db[0])
        st.session_state["_pending_session_cookie"] = new_token
        st.session_state["logged_in"] = True
        st.session_state["session_token"] = new_token
        st.session_state["user_info"] = {"id": user_db[0], "username": user_db[1], "fullname": user_db[2], "role": user_db[3], "workshop": user_db[4]}
        st.rerun()

# Nếu đang đăng nhập, kiểm tra lại mỗi lần tải trang: tài khoản bị khóa hoặc đổi Role sẽ có hiệu lực ngay
if st.session_state["logged_in"]:
    fresh = cursor.execute("SELECT fullname, role, workshop FROM users WHERE id = ? AND is_deleted = 0",
                           (st.session_state["user_info"]["id"],)).fetchone()
    if not fresh or not fresh[1] or fresh[1] == 'Pending':
        tok = st.session_state.get("session_token")
        if tok:
            delete_session(tok)
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
        st.rerun()
    st.session_state["user_info"]["fullname"] = fresh[0]
    st.session_state["user_info"]["role"] = fresh[1]
    st.session_state["user_info"]["workshop"] = fresh[2]

    # 🔒 Tài khoản đã được đăng nhập ở nơi khác → phiên này hết hiệu lực → đăng xuất
    def _kick_if_signed_in_elsewhere():
        tok = st.session_state.get("session_token")
        # Không có mã phiên (tab đăng nhập từ bản app cũ) cũng coi là hết hiệu lực → bắt đăng nhập lại
        if st.session_state.get("logged_in") and (not tok or not session_is_valid(tok)):
            st.session_state["logged_in"] = False
            st.session_state["user_info"] = None
            st.session_state["session_token"] = None
            st.session_state["_kicked"] = True
            st.rerun(scope="app")

    _kick_if_signed_in_elsewhere()

    # Kiểm tra lại mỗi 5 giây kể cả khi không bấm gì, để máy cũ tự đăng xuất ngay
    @st.fragment(run_every=5)
    def _session_watchdog():
        _kick_if_signed_in_elsewhere()

    _session_watchdog()

# 🌐 Nhớ ngôn ngữ đã chọn (lưu trong cookie của trình duyệt)
#    Cookie có thể đến chậm hơn lần chạy đầu, nên cứ khi nào cookie có mà chưa áp dụng thì áp dụng.
_lang_cookie = all_cookies.get(LANG_COOKIE)
if (_lang_cookie in LANG_OPTIONS and not st.session_state.get("_lang_restored")
        and not st.session_state.get("_lang_changed")):
    st.session_state["_lang_restored"] = True
    if _lang_cookie != ui_lang():
        st.session_state["ui_lang"] = _lang_cookie
        st.rerun()

def _on_lang_change():
    st.session_state["ui_lang"] = st.session_state["w_ui_lang"]
    st.session_state["_lang_changed"] = True

# 🎨 Nhớ chủ đề đã chọn (cookie), cùng cách với ngôn ngữ
THEME_COOKIE = "shipcontrol_theme"
_theme_cookie = all_cookies.get(THEME_COOKIE)
if (_theme_cookie in THEME_OPTIONS and not st.session_state.get("_theme_restored")
        and not st.session_state.get("_theme_changed")):
    st.session_state["_theme_restored"] = True
    if _theme_cookie != st.session_state.get("ui_theme", "modern"):
        st.session_state["ui_theme"] = _theme_cookie
        st.rerun()

def _on_theme_change():
    st.session_state["ui_theme"] = st.session_state["w_ui_theme"]
    st.session_state["_theme_changed"] = True

# 📱 Thiết bị đang dùng (Máy tính / Điện thoại) — nhớ bằng cookie, lần đầu thì tự đoán
_dev_cookie = all_cookies.get(DEVICE_COOKIE)
if "device_mode" not in st.session_state:
    st.session_state["device_mode"] = _dev_cookie if _dev_cookie in DEVICE_OPTIONS else _guess_device()
if (_dev_cookie in DEVICE_OPTIONS and not st.session_state.get("_device_restored")
        and not st.session_state.get("_device_changed")):
    st.session_state["_device_restored"] = True
    if _dev_cookie != st.session_state["device_mode"]:
        st.session_state["device_mode"] = _dev_cookie
        st.rerun()

def _on_device_change():
    st.session_state["device_mode"] = st.session_state["w_device_mode"]
    st.session_state["_device_changed"] = True

def _on_login_device_change():
    st.session_state["device_mode"] = st.session_state["device_mode_login"]
    st.session_state["_device_changed"] = True

# Các nút chọn dùng khóa riêng (w_...), còn giá trị thật lưu ở ui_theme / ui_lang / device_mode.
# Mỗi lần chạy gán lại giá trị cho nút chọn, để nút luôn hiển thị đúng (không bị lệch hay bị reset).
st.session_state.setdefault("ui_lang", "vi")
st.session_state.setdefault("ui_theme", "modern")
st.session_state["w_ui_lang"] = st.session_state["ui_lang"]
st.session_state["w_ui_theme"] = st.session_state["ui_theme"]
st.session_state["w_device_mode"] = st.session_state["device_mode"]

with _settings_slot:
    # Hàng nút trên cùng: [⚙️ Cài đặt]  [🌐 ▾ Ngôn ngữ]
    with st.container(horizontal=True, gap="small", vertical_alignment="center"):
        with st.popover("⚙️ Cài đặt", key="pop_settings"):
            # 🎨 Chủ đề: nút bấm xổ xuống (giống nút Ngôn ngữ)
            st.selectbox("🎨 Chủ đề", THEME_OPTIONS, key="w_ui_theme", on_change=_on_theme_change,
                         format_func=lambda t: THEME_LABELS[t])
            st.toggle("🌙 Chế độ Tối (Dark)", value=(st.session_state["theme_mode"] == "Dark"), key="dark_toggle",
                      disabled=(ui_theme == "futuristic"))
            if ui_theme == "futuristic":
                st.caption("Chủ đề Tương lai luôn dùng nền tối.")
            # 🌐 Ngôn ngữ: nút xanh có quả địa cầu + mũi tên, bấm để chọn
            st.selectbox("🌐 Ngôn ngữ", LANG_OPTIONS, key="w_ui_lang", on_change=_on_lang_change,
                         format_func=lambda c: LANG_LABELS[c])
            st.radio("📲 Thiết bị", DEVICE_OPTIONS, key="w_device_mode", horizontal=True, on_change=_on_device_change,
                     format_func=lambda d: DEVICE_LABELS[d])
            if st.session_state["device_mode"] == "mobile":
                st.caption("🎤 Bấm nút micro trong ô nhập chữ để nói thay vì gõ.")


# 🎤 Nút micro trong ô nhập chữ (chỉ ở chế độ Điện thoại)
render_voice_input(st.session_state["device_mode"] == "mobile")
if st.session_state.get("_device_changed") and _dev_cookie != st.session_state["device_mode"]:
    try:
        cookie_manager.set(DEVICE_COOKIE, st.session_state["device_mode"], max_age=365 * 24 * 3600, key="set_device_cookie")
    except Exception:
        pass
# 🍪 Lưu cookie đăng nhập (để lần sau mở lại vẫn đăng nhập). Ghi lại cho tới khi trình duyệt xác nhận đã lưu.
_pending_cookie = st.session_state.get("_pending_session_cookie")
if _pending_cookie:
    if not st.session_state.get("logged_in") or all_cookies.get(SESSION_COOKIE) == _pending_cookie:
        st.session_state.pop("_pending_session_cookie", None)
    else:
        try:
            cookie_manager.set(SESSION_COOKIE, _pending_cookie, max_age=SESSION_DAYS * 24 * 3600, key="set_session_cookie")
        except Exception:
            pass

if st.session_state.get("_theme_changed") and _theme_cookie != st.session_state.get("ui_theme"):
    try:
        cookie_manager.set(THEME_COOKIE, st.session_state.get("ui_theme"), max_age=365 * 24 * 3600, key="set_theme_cookie")
    except Exception:
        pass

# Chỉ ghi cookie khi người dùng tự đổi ngôn ngữ
if st.session_state.get("_lang_changed") and _lang_cookie != ui_lang():
    try:
        cookie_manager.set(LANG_COOKIE, ui_lang(), max_age=365 * 24 * 3600, key="set_lang_cookie")
    except Exception:
        pass

# ==========================================
# 🔐 HỆ THỐNG XÁC THỰC
# ==========================================
if not st.session_state["logged_in"]:
    st.sidebar.markdown("<div class='sidebar-header'>🔐 Xác Thực</div>", unsafe_allow_html=True)
    st.sidebar.info("Vui lòng đăng nhập hoặc đăng ký để tiếp tục.")
    if st.session_state.get("_kicked"):
        st.warning("🔒 Tài khoản của bạn vừa được mở ở một tab hoặc thiết bị khác, nên bạn đã bị đăng xuất khỏi trang này. "
                   "Nếu đó không phải bạn, hãy đăng nhập lại và đổi mật khẩu ngay.")

    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        is_login = st.session_state["auth_tab"] == "login"
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            st.button("🔑 Đăng Nhập", type="primary" if is_login else "secondary", use_container_width=True, key="btn_auth_tab_login",
                      on_click=lambda: st.session_state.update({"auth_tab": "login"}))
                
        with t_col2:
            st.button("📝 Đăng Ký Tài Khoản", type="primary" if not is_login else "secondary", use_container_width=True, key="btn_auth_tab_reg",
                      on_click=lambda: st.session_state.update({"auth_tab": "register"}))

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # 📲 Chọn thiết bị ngay khi đăng nhập (Điện thoại → có nút 🎤 nói để nhập chữ)
        st.session_state["device_mode_login"] = st.session_state["device_mode"]
        st.radio("📲 Bạn đang dùng:", DEVICE_OPTIONS, key="device_mode_login", horizontal=True,
                 on_change=_on_login_device_change, format_func=lambda d: DEVICE_LABELS[d])
        if st.session_state["device_mode"] == "mobile":
            st.caption("🎤 Chế độ điện thoại: bấm nút micro trong ô Tên tài khoản để nói thay vì gõ.")

        if st.session_state["auth_tab"] == "login":
            with st.form("form_login_system"):
                login_user = st.text_input("Tên tài khoản (Username):")
                login_pass = st.text_input("Mật khẩu (Password):", type="password")
                btn_login = st.form_submit_button("🚀 ĐĂNG NHẬP")

                if btn_login:
                    if not login_user or not login_pass:
                        st.error("Vui lòng nhập đầy đủ Username và Mật khẩu!")
                    else:
                        user = cursor.execute("SELECT id, username, password, fullname, role, workshop FROM users WHERE username = ? AND is_deleted = 0", (login_user.strip(),)).fetchone()
                        if user and not verify_password(login_pass, user[2]):
                            user = None
                        if user:
                            # Tự động nâng cấp hash cũ (SHA-256) lên PBKDF2
                            if is_legacy_hash(user[2]):
                                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(login_pass), user[0]))
                                conn.commit()
                            user_role = user[4] if len(user) > 4 and user[4] else 'Pending'
                            
                            if user_role == 'Pending':
                                st.warning("⏳ Tài khoản của bạn đang chờ Admin / WOS Manager cấp Role. Vui lòng quay lại sau!")
                            else:
                                st.session_state["logged_in"] = True
                                st.session_state["user_info"] = {"id": user[0], "username": user[1], "fullname": user[3], "role": user_role, "workshop": user[5]}
                                
                                token = create_session(user[0])
                                st.session_state["session_token"] = token
                                st.session_state["_kicked"] = False
                                # Cookie được ghi ở lần chạy sau (ghi ngay rồi st.rerun thì trình duyệt không kịp lưu)
                                st.session_state["_pending_session_cookie"] = token
                                st.success(f"Chào mừng {user[3]} ({user_role}) đã quay trở lại!")
                                st.rerun()
                        else:
                            st.error("Sai tên tài khoản, mật khẩu hoặc tài khoản đã bị khóa/xóa!")

        else:
            with st.form("form_register_system"):
                reg_fullname = st.text_input("Họ và Tên:")
                reg_user = st.text_input("Tên đăng nhập mới (Username):")
                reg_pass = st.text_input("Mật khẩu mới:", type="password")
                reg_confirm = st.text_input("Xác nhận lại mật khẩu:", type="password")
                
                btn_register = st.form_submit_button("✨ ĐĂNG KÝ NGAY")

                if btn_register:
                    reg_user = reg_user.strip()
                    reg_fullname = reg_fullname.strip()
                    if not reg_fullname or not reg_user or not reg_pass:
                        st.error("Vui lòng điền đầy đủ các thông tin!")
                    elif len(reg_pass) < 8:
                        st.error("Mật khẩu phải có ít nhất 8 ký tự!")
                    elif len(reg_user) > 50 or len(reg_fullname) > 100:
                        st.error("Username hoặc Họ tên quá dài!")
                    elif reg_pass != reg_confirm:
                        st.error("Mật khẩu xác nhận không trùng khớp!")
                    else:
                        try:
                            # LƯU VỚI ROLE LÀ Pending CHỜ ADMIN DUYỆT EMAIL
                            cursor.execute("INSERT INTO users (username, password, fullname, role, is_deleted) VALUES (?, ?, ?, 'Pending', 0)", 
                                           (reg_user, hash_password(reg_pass), reg_fullname))
                            conn.commit()
                            
                            # GỬI EMAIL THÔNG BÁO ĐẾN ADMIN (không chứa link cấp quyền)
                            send_new_user_email(reg_user, reg_fullname)
                            
                            st.success("🎉 Đăng ký thành công! Tài khoản đang chờ WOS Manager phê duyệt Role.")
                        except sqlite3.IntegrityError:
                            st.error("Tên đăng nhập này đã tồn tại, vui lòng chọn tên khác!")

# ==========================================
# 🚢 GIAO DIỆN CHÍNH
# ==========================================
else:
    user_data = st.session_state["user_info"]
    current_role = user_data.get("role", "Worker")

    st.sidebar.markdown("<div class='sidebar-header'>☸️ Control Menu</div>", unsafe_allow_html=True)

    if st.session_state.get("current_menu") in (CHAT_MENU, MEETING_MENU):
        st.session_state["connect_tab"] = "meet" if st.session_state["current_menu"] == MEETING_MENU else "chat"
        st.session_state["current_menu"] = CONNECT_MENU
    is_admin = current_role == "Admin"
    is_manager_up = current_role in ["Admin", "WOS Manager"]

    if is_manager_up:
        menu_options = [
            "🧰 Bảng Công Việc", 
            "💬 Tin Nhắn & Họp",
            "➕ Thêm Công Việc", 
            "📋 Giao Việc",
            "✏️ Chỉnh Sửa/Xóa",
            "👥 Quản Lý Phân Quyền",
            "🗑️ Thùng Rác",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    elif current_role == "Foreman":
        menu_options = [
            "🧰 Bảng Công Việc", 
            "💬 Tin Nhắn & Họp",
            "➕ Thêm Công Việc", 
            "👥 Team Của Tôi",
            "📋 Giao Việc",
            "✏️ Chỉnh Sửa/Xóa",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    elif current_role == "Team Leader":
        menu_options = [
            "🧰 Bảng Công Việc", 
            "💬 Tin Nhắn & Họp",
            "➕ Thêm Công Việc",
            "👥 Team Của Tôi",
            "📋 Giao Việc",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    else:
        menu_options = [
            "🧰 Bảng Công Việc",
            "💬 Tin Nhắn & Họp",
            "👥 Team Của Tôi",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]

    def _go_to_page(target):
        st.session_state["current_menu"] = target

    try:
        _chat_unread_total = sum(chat_unread_by_conv(user_data["id"]).values())
    except sqlite3.OperationalError:
        _chat_unread_total = 0

    for item in menu_options:
        is_selected = (st.session_state["current_menu"] == item)
        _label = item + (f"  🔴 {_chat_unread_total}" if item == CONNECT_MENU and _chat_unread_total else "")
        # on_click đổi trang TRƯỚC khi app chạy lại → chỉ chạy 1 lần thay vì 2 lần
        st.sidebar.button(
            _label, 
            type="primary" if is_selected else "secondary", 
            use_container_width=True, 
            key=f"btn_menu_{item}",
            on_click=_go_to_page,
            args=(item,),
        )

    menu = st.session_state["current_menu"]
    
    role_icons = {
        "Admin": "🛡️ Admin",
        "WOS Manager": "👑 WOS Manager",
        "Foreman": "👔 Foreman",
        "Team Leader": "🧢 Team Leader",
        "Worker": "👷 Worker"
    }
    role_badge = role_icons.get(current_role, f"👤 {current_role}")

    # 🪪 THẺ TÀI KHOẢN: ngay dưới menu, cho biết đang đăng nhập bằng tài khoản nào và vai trò gì
    _full = str(user_data.get('fullname') or user_data['username'])
    _words = [w for w in _full.split() if w]
    _initials = ((_words[0][0] + (_words[-1][0] if len(_words) > 1 else "")) if _words else "?").upper()
    _ws_code = user_data.get('workshop')
    _ws_row = ""
    if _ws_code:
        _ws_name = cursor.execute("SELECT name FROM custom_cost_codes WHERE code = ?", (_ws_code,)).fetchone()
        _ws_text = f"{_ws_code} · {_ws_name[0]}" if _ws_name and _ws_name[0] else _ws_code
        _ws_row = (f"<div class='pc-row'><span class='pc-label'>Workshop</span>"
                   f"<span class='pc-val'>{html.escape(_ws_text)}</span></div>")
    st.sidebar.markdown(f"""<div class='profile-card'>
<div class='pc-top'><div class='pc-avatar'>{html.escape(_initials)}</div>
<div class='pc-id'><div class='pc-name'>{html.escape(_full)}</div><div class='pc-status'>● <span>Đang đăng nhập</span></div></div></div>
<div class='pc-row'><span class='pc-label'>Tài khoản</span><span class='pc-val'>@{html.escape(str(user_data['username']))}</span></div>
<div class='pc-row'><span class='pc-label'>Vai trò</span><span class='pc-role'>{html.escape(role_badge)}</span></div>{_ws_row}</div>""", unsafe_allow_html=True)


    my_pw = cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],)).fetchone()
    # Kiểm tra mật khẩu mặc định rất tốn thời gian (băm 200.000 vòng), nên chỉ kiểm tra lại khi mật khẩu thay đổi
    if my_pw and st.session_state.get("_pw_checked_hash") != my_pw[0]:
        st.session_state["_pw_checked_hash"] = my_pw[0]
        st.session_state["_pw_is_default"] = verify_password("admin123", my_pw[0])
    if my_pw and st.session_state.get("_pw_is_default"):
        st.error("⚠️ Tài khoản này vẫn dùng mật khẩu mặc định 'admin123'. Vào mục 🔑 Đổi Mật Khẩu và đổi NGAY!")

    if st.sidebar.button("🚪 Đăng Xuất", type="secondary", key="btn_logout_bottom", use_container_width=True):
        tok = st.session_state.get("session_token")
        if tok:
            delete_session(tok)
        try:
            cookie_manager.delete(SESSION_COOKIE)
        except Exception:
            pass
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
        st.rerun()

    # 🎞️ KHUNG TRANG: mỗi lần đổi trang tạo khung mới để hiệu ứng lướt chạy lại.
    #    Bấm nút trong cùng một trang thì khung giữ nguyên, không bị lướt lại.
    page_idx = menu_options.index(menu) if menu in menu_options else 0
    prev_idx = st.session_state.get("page_prev_idx")
    if prev_idx != page_idx:
        st.session_state["page_dir"] = "L" if (prev_idx is not None and page_idx < prev_idx) else "R"
        st.session_state["page_prev_idx"] = page_idx
    _page_frame = st.container(key=f"pg{st.session_state.get('page_dir', 'R')}_{page_idx}")
    _page_frame.__enter__()

    # 💬 Tin Nhắn & Họp: 1 nút menu, bên trong có 2 thẻ (Tin nhắn | Họp online)
    if menu == CONNECT_MENU:
        st.markdown("<div class='big-table-title'>💬 Tin Nhắn & Họp</div>", unsafe_allow_html=True)
        st.session_state.setdefault("connect_tab", "chat")
        _ct1, _ct2, _ct_space = st.columns([1.3, 1.3, 2])
        with _ct1:
            st.button("💬 Tin Nhắn" + (f"  🔴 {_chat_unread_total}" if _chat_unread_total else ""),
                      key="btn_connect_chat", use_container_width=True,
                      type="primary" if st.session_state["connect_tab"] == "chat" else "secondary",
                      on_click=lambda: st.session_state.update({"connect_tab": "chat"}))
        with _ct2:
            st.button("🎥 Họp Online", key="btn_connect_meet", use_container_width=True,
                      type="primary" if st.session_state["connect_tab"] == "meet" else "secondary",
                      on_click=lambda: st.session_state.update({"connect_tab": "meet"}))
        menu = CHAT_MENU if st.session_state["connect_tab"] == "chat" else MEETING_MENU

    # 1. BẢNG CÔNG VIỆC
    if menu == "🧰 Bảng Công Việc":
        st.markdown("<div class='big-table-title'>📋 Bảng Quản Lý Tiến Độ Công Việc</div>", unsafe_allow_html=True)
        
        df = pd.read_sql_query("""
            SELECT 
                t.id AS _id,
                t.assigned_leader_id AS _leader_id,
                t.assigned_worker_id AS _worker_id,
                t.task_id AS 'Task ID', 
                t.task_name AS 'Task Name', 
                t.task_cost_code AS 'WS Cost Code', 
                t.description AS 'Description',
                t.initial_by AS 'Initial By', 
                t.initial_date AS 'Initial Date', 
                t.block AS 'Block', 
                t.area AS 'Area', 
                t.deck AS 'Deck', 
                t.frame AS 'Frame', 
                t.in_charge_by AS 'In Charge By', 
                l.team_name AS 'Team',
                l.fullname AS 'Leader / Foreman',
                w.fullname AS 'Worker',
                t.plan_start_date AS 'Plan Start Date', 
                t.plan_finish_date AS 'Plan Finish Date', 
                t.progress AS 'Progress (%)', 
                t.remark AS 'Remark' 
            FROM tasks t
            LEFT JOIN users l ON l.id = t.assigned_leader_id
            LEFT JOIN users w ON w.id = t.assigned_worker_id
            WHERE t.is_deleted = 0
        """, conn)

        my_id = user_data['id']
        if current_role == "Worker":
            df = df[df['_worker_id'] == my_id]
            st.caption("👷 Đây là các công việc được giao cho bạn.")
        elif current_role in LEADER_ROLES:
            only_team = st.toggle("Chỉ xem công việc của team tôi", value=True)
            if only_team:
                df = df[df['_leader_id'] == my_id]
        
        if df.empty:
            st.info("Chưa có công việc nào để hiển thị.")
        else:
            st.dataframe(df.drop(columns=['_id', '_leader_id', '_worker_id']), use_container_width=True, height=400)
            
            st.markdown("---")
            st.markdown("### ⚡ Cập Nhật Tiến Độ Công Việc Nhanh")

            # Ai được cập nhật việc nào: Worker = việc của mình, Leader = việc của team, Manager = tất cả
            if current_role == "Worker":
                upd_df = df
            elif current_role in LEADER_ROLES:
                upd_df = df[df['_leader_id'] == my_id]
            else:
                upd_df = df

            if upd_df.empty:
                st.info("Bạn chưa có công việc nào để cập nhật tiến độ.")
            else:
                options_tasks = [f"{row['_id']} | {row['Task ID']} - {row['Task Name']} (Hiện tại: {row['Progress (%)']}%)" for _, row in upd_df.iterrows()]
                selected_update_task = st.selectbox("Chọn công việc cần cập nhật tiến độ:", options_tasks)
                selected_task_id = int(selected_update_task.split(" | ")[0])
                
                curr_task = cursor.execute("SELECT progress, remark FROM tasks WHERE id = ?", (selected_task_id,)).fetchone()
                
                with st.form("quick_update_progress_form"):
                    u_col1, u_col2 = st.columns([1, 2])
                    with u_col1:
                        new_progress = st.number_input("Mức Tiến Độ Mới (%)", min_value=0, max_value=100, value=int(curr_task[0] or 0), step=5)
                    with u_col2:
                        new_remark = st.text_input("Ghi Chú Thi Công (Remark):", value=curr_task[1] if curr_task[1] else "")
                    
                    btn_update_p = st.form_submit_button("🚀 CẬP NHẬT TIẾN ĐỘ")
                    if btn_update_p:
                        cursor.execute("UPDATE tasks SET progress = ?, remark = ? WHERE id = ?", (new_progress, new_remark.strip(), selected_task_id))
                        conn.commit()
                        st.success("Đã cập nhật tiến độ công việc thành công!")
                        st.rerun()

    # 3. THÊM CÔNG VIỆC MỚI
    elif menu == "➕ Thêm Công Việc" and current_role in ["Team Leader", "Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>➕ Thêm Công Việc Mới</div>", unsafe_allow_html=True)

        # ⚙️ Thêm / xóa trong danh sách Block và WS Cost Code (Foreman, WOS Manager, Admin)
        if current_role in ["Foreman", "WOS Manager", "Admin"]:
            with st.expander("⚙️ Thêm / Xóa trong danh sách Block và WS Cost Code"):
                lc1, lc2 = st.columns(2)

                with lc1:
                    st.markdown("#### 🧱 Block")
                    nb = st.text_input("Block mới (Ví dụ: 170150):", key="new_block_name")
                    if st.button("➕ THÊM BLOCK", key="btn_add_block"):
                        nb_clean = nb.strip().upper()
                        if not nb_clean:
                            st.error("Vui lòng nhập tên Block!")
                        else:
                            ex = cursor.execute("SELECT is_deleted FROM blocks WHERE name = ?", (nb_clean,)).fetchone()
                            if ex and ex[0] == 0:
                                st.error(f"Block **{nb_clean}** đã có trong danh sách!")
                            else:
                                if ex:
                                    cursor.execute("UPDATE blocks SET is_deleted = 0 WHERE name = ?", (nb_clean,))
                                else:
                                    cursor.execute("INSERT INTO blocks (name, is_deleted) VALUES (?, 0)", (nb_clean,))
                                conn.commit()
                                st.success(f"Đã thêm Block **{nb_clean}**!")
                                st.rerun()

                    blk_list = [r[0] for r in cursor.execute("SELECT name FROM blocks WHERE is_deleted = 0 ORDER BY name").fetchall()]
                    if blk_list:
                        del_blk = st.selectbox("Chọn Block để xóa:", blk_list, key="sb_del_block")
                        if st.button("🗑️ XÓA BLOCK", key="btn_del_block"):
                            cursor.execute("UPDATE blocks SET is_deleted = 1 WHERE name = ?", (del_blk,))
                            conn.commit()
                            st.success(f"Đã xóa Block **{del_blk}** khỏi danh sách. Công việc cũ vẫn giữ nguyên.")
                            st.rerun()
                    else:
                        st.caption("Danh sách Block đang trống.")

                with lc2:
                    st.markdown("#### 🏭 WS Cost Code")
                    ncc1, ncc2 = st.columns([1, 2])
                    with ncc1:
                        nc_code = st.text_input("Mã (Ví dụ: WOS_07):", key="new_cc_code")
                    with ncc2:
                        nc_name = st.text_input("Tên Workshop / Phòng ban:", key="new_cc_name")
                    if st.button("➕ THÊM COST CODE", key="btn_add_cc"):
                        code_clean = nc_code.strip().upper()
                        name_clean = nc_name.strip()
                        if not code_clean or not name_clean:
                            st.error("Vui lòng nhập cả Mã và Tên!")
                        else:
                            ex = cursor.execute("SELECT is_deleted FROM custom_cost_codes WHERE code = ?", (code_clean,)).fetchone()
                            if ex and ex[0] == 0:
                                st.error(f"Mã **{code_clean}** đã có trong danh sách!")
                            else:
                                if ex:
                                    cursor.execute("UPDATE custom_cost_codes SET name = ?, is_deleted = 0 WHERE code = ?", (name_clean, code_clean))
                                else:
                                    cursor.execute("INSERT INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, '', 0)",
                                                   (code_clean, name_clean))
                                conn.commit()
                                st.success(f"Đã thêm **{code_clean} - {name_clean}**!")
                                st.rerun()

                    cc_df = pd.read_sql_query("SELECT code, COALESCE(name, '') AS name FROM custom_cost_codes WHERE is_deleted = 0 ORDER BY code", conn)
                    if not cc_df.empty:
                        cc_opts = {r['code']: f"{r['code']} - {r['name']}" for _, r in cc_df.iterrows()}
                        del_cc = st.selectbox("Chọn Cost Code để xóa:", list(cc_opts.keys()), format_func=lambda c: cc_opts[c], key="sb_del_cc")
                        if st.button("🗑️ XÓA COST CODE", key="btn_del_cc"):
                            users_in_ws = cursor.execute("SELECT COUNT(*) FROM users WHERE workshop = ? AND is_deleted = 0", (del_cc,)).fetchone()[0]
                            if users_in_ws > 0:
                                st.error(f"Không thể xóa: còn **{users_in_ws}** tài khoản thuộc workshop này. "
                                         "Hãy chuyển họ sang workshop khác ở 👥 Quản Lý Phân Quyền trước.")
                            else:
                                cursor.execute("UPDATE custom_cost_codes SET is_deleted = 1 WHERE code = ?", (del_cc,))
                                conn.commit()
                                st.success(f"Đã xóa **{cc_opts[del_cc]}** khỏi danh sách. Công việc cũ vẫn giữ nguyên.")
                                st.rerun()
                    else:
                        st.caption("Danh sách Cost Code đang trống.")

        cost_codes_df = pd.read_sql_query("SELECT code, COALESCE(name, '') AS name FROM custom_cost_codes WHERE is_deleted = 0 ORDER BY code", conn)
        block_options = ["— Không chọn —"] + [r[0] for r in cursor.execute("SELECT name FROM blocks WHERE is_deleted = 0 ORDER BY name").fetchall()]
        
        if cost_codes_df.empty:
            st.warning("⚠️ CHƯA CÓ WS COST CODE: Foreman / WOS Manager hãy thêm Cost Code ở mục ⚙️ phía trên trước khi thêm công việc!")
        else:
            options = [f"{row['code']} - {row['name']}" if row['name'] else row['code'] for _, row in cost_codes_df.iterrows()]
            
            with st.form("add_task_form_full", clear_on_submit=True):
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    task_id = st.text_input("Task ID *")
                with c2:
                    task_name_input = st.text_input("Task Name *")
                with c3:
                    selected_cost_code = st.selectbox("WS Cost Code *", options)

                description = st.text_area("Description (Mô tả công việc):", height=80)

                c4, c5, c6 = st.columns(3)
                with c4:
                    initial_by = st.text_input("Initial By (Người khởi tạo):", value=user_data['fullname'])
                with c5:
                    initial_date = st.date_input("Initial Date (Ngày tạo):", value=date.today())
                with c6:
                    in_charge_by = st.text_input("In Charge By (Người phụ trách):")

                c7, c8, c9, c10 = st.columns(4)
                with c7:
                    block = st.selectbox("Block:", block_options)
                    if block == "— Không chọn —":
                        block = ""
                with c8:
                    area = st.text_input("Area:")
                with c9:
                    deck = st.text_input("Deck:")
                with c10:
                    frame = st.text_input("Frame:")

                c11, c12, c13 = st.columns(3)
                with c11:
                    plan_start = st.date_input("Plan Start Date:", value=date.today())
                with c12:
                    plan_finish = st.date_input("Plan Finish Date:", value=date.today())
                with c13:
                    progress_val = st.number_input("Progress (%)", min_value=0, max_value=100, value=0, step=5)

                remark = st.text_input("Remark (Ghi chú):")

                # Giao việc ngay khi tạo
                new_task_leader_id = None
                if current_role in LEADER_ROLES:
                    new_task_leader_id = user_data['id']
                    st.caption("📌 Công việc này sẽ thuộc team của bạn. Vào 📋 Giao Việc để giao cho Worker.")
                else:
                    leaders_df_add = pd.read_sql_query(
                        "SELECT id, fullname, role, workshop FROM users WHERE is_deleted = 0 AND role IN ('Team Leader', 'Foreman') ORDER BY fullname", conn)
                    leader_opts_add = {None: "— Chưa giao —"}
                    for _, r in leaders_df_add.iterrows():
                        leader_opts_add[int(r['id'])] = f"{r['fullname']} ({r['role']}{', ' + r['workshop'] if r['workshop'] else ''})"
                    new_task_leader_id = st.selectbox("Giao cho Team Leader / Foreman:", list(leader_opts_add.keys()),
                                                      format_func=lambda k: leader_opts_add[k])

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
                
                if submitted:
                    if not task_id.strip() or not task_name_input.strip():
                        st.error("Vui lòng điền đầy đủ thông tin bắt buộc: Task ID và Task Name!")
                    elif plan_finish < plan_start:
                        st.error("Plan Finish Date không được trước Plan Start Date!")
                    elif cursor.execute("SELECT 1 FROM tasks WHERE task_id = ?", (task_id.strip(),)).fetchone():
                        st.error(f"Task ID **{task_id.strip()}** đã tồn tại (có thể đang trong Thùng Rác). Vui lòng dùng ID khác!")
                    else:
                        ws_code_only = selected_cost_code.split(" - ")[0]
                        cursor.execute("""
                            INSERT INTO tasks (
                                task_id, task_name, task_cost_code, description,
                                initial_by, initial_date, block, area, deck, frame,
                                in_charge_by, plan_start_date, plan_finish_date,
                                progress, remark, assigned_leader_id, is_deleted
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """, (
                            task_id.strip(), task_name_input.strip(), ws_code_only,
                            description.strip(), initial_by.strip(), str(initial_date),
                            block.strip(), area.strip(), deck.strip(), frame.strip(),
                            in_charge_by.strip(), str(plan_start), str(plan_finish),
                            int(progress_val), remark.strip(), new_task_leader_id
                        ))
                        conn.commit()
                        st.success(f"Đã lưu thành công công việc **{task_id} - {task_name_input}**!")

    # 3B. GIAO VIỆC
    #    - WOS Manager / Admin: giao công việc cho Team Leader / Foreman
    #    - Team Leader / Foreman: giao công việc của team mình cho Worker trong team
    elif menu == "📋 Giao Việc" and current_role in ["Team Leader", "Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>📋 Giao Việc</div>", unsafe_allow_html=True)

        if is_manager_up:
            st.info("👑 Chọn công việc và giao cho một **Team Leader** hoặc **Foreman**. Họ sẽ giao tiếp cho Worker trong team.")
            tasks_df = pd.read_sql_query("""
                SELECT t.id, t.task_id, t.task_name, t.task_cost_code, t.assigned_leader_id, l.fullname AS leader_name
                FROM tasks t LEFT JOIN users l ON l.id = t.assigned_leader_id
                WHERE t.is_deleted = 0 ORDER BY t.id DESC
            """, conn)
            leaders_df = pd.read_sql_query(
                "SELECT id, fullname, role, workshop FROM users WHERE is_deleted = 0 AND role IN ('Team Leader', 'Foreman') ORDER BY fullname", conn)

            if tasks_df.empty:
                st.info("Chưa có công việc nào. Vào ➕ Thêm Công Việc để tạo.")
            elif leaders_df.empty:
                st.warning("Chưa có Team Leader / Foreman nào. Vào 👥 Quản Lý Phân Quyền để cấp role trước.")
            else:
                show_unassigned = st.toggle("Chỉ hiện công việc chưa giao", value=False)
                if show_unassigned:
                    tasks_df = tasks_df[tasks_df['assigned_leader_id'].isna()]
                if tasks_df.empty:
                    st.success("Tất cả công việc đã được giao!")
                else:
                    task_opts = {int(r['id']): f"{r['task_id']} - {r['task_name']} ({r['task_cost_code']}) → "
                                               f"{r['leader_name'] if r['leader_name'] else 'Chưa giao'}"
                                 for _, r in tasks_df.iterrows()}
                    sel_task = st.selectbox("Chọn công việc:", list(task_opts.keys()), format_func=lambda k: task_opts[k])

                    leader_opts = {None: "— Chưa giao —"}
                    for _, r in leaders_df.iterrows():
                        leader_opts[int(r['id'])] = f"{r['fullname']} ({r['role']}{', ' + r['workshop'] if r['workshop'] else ''})"
                    cur_leader = tasks_df.loc[tasks_df['id'] == sel_task, 'assigned_leader_id'].iloc[0]
                    cur_leader = None if pd.isna(cur_leader) else int(cur_leader)
                    keys = list(leader_opts.keys())
                    sel_leader = st.selectbox("Giao cho Team Leader / Foreman:", keys,
                                              index=keys.index(cur_leader) if cur_leader in keys else 0,
                                              format_func=lambda k: leader_opts[k])

                    if st.button("💾 LƯU GIAO VIỆC", type="primary", key="btn_assign_leader"):
                        if sel_leader != cur_leader:
                            # Đổi người phụ trách thì bỏ Worker cũ (vì Worker thuộc team cũ)
                            cursor.execute("UPDATE tasks SET assigned_leader_id = ?, assigned_worker_id = NULL WHERE id = ?",
                                           (sel_leader, sel_task))
                            conn.commit()
                        st.success(f"Đã giao công việc cho **{leader_opts[sel_leader]}**!")
                        st.rerun()

        else:
            my_id = user_data['id']
            team_df = pd.read_sql_query(
                "SELECT id, username, fullname FROM users WHERE is_deleted = 0 AND role = 'Worker' AND leader_id = ? ORDER BY fullname",
                conn, params=(my_id,))

            my_team_name = cursor.execute("SELECT team_name FROM users WHERE id = ?", (my_id,)).fetchone()[0]
            st.markdown(f"### 👷 Team: {html.escape(my_team_name) if my_team_name else '(chưa đặt tên)'} – {len(team_df)} Worker")
            if team_df.empty:
                st.info("Team của bạn chưa có Worker nào. Vào 👥 Team Của Tôi để tạo team và thêm Worker.")

            st.markdown("---")
            st.markdown("### 📌 Giao Việc Cho Worker")
            my_tasks = pd.read_sql_query("""
                SELECT t.id, t.task_id, t.task_name, t.progress, t.assigned_worker_id, w.fullname AS worker_name
                FROM tasks t LEFT JOIN users w ON w.id = t.assigned_worker_id
                WHERE t.is_deleted = 0 AND t.assigned_leader_id = ? ORDER BY t.id DESC
            """, conn, params=(my_id,))

            if my_tasks.empty:
                st.info("Bạn chưa được giao công việc nào.")
            elif team_df.empty:
                st.warning("Cần có Worker trong team trước khi giao việc.")
            else:
                task_opts = {int(r['id']): f"{r['task_id']} - {r['task_name']} ({r['progress']}%) → "
                                           f"{r['worker_name'] if r['worker_name'] else 'Chưa giao'}"
                             for _, r in my_tasks.iterrows()}
                sel_task = st.selectbox("Chọn công việc:", list(task_opts.keys()), format_func=lambda k: task_opts[k])

                worker_opts = {None: "— Chưa giao —"}
                for _, r in team_df.iterrows():
                    worker_opts[int(r['id'])] = f"{r['fullname']} (@{r['username']})"
                cur_worker = my_tasks.loc[my_tasks['id'] == sel_task, 'assigned_worker_id'].iloc[0]
                cur_worker = None if pd.isna(cur_worker) else int(cur_worker)
                keys = list(worker_opts.keys())
                sel_worker = st.selectbox("Giao cho Worker:", keys,
                                          index=keys.index(cur_worker) if cur_worker in keys else 0,
                                          format_func=lambda k: worker_opts[k])

                if st.button("💾 LƯU GIAO VIỆC", type="primary", key="btn_assign_worker"):
                    cursor.execute("UPDATE tasks SET assigned_worker_id = ? WHERE id = ? AND assigned_leader_id = ?",
                                   (sel_worker, sel_task, my_id))
                    conn.commit()
                    st.success(f"Đã giao công việc cho **{worker_opts[sel_worker]}**!")
                    st.rerun()

    # 3C. TEAM CỦA TÔI
    #    - Team Leader / Foreman: đặt tên team, thêm Worker CÙNG WORKSHOP (chưa thuộc team nào), xóa khỏi team
    #    - Worker: xem team của mình và có thể rời team
    elif menu == "👥 Team Của Tôi" and current_role in ["Team Leader", "Foreman", "Worker"]:
        st.markdown("<div class='big-table-title'>👥 Team Của Tôi</div>", unsafe_allow_html=True)
        my_id = user_data['id']
        my_ws = user_data.get("workshop")

        if current_role in LEADER_ROLES:
            my_team_name = cursor.execute("SELECT team_name FROM users WHERE id = ?", (my_id,)).fetchone()[0]

            if not my_ws:
                st.warning("⚠️ Tài khoản của bạn chưa được gán Workshop. Nhờ WOS Manager gán Workshop trước khi lập team.")
            elif not my_team_name:
                # Bước 1: tạo team (đặt tên)
                st.info("Bạn chưa có team. Hãy đặt tên để tạo team.")
                with st.form("create_team_form"):
                    new_team_name = st.text_input("Tên Team *", placeholder="Ví dụ: Team Hàn Block 170")
                    if st.form_submit_button("➕ TẠO TEAM"):
                        if not new_team_name.strip():
                            st.error("Vui lòng nhập tên team!")
                        elif len(new_team_name.strip()) > 60:
                            st.error("Tên team tối đa 60 ký tự!")
                        else:
                            cursor.execute("UPDATE users SET team_name = ? WHERE id = ?", (new_team_name.strip(), my_id))
                            conn.commit()
                            st.success(f"Đã tạo team **{new_team_name.strip()}**!")
                            st.rerun()
            else:
                st.markdown(f"### 🏷️ {html.escape(my_team_name)}")
                st.caption(f"🏭 Workshop: {my_ws}")

                with st.expander("✏️ Đổi tên team"):
                    with st.form("rename_team_form"):
                        renamed = st.text_input("Tên team mới:", value=my_team_name)
                        if st.form_submit_button("💾 LƯU TÊN"):
                            if not renamed.strip() or len(renamed.strip()) > 60:
                                st.error("Tên team không hợp lệ (1–60 ký tự)!")
                            else:
                                cursor.execute("UPDATE users SET team_name = ? WHERE id = ?", (renamed.strip(), my_id))
                                conn.commit()
                                st.success("Đã đổi tên team!")
                                st.rerun()

                with st.expander("🗑️ Xóa team"):
                    st.warning("Khi xóa team: tất cả Worker sẽ rời team, và các công việc đang giao cho họ sẽ trở về "
                               "trạng thái chưa giao. Công việc vẫn thuộc về bạn, bạn có thể tạo team mới sau.")
                    confirm_delete_team = st.checkbox("Tôi chắc chắn muốn xóa team này", key="chk_delete_team")
                    if st.button("🗑️ XÓA TEAM", type="secondary", key="btn_delete_team", disabled=not confirm_delete_team):
                        cursor.execute("UPDATE tasks SET assigned_worker_id = NULL WHERE assigned_leader_id = ?", (my_id,))
                        cursor.execute("UPDATE users SET leader_id = NULL WHERE leader_id = ?", (my_id,))
                        cursor.execute("UPDATE users SET team_name = NULL WHERE id = ?", (my_id,))
                        conn.commit()
                        st.success("Đã xóa team.")
                        st.rerun()

                team_df = pd.read_sql_query(
                    "SELECT id, username, fullname FROM users WHERE is_deleted = 0 AND role = 'Worker' AND leader_id = ? ORDER BY fullname",
                    conn, params=(my_id,))

                st.markdown("#### 👷 Thành Viên")
                if team_df.empty:
                    st.info("Team chưa có Worker nào.")
                else:
                    st.dataframe(team_df.rename(columns={'username': 'Username', 'fullname': 'Họ và Tên'}).drop(columns=['id']),
                                 use_container_width=True)

                st.markdown("---")
                col_add, col_remove = st.columns(2)

                with col_add:
                    st.markdown("#### ➕ Thêm Worker")
                    # Chỉ lấy Worker cùng workshop và chưa thuộc team nào
                    free_workers = pd.read_sql_query("""
                        SELECT id, username, fullname FROM users
                        WHERE is_deleted = 0 AND role = 'Worker' AND workshop = ? AND leader_id IS NULL
                        ORDER BY fullname
                    """, conn, params=(my_ws,))
                    if free_workers.empty:
                        st.caption(f"Không còn Worker nào trong workshop {my_ws} chưa có team.")
                    else:
                        fw_opts = {int(r['id']): f"{r['fullname']} (@{r['username']})" for _, r in free_workers.iterrows()}
                        to_add = st.multiselect("Chọn Worker (cùng workshop, chưa có team):", list(fw_opts.keys()),
                                                format_func=lambda k: fw_opts[k])
                        if st.button("➕ THÊM VÀO TEAM", type="primary", key="btn_add_team_members"):
                            if not to_add:
                                st.error("Hãy chọn ít nhất 1 Worker!")
                            else:
                                for wid in to_add:
                                    # Kiểm tra lại phía server: đúng workshop và vẫn chưa có team
                                    cursor.execute("""UPDATE users SET leader_id = ?
                                                      WHERE id = ? AND role = 'Worker' AND workshop = ? AND leader_id IS NULL AND is_deleted = 0""",
                                                   (my_id, wid, my_ws))
                                conn.commit()
                                st.success(f"Đã thêm {len(to_add)} Worker vào team!")
                                st.rerun()

                with col_remove:
                    st.markdown("#### ➖ Xóa Khỏi Team")
                    if team_df.empty:
                        st.caption("Chưa có thành viên để xóa.")
                    else:
                        tm_opts = {int(r['id']): f"{r['fullname']} (@{r['username']})" for _, r in team_df.iterrows()}
                        to_remove = st.selectbox("Chọn Worker:", list(tm_opts.keys()), format_func=lambda k: tm_opts[k])
                        if st.button("➖ XÓA KHỎI TEAM", type="secondary", key="btn_remove_team_member"):
                            remove_worker_from_team(to_remove, my_id)
                            st.success("Đã xóa Worker khỏi team. Các việc của team giao cho người này đã được bỏ giao.")
                            st.rerun()

        else:
            # WORKER
            my_leader = cursor.execute("""
                SELECT l.id, l.fullname, l.role, l.team_name FROM users me
                JOIN users l ON l.id = me.leader_id
                WHERE me.id = ? AND l.is_deleted = 0
            """, (my_id,)).fetchone()

            if not my_leader:
                st.info("Bạn chưa thuộc team nào. Team Leader / Foreman trong workshop của bạn có thể thêm bạn vào team.")
            else:
                leader_id, leader_name, leader_role, team_name = my_leader
                st.markdown(f"### 🏷️ {html.escape(team_name) if team_name else '(Team chưa đặt tên)'}")
                st.markdown(f"**Trưởng team:** {html.escape(leader_name)} ({leader_role})")

                mates = pd.read_sql_query(
                    "SELECT username, fullname FROM users WHERE is_deleted = 0 AND role = 'Worker' AND leader_id = ? ORDER BY fullname",
                    conn, params=(leader_id,))
                st.dataframe(mates.rename(columns={'username': 'Username', 'fullname': 'Họ và Tên'}), use_container_width=True)

                st.markdown("---")
                st.markdown("#### 🚪 Rời Team")
                st.caption("Khi rời team, các công việc của team đang giao cho bạn sẽ trở về trạng thái chưa giao.")
                confirm_leave = st.checkbox("Tôi chắc chắn muốn rời team này")
                if st.button("🚪 RỜI TEAM", type="secondary", key="btn_leave_team", disabled=not confirm_leave):
                    remove_worker_from_team(my_id, leader_id)
                    st.success("Bạn đã rời team.")
                    st.rerun()

    # 4. CHỈNH SỬA / XÓA TẠM
    elif menu == "✏️ Chỉnh Sửa/Xóa" and current_role in ["Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>✏️ Chỉnh Sửa & Xóa Quản Lý</div>", unsafe_allow_html=True)
        
        btn_col1, btn_col2, btn_col_space = st.columns([1.5, 2, 2.5])
        is_edit_task = st.session_state["edit_sub_tab"] == "task"
        
        with btn_col1:
            st.button("🧰 Xóa Tạm Công Việc", type="primary" if is_edit_task else "secondary", key="btn_sub_edit_task", on_click=lambda: st.session_state.update({"edit_sub_tab": "task"}))
                
        with btn_col2:
            st.button("👤 Xóa Tạm Tài Khoản Người Dùng", type="primary" if not is_edit_task else "secondary", key="btn_sub_edit_user", on_click=lambda: st.session_state.update({"edit_sub_tab": "user"}))

        st.markdown("---")

        if st.session_state["edit_sub_tab"] == "task":
            tasks_df = pd.read_sql_query("SELECT id, task_id, task_name FROM tasks WHERE is_deleted = 0", conn)
            if tasks_df.empty:
                st.info("Hiện không có công việc nào để chỉnh sửa hoặc xóa.")
            else:
                task_list = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in tasks_df.iterrows()]
                selected_task_str = st.selectbox("Chọn công việc cần chuyển vào Thùng Rác:", task_list)
                selected_id = int(selected_task_str.split(" | ")[0])
                
                if st.button("🗑️ Chuyển Công Việc Vào Thùng Rác", type="secondary", key="btn_soft_delete_task"):
                    cursor.execute("UPDATE tasks SET is_deleted = 1 WHERE id = ?", (selected_id,))
                    conn.commit()
                    st.success("Đã chuyển công việc vào Thùng Rác thành công!")
                    st.rerun()

        else:
            users_df = pd.read_sql_query("SELECT id, username, fullname, role FROM users WHERE is_deleted = 0", conn)
            users_df = users_df[users_df['id'] != user_data['id']]
            users_df = users_df[users_df['role'] != "Admin"]
            if current_role == "WOS Manager":
                # WOS Manager không được khóa WOS Manager khác
                users_df = users_df[users_df['role'] != "WOS Manager"]
            elif current_role != "Admin":
                # Foreman chỉ được khóa Worker, Team Leader và tài khoản đang chờ duyệt
                users_df = users_df[users_df['role'].isin(["Worker", "Team Leader", "Pending"])]
            
            if users_df.empty:
                st.info("Không có tài khoản khác khả dụng để xóa.")
            else:
                user_list = [f"{row['id']} | @{row['username']} - {row['fullname']} ({row['role']})" for _, row in users_df.iterrows()]
                selected_user_str = st.selectbox("Chọn tài khoản muốn khóa/xóa tạm:", user_list)
                selected_user_id = int(selected_user_str.split(" | ")[0])
                
                if st.button("🗑️ Khóa/Xóa Tạm Tài Khoản Này", type="secondary", key="btn_soft_delete_user"):
                    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (selected_user_id,))
                    conn.commit()
                    delete_user_sessions(selected_user_id)
                    st.success("Đã khóa/chuyển tài khoản vào Thùng Rác thành công!")
                    st.rerun()

    # 5. QUẢN LÝ PHÂN QUYỀN
    #    - Admin: CHỈ cấp role WOS Manager và chọn workshop cho Manager
    #    - WOS Manager: cấp Worker / Team Leader / Foreman trong workshop của mình
    elif menu == "👥 Quản Lý Phân Quyền" and is_manager_up:
        st.markdown("<div class='big-table-title'>👥 Quản Lý & Cấp Quyền Tài Khoản (Role List)</div>", unsafe_allow_html=True)

        ws_df = pd.read_sql_query("SELECT code, COALESCE(name, '') AS name FROM custom_cost_codes WHERE is_deleted = 0 ORDER BY code", conn)
        ws_label = {row['code']: f"{row['code']} - {row['name']}" for _, row in ws_df.iterrows()}

        all_users = pd.read_sql_query("""
            SELECT u.id, u.username, u.fullname, u.role, u.workshop, u.leader_id, u.team_name,
                   COALESCE(l.team_name || ' (' || l.fullname || ')', l.fullname) AS leader_name
            FROM users u LEFT JOIN users l ON l.id = u.leader_id
            WHERE u.is_deleted = 0
        """, conn)
        all_users = all_users[(all_users['id'] != user_data['id']) & (all_users['role'] != "Admin")]

        if is_admin:
            visible_users = all_users
            st.info("🛡️ Admin chỉ cấp quyền **WOS Manager** và chọn **Workshop** mà Manager đó phụ trách. "
                    "Các role Worker / Team Leader / Foreman do WOS Manager cấp.")
        else:
            st.info("👑 Bạn có thể cấp **Worker / Team Leader / Foreman**, chọn **Workshop**, "
                    "và xếp Worker vào **team** của một Team Leader / Foreman.")
            visible_users = all_users[all_users['role'] != "WOS Manager"]

        show_df = visible_users.copy()
        show_df['workshop'] = show_df['workshop'].map(lambda c: ws_label.get(c, c) if c else "—")
        show_df['leader_name'] = show_df['leader_name'].fillna("—")
        show_df = show_df.rename(columns={'username': 'Username', 'fullname': 'Họ và Tên',
                                          'role': 'Vai Trò (Role)', 'workshop': 'Workshop',
                                          'leader_name': 'Team của'})
        st.dataframe(show_df.drop(columns=['id', 'leader_id', 'team_name']), use_container_width=True)

        # 🏭 QUẢN LÝ WORKSHOP ngay tại trang phân quyền (thêm workshop mới rồi chọn luôn cho tài khoản)
        with st.expander("🏭 Workshop: xem danh sách / thêm / xóa", expanded=ws_df.empty):
            ws_stats = pd.read_sql_query("""
                SELECT c.code AS 'Mã', COALESCE(c.name, '') AS 'Tên Workshop',
                       (SELECT COUNT(*) FROM users u WHERE u.workshop = c.code AND u.is_deleted = 0) AS 'Số tài khoản',
                       (SELECT COUNT(*) FROM tasks t WHERE t.task_cost_code = c.code AND t.is_deleted = 0) AS 'Số công việc'
                FROM custom_cost_codes c WHERE c.is_deleted = 0 ORDER BY c.code
            """, conn)
            if ws_stats.empty:
                st.info("Chưa có Workshop nào. Hãy thêm Workshop đầu tiên bên dưới.")
            else:
                st.dataframe(ws_stats, use_container_width=True, hide_index=True)

            st.markdown("#### ➕ Thêm Workshop Mới")
            wa1, wa2 = st.columns([1, 2])
            with wa1:
                new_ws_code = st.text_input("Mã Workshop (Ví dụ: WOS_07):", key="role_new_ws_code")
            with wa2:
                new_ws_name = st.text_input("Tên Workshop / Phòng ban:", key="role_new_ws_name")
            if st.button("➕ THÊM WORKSHOP", type="primary", key="btn_role_add_ws"):
                code_clean = new_ws_code.strip().upper().replace(" ", "_")
                name_clean = new_ws_name.strip()
                if not code_clean or not name_clean:
                    st.error("Vui lòng nhập cả Mã và Tên!")
                elif len(code_clean) > 20 or len(name_clean) > 80:
                    st.error("Mã tối đa 20 ký tự, tên tối đa 80 ký tự!")
                else:
                    ex = cursor.execute("SELECT is_deleted FROM custom_cost_codes WHERE code = ?", (code_clean,)).fetchone()
                    if ex and ex[0] == 0:
                        st.error(f"Mã **{code_clean}** đã có trong danh sách!")
                    else:
                        if ex:
                            cursor.execute("UPDATE custom_cost_codes SET name = ?, is_deleted = 0 WHERE code = ?", (name_clean, code_clean))
                        else:
                            cursor.execute("INSERT INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, '', 0)",
                                           (code_clean, name_clean))
                        conn.commit()
                        st.success(f"Đã thêm **{code_clean} - {name_clean}**!")
                        st.rerun()

            if not ws_stats.empty:
                st.markdown("#### 🗑️ Xóa Workshop")
                del_opts = {r['Mã']: f"{r['Mã']} - {r['Tên Workshop']}" for _, r in ws_stats.iterrows()}
                del_ws = st.selectbox("Chọn Workshop để xóa:", list(del_opts.keys()),
                                      format_func=lambda c: del_opts[c], key="role_del_ws")
                if st.button("🗑️ XÓA WORKSHOP", key="btn_role_del_ws"):
                    users_in_ws = cursor.execute("SELECT COUNT(*) FROM users WHERE workshop = ? AND is_deleted = 0", (del_ws,)).fetchone()[0]
                    if users_in_ws > 0:
                        st.error(f"Không thể xóa: còn **{users_in_ws}** tài khoản thuộc workshop này. "
                                 "Hãy chuyển họ sang workshop khác ở 👥 Quản Lý Phân Quyền trước.")
                    else:
                        cursor.execute("UPDATE custom_cost_codes SET is_deleted = 1 WHERE code = ?", (del_ws,))
                        conn.commit()
                        st.success(f"Đã xóa **{del_opts[del_ws]}** khỏi danh sách. Công việc cũ vẫn giữ nguyên.")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 🔄 Thay Đổi Quyền Hạn Cho Tài Khoản")

        if visible_users.empty:
            st.info("Không có tài khoản nào để cấp quyền.")
        else:
            user_roles_list = [f"{row['id']} | @{row['username']} - {row['fullname']} (Hiện tại: {row['role']})"
                               for _, row in visible_users.iterrows()]
            target_role_user = st.selectbox("Chọn tài khoản cần chuyển đổi Role:", user_roles_list)
            target_user_id = int(target_role_user.split(" | ")[0])

            if is_admin:
                if ws_df.empty:
                    st.warning("⚠️ Chưa có Workshop nào. Vào ➕ Thêm Công Việc → ⚙️ Thêm / Xóa trong danh sách để thêm.")
                else:
                    action = st.radio("Chọn thao tác:", ["👑 Cấp quyền WOS Manager", "⛔ Thu hồi quyền (về Pending)"], horizontal=True)
                    chosen_ws = None
                    if action.startswith("👑"):
                        chosen_ws = st.selectbox("Workshop mà Manager này phụ trách:", list(ws_label.keys()),
                                                 format_func=lambda c: ws_label[c])
                    if st.button("💾 LƯU THAY ĐỔI", type="primary", key="btn_save_role_admin"):
                        if chosen_ws:
                            cursor.execute("UPDATE users SET role = 'WOS Manager', workshop = ? WHERE id = ?", (chosen_ws, target_user_id))
                            msg = f"Đã cấp **WOS Manager** cho workshop **{ws_label[chosen_ws]}**!"
                        else:
                            cursor.execute("UPDATE users SET role = 'Pending' WHERE id = ?", (target_user_id,))
                            msg = "Đã thu hồi quyền, tài khoản trở về trạng thái Pending."
                        conn.commit()
                        delete_user_sessions(target_user_id)
                        st.success(msg)
                        st.rerun()
            else:
                target_row = visible_users[visible_users['id'] == target_user_id].iloc[0]
                role_choices = ["Worker", "Team Leader", "Foreman", "Pending"]
                cur_role = target_row['role'] if target_row['role'] in role_choices else "Worker"
                new_role = st.radio("Chọn Role Mới:", role_choices, index=role_choices.index(cur_role), horizontal=True)

                ws_keys = list(ws_label.keys())
                default_ws = target_row['workshop'] if target_row['workshop'] in ws_keys else user_data.get("workshop")
                new_ws = st.selectbox("Workshop:", ws_keys,
                                      index=ws_keys.index(default_ws) if default_ws in ws_keys else 0,
                                      format_func=lambda c: ws_label[c]) if ws_keys else None

                new_leader = None
                if new_role == "Worker":
                    leaders_in_ws = all_users[(all_users['role'].isin(LEADER_ROLES)) & (all_users['workshop'] == new_ws)]
                    leader_opts = {None: "— Chưa xếp team —"}
                    for _, r in leaders_in_ws.iterrows():
                        leader_opts[int(r['id'])] = f"{r['team_name'] + ' – ' if r['team_name'] else ''}{r['fullname']} ({r['role']})"
                    cur_ld = None if pd.isna(target_row['leader_id']) else int(target_row['leader_id'])
                    ld_keys = list(leader_opts.keys())
                    new_leader = st.selectbox("Thuộc team của (Team Leader / Foreman):", ld_keys,
                                              index=ld_keys.index(cur_ld) if cur_ld in ld_keys else 0,
                                              format_func=lambda k: leader_opts[k])
                    if len(leader_opts) == 1:
                        st.caption("Workshop này chưa có Team Leader / Foreman nào.")

                if st.button("💾 LƯU THAY ĐỔI ROLE", type="primary", key="btn_save_role"):
                    cursor.execute("UPDATE users SET role = ?, workshop = ?, leader_id = ? WHERE id = ?",
                                   (new_role, new_ws, new_leader, target_user_id))
                    if new_role not in LEADER_ROLES or new_ws != target_row['workshop']:
                        # Không còn là Leader (hoặc đổi workshop): giải tán team và trả công việc về trạng thái chưa giao
                        cursor.execute("UPDATE users SET team_name = NULL WHERE id = ?", (target_user_id,))
                        cursor.execute("UPDATE users SET leader_id = NULL WHERE leader_id = ?", (target_user_id,))
                        cursor.execute("UPDATE tasks SET assigned_leader_id = NULL, assigned_worker_id = NULL WHERE assigned_leader_id = ?",
                                       (target_user_id,))
                    if new_role != "Worker":
                        cursor.execute("UPDATE tasks SET assigned_worker_id = NULL WHERE assigned_worker_id = ?", (target_user_id,))
                    else:
                        # Worker đổi team: bỏ các việc không thuộc team mới
                        cursor.execute("""UPDATE tasks SET assigned_worker_id = NULL
                                          WHERE assigned_worker_id = ? AND (assigned_leader_id IS NULL OR assigned_leader_id != ?)""",
                                       (target_user_id, new_leader if new_leader else -1))
                    conn.commit()
                    st.success(f"Đã cập nhật: **{new_role}** – workshop **{ws_label.get(new_ws, '')}**!")
                    st.rerun()

    # 6. THÙNG RÁC TỔNG HỢP (CHỈ WOS MANAGER)
    elif menu == "🗑️ Thùng Rác" and is_manager_up:
        st.markdown("<div class='big-table-title'>🗑️ Thùng Rác & Khôi Phục Tổng Hợp</div>", unsafe_allow_html=True)
        
        t_col1, t_col3, t_space = st.columns([1.5, 1.5, 3])
        
        is_t_task = st.session_state["trash_sub_tab"] == "task"
        is_t_ws = st.session_state["trash_sub_tab"] == "ws"
        is_t_user = st.session_state["trash_sub_tab"] == "user"
        
        with t_col1:
            st.button("🧰 Thùng Rác Công Việc", type="primary" if is_t_task else "secondary", key="btn_t_task", on_click=lambda: st.session_state.update({"trash_sub_tab": "task"}))
                
        with t_col3:
            st.button("👤 Thùng Rác Tài Khoản", type="primary" if is_t_user else "secondary", key="btn_t_user", on_click=lambda: st.session_state.update({"trash_sub_tab": "user"}))

        st.markdown("---")

        if st.session_state["trash_sub_tab"] == "task":
            deleted_tasks = pd.read_sql_query("SELECT id, task_id, task_name, task_cost_code, initial_by FROM tasks WHERE is_deleted = 1", conn)
            if deleted_tasks.empty:
                st.info("Thùng rác công việc đang trống.")
            else:
                st.dataframe(deleted_tasks, use_container_width=True)
                task_del_options = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in deleted_tasks.iterrows()]
                restore_task_target = st.selectbox("Chọn công việc để xử lý:", task_del_options, key="sb_res_task")
                res_task_id = int(restore_task_target.split(" | ")[0])
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    if st.button("♻️ KHÔI PHỤC CÔNG VIỆC", type="primary", key="btn_res_task"):
                        cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE id = ?", (res_task_id,))
                        conn.commit()
                        st.success("Đã khôi phục công việc!")
                        st.rerun()
                with col_r2:
                    if st.button("💥 XÓA VĨNH VIỄN CÔNG VIỆC", type="secondary", key="btn_perm_del_task"):
                        cursor.execute("DELETE FROM tasks WHERE id = ?", (res_task_id,))
                        conn.commit()
                        st.warning("Đã xóa vĩnh viễn công việc!")
                        st.rerun()

        else:
            deleted_users = pd.read_sql_query("SELECT id, username, fullname, role FROM users WHERE is_deleted = 1", conn)
            if deleted_users.empty:
                st.info("Thùng rác tài khoản đang trống.")
            else:
                st.dataframe(deleted_users, use_container_width=True)
                user_res_options = [f"{row['id']} | @{row['username']} - {row['fullname']} ({row['role']})" for _, row in deleted_users.iterrows()]
                restore_user_target = st.selectbox("Chọn tài khoản để xử lý:", user_res_options, key="sb_res_user")
                res_user_id = int(restore_user_target.split(" | ")[0])
                
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    if st.button("♻️ MỞ KHÓA / KHÔI PHỤC TÀI KHOẢN", type="primary", key="btn_res_user"):
                        cursor.execute("UPDATE users SET is_deleted = 0 WHERE id = ?", (res_user_id,))
                        conn.commit()
                        st.success("Đã khôi phục tài khoản người dùng!")
                        st.rerun()
                with col_u2:
                    if st.button("💥 XÓA VĨNH VIỄN TÀI KHOẢN", type="secondary", key="btn_perm_del_user"):
                        cursor.execute("DELETE FROM users WHERE id = ?", (res_user_id,))
                        conn.commit()
                        delete_user_sessions(res_user_id)
                        st.warning("Đã xóa vĩnh viễn tài khoản khỏi cơ sở dữ liệu!")
                        st.rerun()

    # 7. BÁO CÁO & THỐNG KÊ
    elif menu == "📊 Báo Cáo & Khai Báo":
        st.markdown("<div class='big-table-title'>📊 Báo Cáo & Thống Kê Tiến Độ</div>", unsafe_allow_html=True)
        
        df_all = pd.read_sql_query("SELECT task_id, task_name, task_cost_code, block, in_charge_by, progress FROM tasks WHERE is_deleted = 0", conn)
        
        if df_all.empty:
            st.info("Chưa có dữ liệu công việc để tạo báo cáo. Vui lòng thêm công việc trước!")
        else:
            df_all['progress'] = pd.to_numeric(df_all['progress'], errors='coerce').fillna(0)
            
            total_tasks = len(df_all)
            completed_tasks = len(df_all[df_all['progress'] == 100])
            in_progress_tasks = len(df_all[(df_all['progress'] > 0) & (df_all['progress'] < 100)])
            avg_progress = round(df_all['progress'].mean(), 1)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tổng Số Công Việc", f"{total_tasks}")
            m2.metric("Đã Hoàn Thành (100%)", f"{completed_tasks}", f"{(completed_tasks/total_tasks*100):.1f}%")
            m3.metric("Đang Thực Hiện", f"{in_progress_tasks}")
            m4.metric("Tiến Độ Trung Bình", f"{avg_progress}%")
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### 📈 Phân Bố Tiến Độ Công Việc")
                progress_bins = pd.cut(df_all['progress'], bins=[-1, 0, 50, 99, 100], labels=[tr('Chưa bắt đầu (0%)'), tr('Đang làm (1-50%)'), tr('Sắp xong (51-99%)'), tr('Hoàn thành (100%)')])
                progress_dist = progress_bins.value_counts().reset_index()
                _c_status, _c_count = tr('Trạng Thái'), tr('Số Lượng')
                progress_dist.columns = [_c_status, _c_count]
                
                chart = alt.Chart(progress_dist).mark_bar(color='#3b82f6').encode(
                    x=alt.X(f'{_c_status}:N', axis=alt.Axis(labelAngle=0, labelFontSize=12, title=_c_status)),
                    y=alt.Y(f'{_c_count}:Q', axis=alt.Axis(title=tr("Số Lượng Công Việc"), tickMinStep=1, format='d')),
                    tooltip=[_c_status, _c_count]
                ).properties(height=350)
                
                st.altair_chart(chart, use_container_width=True)

            with col_chart2:
                st.markdown("### 🏭 Thống Kê Theo Workshop")
                ws_stats = df_all.groupby('task_cost_code').agg(
                    Tổng_CV=('task_id', 'count'),
                    Tiến_Độ_TB=('progress', 'mean')
                ).reset_index()
                ws_stats['Tiến_Độ_TB'] = ws_stats['Tiến_Độ_TB'].round(1)
                ws_stats.columns = ['WS Cost Code', 'Tổng Công Việc', 'Tiến Độ Trung Bình (%)']
                st.dataframe(ws_stats, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📥 Tải Báo Cáo Dữ Liệu")
            
            csv_data = df_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải Báo Cáo Bảng Công Việc (File CSV/Excel)",
                data=csv_data,
                file_name=f"ShipControl_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )

    # 8. ĐỔI MẬT KHẨU (MỌI ROLE)
    elif menu == "🔑 Đổi Mật Khẩu":
        st.markdown("<div class='big-table-title'>🔑 Đổi Mật Khẩu</div>", unsafe_allow_html=True)
        with st.form("change_password_form", clear_on_submit=True):
            old_pw = st.text_input("Mật khẩu hiện tại:", type="password")
            new_pw = st.text_input("Mật khẩu mới (ít nhất 8 ký tự):", type="password")
            new_pw2 = st.text_input("Nhập lại mật khẩu mới:", type="password")
            btn_change_pw = st.form_submit_button("💾 ĐỔI MẬT KHẨU")
            if btn_change_pw:
                row = cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],)).fetchone()
                if not row or not verify_password(old_pw, row[0]):
                    st.error("Mật khẩu hiện tại không đúng!")
                elif len(new_pw) < 8:
                    st.error("Mật khẩu mới phải có ít nhất 8 ký tự!")
                elif new_pw != new_pw2:
                    st.error("Mật khẩu xác nhận không trùng khớp!")
                elif new_pw == "admin123":
                    st.error("Không được dùng lại mật khẩu mặc định!")
                else:
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_pw), user_data['id']))
                    conn.commit()
                    # Đăng xuất mọi thiết bị khác
                    cursor.execute("DELETE FROM sessions WHERE user_id = ? AND token != ?",
                                   (user_data['id'], st.session_state.get("session_token", "")))
                    conn.commit()
                    st.success("✅ Đã đổi mật khẩu thành công! Các thiết bị khác đã bị đăng xuất.")

    # 9. 💬 TIN NHẮN: kênh chung + nhóm chat tự tạo + nhắn riêng (bấm vào tên tài khoản)
    elif menu == CHAT_MENU:
        st.session_state.setdefault("chat_conv", "general")
        if str(st.session_state["chat_conv"]).startswith("dm:"):
            st.session_state["chat_conv"] = "general"

        def _open_conv(conv):
            st.session_state["chat_conv"] = conv

        @st.fragment(run_every=3)
        def _chat_room():
            me = user_data["id"]
            conv = st.session_state.get("chat_conv", "general")
            all_people = cursor.execute("""
                SELECT id, username, fullname, role FROM users
                WHERE is_deleted = 0 AND id != ? AND role IS NOT NULL AND role != 'Pending'
                ORDER BY fullname COLLATE NOCASE
            """, (me,)).fetchall()
            people_label = {p[0]: f"{CHAT_ROLE_ICONS.get(p[3], '👤')} {p[2] or p[1]} (@{p[1]})" for p in all_people}

            col_list, col_chat = st.columns([1, 2.2], gap="medium")

            # ---------- Cột trái: Kênh chung + Nhóm chat (không còn nhắn riêng từng người) ----------
            with col_list:
                # ➕ Tạo nhóm chat: đặt tên + chọn người
                with st.expander("➕ Tạo nhóm chat"):
                    g_name = st.text_input("Tên nhóm", key="chat_new_group_name", placeholder="Ví dụ: Tổ hàn Block 170")
                    g_members = st.multiselect("Thêm người vào nhóm", list(people_label.keys()), placeholder="Chọn người...",
                                               format_func=lambda i: people_label[i], key="chat_new_group_members")
                    if st.button("✨ TẠO NHÓM", key="chat_create_group", type="primary", use_container_width=True):
                        if not g_name.strip():
                            st.error("Vui lòng đặt tên nhóm!")
                        elif not g_members:
                            st.error("Hãy chọn ít nhất 1 người!")
                        else:
                            new_gid = create_chat_group(g_name.strip()[:60], me, g_members)
                            conv = f"group:{new_gid}"
                            st.session_state["chat_conv"] = conv
                            st.success(f"Đã tạo nhóm **{g_name.strip()[:60]}**!")

                unread = chat_unread_by_conv(me)
                unread.pop(conv, None)        # cuộc đang mở thì coi như đã đọc
                g_badge = f"  🔴 {unread['general']}" if unread.get("general") else ""
                st.button("📢 Kênh chung" + g_badge, key="chat_open_general", use_container_width=True,
                          type="primary" if conv == "general" else "secondary",
                          on_click=_open_conv, args=("general",))

                my_groups = user_chat_groups(me)
                if my_groups:
                    st.markdown("#### 💬 Nhóm chat")
                    for gid, gname, gowner, gcount in my_groups:
                        c_id = f"group:{gid}"
                        badge = f"  🔴 {unread[c_id]}" if unread.get(c_id) else ""
                        st.button(f"💬 {gname} · {gcount}{badge}", key=f"chat_open_g{gid}", use_container_width=True,
                                  type="primary" if conv == c_id else "secondary",
                                  on_click=_open_conv, args=(c_id,))


            # ---------- Cột phải: khung trò chuyện ----------
            with col_chat:
                if conv.startswith("group:"):
                    gid = int(conv.split(":")[1])
                    group = cursor.execute("SELECT id, name, created_by FROM chat_groups WHERE id = ?", (gid,)).fetchone()
                    if not group or not is_group_member(gid, me):
                        conv = "general"
                        st.session_state["chat_conv"] = "general"
                if conv.startswith("group:"):
                    is_owner = (group[2] == me)
                    members = group_members(gid)
                    st.markdown(f"### 💬 {html.escape(group[1])}")
                    owner_row = next((m for m in members if m[0] == group[2]), None)
                    if owner_row:
                        st.caption("👑 Quản trị nhóm" + f": {owner_row[2] or owner_row[1]}")
                    st.caption(" · ".join(f"{CHAT_ROLE_ICONS.get(r, '👤')} {n or u}" for _, u, n, r in members))
                    with st.expander("⚙️ Thành viên nhóm"):
                        if is_owner:
                            outsiders = [p for p in all_people if p[0] not in {m[0] for m in members}]
                            add_ids = st.multiselect("Thêm người vào nhóm", [p[0] for p in outsiders], placeholder="Chọn người...",
                                                     format_func=lambda i: people_label[i], key=f"chat_add_{gid}")
                            if st.button("➕ THÊM VÀO NHÓM", key=f"chat_add_btn_{gid}"):
                                if add_ids:
                                    for uid in add_ids:
                                        cursor.execute("INSERT OR IGNORE INTO chat_group_members (group_id, user_id) VALUES (?, ?)", (gid, uid))
                                    st.success(f"Đã thêm {len(add_ids)} người vào nhóm!")
                            others = [m for m in members if m[0] != me]
                            if others:
                                rm_id = st.selectbox("Xóa khỏi nhóm", [m[0] for m in others],
                                                     format_func=lambda i: next(f"{n or u} (@{u})" for x, u, n, r in others if x == i),
                                                     key=f"chat_rm_{gid}")
                                if st.button("➖ XÓA KHỎI NHÓM", key=f"chat_rm_btn_{gid}"):
                                    cursor.execute("DELETE FROM chat_group_members WHERE group_id = ? AND user_id = ?", (gid, rm_id))
                                    st.success("Đã xóa khỏi nhóm.")
                            if st.button("🗑️ XÓA NHÓM", key=f"chat_del_group_{gid}"):
                                delete_chat_group(gid)
                                conv = "general"
                                st.session_state["chat_conv"] = "general"
                        else:
                            st.caption("Chỉ người tạo nhóm mới thêm / xóa được thành viên.")
                        if conv.startswith("group:") and st.button("🚪 RỜI NHÓM", key=f"chat_leave_{gid}"):
                            leave_chat_group(gid, me)
                            conv = "general"
                            st.session_state["chat_conv"] = "general"
                    if not conv.startswith("group:"):
                        st.markdown("### 📢 Kênh chung")
                elif conv == "general":
                    st.markdown("### 📢 Kênh chung")
                    st.caption("Mọi người trong app đều thấy kênh này.")
                else:                                  # nhắn riêng đã bỏ → quay về kênh chung
                    conv = "general"
                    st.session_state["chat_conv"] = "general"
                    st.markdown("### 📢 Kênh chung")
                    st.caption("Mọi người trong app đều thấy kênh này.")

                # Chỗ hiện tin nhắn được giữ trước; ô nhập nằm dưới. Gửi xong thì tin mới hiện ngay.
                msg_box = st.container()
                new_msg = st.chat_input("Nhập tin nhắn...", key=f"chat_input_{conv}")
                if new_msg and new_msg.strip():
                    post_chat_message(conv, me, new_msg)

                msgs = cursor.execute("""
                    SELECT m.id, m.sender_id, m.body, m.created_at, u.fullname, u.username, u.role
                    FROM chat_messages m LEFT JOIN users u ON u.id = m.sender_id
                    WHERE m.conv = ? ORDER BY m.id DESC LIMIT 200
                """, (conv,)).fetchall()
                with msg_box:
                    render_chat_messages(msgs, me)
                if msgs:
                    mark_chat_read(me, conv, msgs[0][0])

                # 🗑️ Chỉ QUẢN TRỊ của cuộc trò chuyện mới xóa được tin nhắn:
                #    nhóm chat → người tạo nhóm; kênh chung → Admin / WOS Manager
                if is_chat_admin(conv, me, current_role):
                    with st.expander("🗑️ Xóa tin nhắn (quản trị)"):
                        if not msgs:
                            st.caption("Chưa có tin nhắn để xóa.")
                        else:
                            def _msg_label(mid):
                                m = next(x for x in msgs if x[0] == mid)
                                who = m[4] or m[5] or "?"
                                body = (m[2] or "").replace("\n", " ")
                                return f"{_chat_time(m[3])} · {who}: {body[:60]}{'…' if len(body) > 60 else ''}"
                            del_id = st.selectbox("Chọn tin nhắn để xóa", [m[0] for m in msgs],
                                                  format_func=_msg_label, key=f"chat_del_pick_{conv}")
                            if st.button("🗑️ XÓA TIN NHẮN", key="chat_del_msg_btn"):
                                cursor.execute("DELETE FROM chat_messages WHERE id = ? AND conv = ?", (del_id, conv))
                                st.success("Đã xóa tin nhắn.")
                                st.rerun()
                            st.markdown("---")
                            sure = st.checkbox("Tôi chắc chắn muốn xóa toàn bộ tin nhắn", key=f"chat_clear_ok_{conv}")
                            if st.button("🧹 XÓA TOÀN BỘ TIN NHẮN", key="chat_clear_btn", disabled=not sure):
                                cursor.execute("DELETE FROM chat_messages WHERE conv = ?", (conv,))
                                st.success("Đã xóa toàn bộ tin nhắn.")
                                st.rerun()

        _chat_room()

    # 10. 🎥 HỌP ONLINE: Foreman / Team Leader tạo phòng họp có ID + mật khẩu; ai cũng vào được nếu có mã
    elif menu == MEETING_MENU:
        me = user_data["id"]
        can_host = current_role in MEETING_HOST_ROLES
        my_name = user_data.get("fullname") or user_data["username"]

        # ---------- 📨 Lời mời họp (vào thẳng, không cần gõ mã) ----------
        invites = cursor.execute("""
            SELECT m.id, m.room_id, m.password, m.title, m.video_room, m.start_at, u.fullname, u.username
            FROM meeting_invites i JOIN meetings m ON m.id = i.meeting_id
            LEFT JOIN users u ON u.id = m.host_id
            WHERE i.user_id = ? AND m.is_active = 1 ORDER BY m.start_at
        """, (me,)).fetchall()
        if invites:
            st.markdown("### 📨 Lời mời họp của bạn")
            for mid, rid, pw, ttl, vroom, start_at, hname, huser in invites:
                with st.container(border=True):
                    ic1, ic2 = st.columns([2, 1], vertical_alignment="center")
                    with ic1:
                        when = datetime.fromisoformat(start_at).strftime("%d/%m/%Y %H:%M") if start_at else ""
                        st.markdown(f"**🎥 {html.escape(ttl)}**  \n🕒 {when} · " + "Chủ phòng" + f": {html.escape(hname or huser or '')}")
                        st.markdown(meeting_code_card(rid, pw, compact=True), unsafe_allow_html=True)
                    with ic2:
                        st.link_button("🎥 VÀO HỌP", meeting_url(vroom, my_name), type="primary", use_container_width=True)
            st.markdown("---")

        # ---------- 🔑 Vào cuộc họp ----------
        st.markdown("### 🔑 Vào cuộc họp")
        jc1, jc2, jc3 = st.columns([1.2, 1, 0.9], vertical_alignment="bottom")
        with jc1:
            j_room = st.text_input("ID phòng họp", key="meet_join_room", placeholder="123 456 789")
        with jc2:
            j_pass = st.text_input("Mật khẩu phòng", key="meet_join_pass", type="password")
        with jc3:
            do_join = st.button("🎥 VÀO PHÒNG", key="meet_join_btn", type="primary", use_container_width=True)
        if do_join:
            st.session_state["meet_attempts"] = st.session_state.get("meet_attempts", 0) + 1
            if st.session_state["meet_attempts"] > 15:
                st.error("Bạn đã nhập sai quá nhiều lần. Hãy tải lại trang và thử lại sau.")
            else:
                mt = find_meeting(j_room, j_pass)
                if mt:
                    st.session_state["meet_joined"] = mt[0]
                    st.session_state["meet_attempts"] = 0
                else:
                    st.session_state.pop("meet_joined", None)
                    st.error("Sai ID phòng hoặc mật khẩu, hoặc cuộc họp đã kết thúc!")
        joined = st.session_state.get("meet_joined")
        if joined:
            mt = cursor.execute("""SELECT m.title, m.video_room, m.start_at, u.fullname, u.username
                                   FROM meetings m LEFT JOIN users u ON u.id = m.host_id
                                   WHERE m.id = ? AND m.is_active = 1""", (joined,)).fetchone()
            if mt:
                st.success(f"✅ Đúng mã phòng: **{mt[0]}** · " + "Chủ phòng" + f": {mt[3] or mt[4]}")
                st.link_button("🎥 MỞ PHÒNG HỌP (camera + micro)", meeting_url(mt[1], my_name), type="primary")
                st.caption("Phòng họp mở trong tab mới. Lần đầu, trình duyệt sẽ hỏi quyền dùng camera và micro — hãy bấm Cho phép.")

        # ---------- ➕ Tạo cuộc họp (Foreman / Team Leader) ----------
        if can_host:
            st.markdown("---")
            st.markdown("### ➕ Tạo cuộc họp mới")
            people = cursor.execute("""
                SELECT id, username, fullname, role FROM users
                WHERE is_deleted = 0 AND id != ? AND role IS NOT NULL AND role != 'Pending'
                ORDER BY fullname COLLATE NOCASE
            """, (me,)).fetchall()
            p_label = {p[0]: f"{CHAT_ROLE_ICONS.get(p[3], '👤')} {p[2] or p[1]} (@{p[1]})" for p in people}
            with st.form("meet_create_form", clear_on_submit=True):
                m_title = st.text_input("Tên cuộc họp *", placeholder="Ví dụ: Họp giao ca sáng")
                mc1, mc2 = st.columns(2)
                with mc1:
                    m_date = st.date_input("Ngày họp", value=date.today())
                with mc2:
                    m_time = st.time_input("Giờ họp", value=(datetime.now() + timedelta(minutes=5)).time().replace(second=0, microsecond=0))
                m_invite = st.multiselect("Mời người (họ sẽ thấy lời mời trong 🎥 Họp Online)", list(p_label.keys()), placeholder="Chọn người...",
                                          format_func=lambda i: p_label[i])
                m_post_general = st.checkbox("📢 Thông báo vào Kênh chung", value=False)
                if st.form_submit_button("🎥 TẠO CUỘC HỌP"):
                    if not m_title.strip():
                        st.error("Vui lòng nhập tên cuộc họp!")
                    else:
                        start_at = datetime.combine(m_date, m_time).isoformat(timespec="minutes")
                        room_id, password = create_meeting(m_title.strip()[:80], me, start_at)
                        invite = (tr("🎥 Mời họp") + f": {m_title.strip()[:80]}\n"
                                  + tr("🕒 Thời gian") + f": {datetime.fromisoformat(start_at).strftime('%d/%m/%Y %H:%M')}\n"
                                  + tr("🔢 ID phòng") + f": {format_room_id(room_id)}\n"
                                  + tr("🔑 Mật khẩu") + f": {password}\n"
                                  + tr("👉 Vào mục 🎥 Họp Online để tham gia."))
                        new_mid = cursor.execute("SELECT id FROM meetings WHERE room_id = ?", (room_id,)).fetchone()[0]
                        for uid in m_invite:
                            cursor.execute("INSERT OR IGNORE INTO meeting_invites (meeting_id, user_id) VALUES (?, ?)", (new_mid, uid))
                        if m_post_general:
                            post_chat_message("general", me, invite)
                        st.session_state["meet_just_created"] = (room_id, password, m_title.strip()[:80])
            if st.session_state.get("meet_just_created"):
                rid, pw, ttl = st.session_state.pop("meet_just_created")
                st.success(f"🎉 Đã tạo cuộc họp **{ttl}**!")
                st.markdown(meeting_code_card(rid, pw), unsafe_allow_html=True)

            # ---------- 📋 Cuộc họp của tôi ----------
            st.markdown("---")
            st.markdown("### 📋 Cuộc họp của tôi")
            mine = cursor.execute("""SELECT id, room_id, password, title, video_room, start_at FROM meetings
                                     WHERE host_id = ? AND is_active = 1 ORDER BY start_at DESC""", (me,)).fetchall()
            if not mine:
                st.info("Bạn chưa có cuộc họp nào.")
            for mid, rid, pw, ttl, vroom, start_at in mine:
                with st.container(border=True):
                    cc1, cc2 = st.columns([2, 1], vertical_alignment="center")
                    with cc1:
                        when = datetime.fromisoformat(start_at).strftime("%d/%m/%Y %H:%M") if start_at else ""
                        st.markdown(f"**🎥 {html.escape(ttl)}**  \n🕒 {when}")
                        st.markdown(meeting_code_card(rid, pw, compact=True), unsafe_allow_html=True)
                    with cc2:
                        st.link_button("▶️ BẮT ĐẦU", meeting_url(vroom, my_name), type="primary", use_container_width=True)
                        if st.button("⛔ KẾT THÚC", key=f"meet_end_{mid}", use_container_width=True):
                            cursor.execute("UPDATE meetings SET is_active = 0 WHERE id = ? AND host_id = ?", (mid, me))
                            st.rerun()
        else:
            st.caption("Chỉ Foreman và Team Leader mới tạo được cuộc họp. Bạn có thể vào họp khi có ID phòng và mật khẩu.")
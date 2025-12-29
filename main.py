"""
メインアプリケーション
Streamlitアプリのエントリーポイント
"""

import streamlit as st
from initialize import initialize_app
from components import (
    show_children_profile_page,
    show_diary_page,
    show_advice_page,
    show_sidebar
)
from constants import APP_TITLE, APP_ICON


def main():
    """メイン処理"""
    # ページ設定
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初期化処理
    initialize_app()
    
    # タイトル
    st.title(APP_TITLE)
    
    # サイドバー表示とページ選択
    selected_page = show_sidebar()
    
    # ページごとの表示
    if selected_page == "👶 プロフィール管理":
        show_children_profile_page()
    
    elif selected_page == "📔 育児日記":
        show_diary_page()
    
    elif selected_page == "💬 育児相談":
        show_advice_page()


if __name__ == "__main__":
    main()

"""
画面表示コンポーネント
Streamlitの各画面やUIコンポーネントを定義
"""

import streamlit as st
from datetime import date, datetime
from typing import List, Dict

import utils


def show_children_profile_page():
    """子どもプロフィール管理画面"""
    st.header("👶 子どもプロフィール管理")
    
    children = utils.load_children()
    
    # 子ども一覧表示
    if children:
        st.subheader("登録済みの子ども")
        
        for child in children:
            with st.expander(f"👤 {child['name']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**名前:** {child['name']}")
                    st.write(f"**生年月日:** {child['birth_date']}")
                    
                    age_months = utils.calculate_age_months(child['birth_date'])
                    age_display = utils.format_age_display(age_months)
                    st.write(f"**年齢:** {age_display} ({age_months}ヶ月)")
                    
                    st.write(f"**メモ:** {child.get('notes', '')}")
                
                with col2:
                    if st.button("✏️ 編集", key=f"edit_{child['child_id']}"):
                        st.session_state.editing_child_id = child['child_id']
                    
                    if st.button("🗑️ 削除", key=f"delete_{child['child_id']}"):
                        utils.delete_child(child['child_id'])
                        st.rerun()
    else:
        st.info("まだ子どもが登録されていません。下のフォームから追加してください。")
    
    st.divider()
    
    # 編集フォーム
    if hasattr(st.session_state, 'editing_child_id'):
        editing_child = utils.get_child_by_id(st.session_state.editing_child_id)
        if editing_child:
            st.subheader("✏️ 子ども情報を編集")
            
            with st.form("edit_child_form"):
                name = st.text_input("名前", value=editing_child['name'])
                birth_date = st.date_input(
                    "生年月日",
                    value=datetime.strptime(editing_child['birth_date'], "%Y-%m-%d").date()
                )
                notes = st.text_area("メモ（性格など）", value=editing_child.get('notes', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("更新", use_container_width=True)
                with col2:
                    canceled = st.form_submit_button("キャンセル", use_container_width=True)
                
                if submitted:
                    utils.update_child(
                        st.session_state.editing_child_id,
                        name,
                        birth_date.strftime("%Y-%m-%d"),
                        notes
                    )
                    del st.session_state.editing_child_id
                    st.success("更新しました！")
                    st.rerun()
                
                if canceled:
                    del st.session_state.editing_child_id
                    st.rerun()
    
    # 新規追加フォーム
    else:
        st.subheader("➕ 新しい子どもを追加")
        
        with st.form("add_child_form"):
            name = st.text_input("名前")
            birth_date = st.date_input("生年月日", value=date.today())
            notes = st.text_area("メモ（性格など）")
            
            submitted = st.form_submit_button("追加", use_container_width=True)
            
            if submitted:
                if name:
                    utils.add_child(name, birth_date.strftime("%Y-%m-%d"), notes)
                    st.success(f"{name}を追加しました！")
                    st.rerun()
                else:
                    st.error("名前を入力してください。")


def show_diary_page():
    """日記管理画面"""
    st.header("📔 育児日記")
    
    children = utils.load_children()
    
    if not children:
        st.warning("まず子どもを登録してください。")
        return
    
    # タブで新規作成と一覧を分ける
    tab1, tab2 = st.tabs(["✍️ 日記を書く", "📚 日記一覧"])
    
    with tab1:
        show_diary_form(children)
    
    with tab2:
        show_diary_list(children)


def show_diary_form(children: List[Dict]):
    """日記作成フォーム"""
    st.subheader("新しい日記")
    
    with st.form("add_diary_form"):
        # 複数選択可能な子どもリスト
        child_options = {child['name']: child['child_id'] for child in children}
        selected_children = st.multiselect(
            "対象の子ども",
            options=list(child_options.keys()),
            default=list(child_options.keys())[0] if child_options else None
        )
        
        diary_date = st.date_input("日付", value=date.today())
        content = st.text_area("日記の内容", height=200)
        
        submitted = st.form_submit_button("保存", use_container_width=True)
        
        if submitted:
            if selected_children and content:
                child_ids = [child_options[name] for name in selected_children]
                utils.add_diary(child_ids, diary_date.strftime("%Y-%m-%d"), content)
                st.success("日記を保存しました！")
                st.rerun()
            else:
                st.error("対象の子どもと内容を入力してください。")


def show_diary_list(children: List[Dict]):
    """日記一覧表示"""
    st.subheader("日記一覧")
    
    diaries = utils.load_diaries()
    
    if not diaries:
        st.info("まだ日記が登録されていません。")
        return
    
    # 日付順にソート（新しい順）
    diaries_sorted = sorted(diaries, key=lambda x: x['date'], reverse=True)
    
    for diary in diaries_sorted:
        # 子どもの名前を取得
        child_names = []
        for child_id in diary['child_ids']:
            child = utils.get_child_by_id(child_id)
            if child:
                child_names.append(child['name'])
        
        with st.expander(f"📅 {diary['date']} - {', '.join(child_names)}"):
            st.write(diary['content'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ 編集", key=f"edit_diary_{diary['diary_id']}"):
                    st.session_state.editing_diary_id = diary['diary_id']
                    st.rerun()
            
            with col2:
                if st.button("🗑️ 削除", key=f"delete_diary_{diary['diary_id']}"):
                    utils.delete_diary(diary['diary_id'])
                    st.success("削除しました！")
                    st.rerun()


def show_advice_page():
    """相談・アドバイス画面"""
    st.header("💬 育児相談")
    
    children = utils.load_children()
    
    if not children:
        st.warning("まず子どもを登録してください。")
        return
    
    # 子ども選択
    child_options = {child['name']: child['child_id'] for child in children}
    selected_child_name = st.selectbox("相談する子ども", options=list(child_options.keys()))
    selected_child_id = child_options[selected_child_name]
    
    # 子ども情報表示
    child = utils.get_child_by_id(selected_child_id)
    if child:
        age_months = utils.calculate_age_months(child['birth_date'])
        age_display = utils.format_age_display(age_months)
        st.info(f"👤 {child['name']} ({age_display})")
    
    st.divider()
    
    # 相談入力
    question = st.text_area(
        "困りごとや相談したいことを自由に入力してください",
        height=150,
        placeholder="例：最近、夜泣きがひどくて困っています..."
    )
    
    if st.button("💡 アドバイスをもらう", use_container_width=True, type="primary"):
        if question:
            with st.spinner("アドバイスを生成中..."):
                advice = utils.generate_advice(question, selected_child_id)
                
                st.success("アドバイス")
                st.write(advice)
        else:
            st.error("相談内容を入力してください。")
    
    st.divider()
    
    # 過去の日記表示
    st.subheader("📚 関連する過去の日記")
    child_diaries = utils.get_diaries_by_child(selected_child_id)
    
    if child_diaries:
        # 新しい順に表示
        child_diaries_sorted = sorted(child_diaries, key=lambda x: x['date'], reverse=True)
        
        for diary in child_diaries_sorted[:5]:  # 最新5件のみ表示
            with st.expander(f"📅 {diary['date']}"):
                st.write(diary['content'])
    else:
        st.info("まだ日記が登録されていません。")


def show_sidebar():
    """サイドバー表示"""
    with st.sidebar:
        st.title("🍼 メニュー")
        
        # ページ選択
        page = st.radio(
            "ページを選択",
            ["📔 育児日記", "💬 育児相談", "👶 プロフィール管理"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 統計情報
        children = utils.load_children()
        diaries = utils.load_diaries()
        
        st.subheader("📊 統計")
        st.metric("登録されている子ども", f"{len(children)}人")
        st.metric("記録された日記", f"{len(diaries)}件")
        
        return page
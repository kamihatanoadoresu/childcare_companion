"""
ユーティリティ関数
データ操作、Embedding、RAG、LLM呼び出しなどの機能を提供
"""

import os
import json
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

from constants import (
    CHILDREN_FILE,
    DIARIES_FILE,
    EMBEDDINGS_INDEX_FILE,
    EMBEDDINGS_METADATA_FILE,
    EMBEDDING_MODEL,
    CHAT_MODEL,
    SYSTEM_PROMPT,
    ADVICE_PROMPT_TEMPLATE,
    RAG_TOP_K,
)

# 環境変数の読み込み
load_dotenv()

# OpenAIクライアントの初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ===========================================
# データ操作関数
# ===========================================

def load_children() -> List[Dict]:
    """子どもデータを読み込み"""
    with open(CHILDREN_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_children(children: List[Dict]):
    """子どもデータを保存"""
    with open(CHILDREN_FILE, 'w', encoding='utf-8') as f:
        json.dump(children, f, ensure_ascii=False, indent=2)


def load_diaries() -> List[Dict]:
    """日記データを読み込み"""
    with open(DIARIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_diaries(diaries: List[Dict]):
    """日記データを保存"""
    with open(DIARIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(diaries, f, ensure_ascii=False, indent=2)


def load_embeddings_metadata() -> List[Dict]:
    """Embeddingメタデータを読み込み"""
    if os.path.exists(EMBEDDINGS_METADATA_FILE):
        with open(EMBEDDINGS_METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_embeddings_metadata(metadata: List[Dict]):
    """Embeddingメタデータを保存"""
    with open(EMBEDDINGS_METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


# ===========================================
# 子ども関連の関数
# ===========================================

def calculate_age_months(birth_date_str: str) -> int:
    """生年月日から月齢を計算"""
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
    today = date.today()
    
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    
    # 日付が誕生日前なら1ヶ月引く
    if today.day < birth_date.day:
        months -= 1
    
    return max(0, months)


def format_age_display(months: int) -> str:
    """月齢を「◯歳◯ヶ月」形式で表示"""
    years = months // 12
    remaining_months = months % 12
    
    if years == 0:
        return f"{remaining_months}ヶ月"
    elif remaining_months == 0:
        return f"{years}歳"
    else:
        return f"{years}歳{remaining_months}ヶ月"


def add_child(name: str, birth_date: str, notes: str = "") -> Dict:
    """子どもを追加"""
    children = load_children()
    
    child = {
        "child_id": str(uuid.uuid4()),
        "name": name,
        "birth_date": birth_date,
        "notes": notes
    }
    
    children.append(child)
    save_children(children)
    
    return child


def update_child(child_id: str, name: str, birth_date: str, notes: str):
    """子ども情報を更新"""
    children = load_children()
    
    for child in children:
        if child["child_id"] == child_id:
            child["name"] = name
            child["birth_date"] = birth_date
            child["notes"] = notes
            break
    
    save_children(children)


def delete_child(child_id: str):
    """子どもを削除"""
    children = load_children()
    children = [c for c in children if c["child_id"] != child_id]
    save_children(children)
    
    # 関連する日記も削除
    diaries = load_diaries()
    diaries = [d for d in diaries if child_id not in d.get("child_ids", [])]
    save_diaries(diaries)


def get_child_by_id(child_id: str) -> Optional[Dict]:
    """IDから子ども情報を取得"""
    children = load_children()
    for child in children:
        if child["child_id"] == child_id:
            return child
    return None


# ===========================================
# 日記関連の関数
# ===========================================

def add_diary(child_ids: List[str], date_str: str, content: str) -> Dict:
    """日記を追加"""
    diaries = load_diaries()
    
    diary = {
        "diary_id": str(uuid.uuid4()),
        "child_ids": child_ids,
        "date": date_str,
        "content": content
    }
    
    diaries.append(diary)
    save_diaries(diaries)
    
    # Embeddingを生成
    update_diary_embedding(diary["diary_id"], content)
    
    return diary


def update_diary(diary_id: str, child_ids: List[str], date_str: str, content: str):
    """日記を更新"""
    diaries = load_diaries()
    
    for diary in diaries:
        if diary["diary_id"] == diary_id:
            diary["child_ids"] = child_ids
            diary["date"] = date_str
            diary["content"] = content
            break
    
    save_diaries(diaries)
    
    # Embeddingを更新
    update_diary_embedding(diary_id, content)


def delete_diary(diary_id: str):
    """日記を削除"""
    diaries = load_diaries()
    diaries = [d for d in diaries if d["diary_id"] != diary_id]
    save_diaries(diaries)
    
    # Embeddingメタデータも削除
    metadata = load_embeddings_metadata()
    metadata = [m for m in metadata if m["diary_id"] != diary_id]
    save_embeddings_metadata(metadata)
    
    # FAISSインデックスを再構築
    rebuild_faiss_index()


def get_diaries_by_child(child_id: str) -> List[Dict]:
    """特定の子どもの日記を取得"""
    diaries = load_diaries()
    return [d for d in diaries if child_id in d.get("child_ids", [])]


# ===========================================
# Embedding関連の関数
# ===========================================

def create_embedding(text: str) -> List[float]:
    """テキストからEmbeddingを生成"""
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding生成エラー: {e}")
        return []


def update_diary_embedding(diary_id: str, content: str):
    """日記のEmbeddingを更新"""
    embedding = create_embedding(content)
    
    if not embedding:
        return
    
    metadata = load_embeddings_metadata()
    
    # 既存のEmbeddingを更新または追加
    found = False
    for item in metadata:
        if item["diary_id"] == diary_id:
            item["embedding"] = embedding
            found = True
            break
    
    if not found:
        metadata.append({
            "diary_id": diary_id,
            "embedding": embedding
        })
    
    save_embeddings_metadata(metadata)
    rebuild_faiss_index()


def rebuild_faiss_index():
    """FAISSインデックスを再構築"""
    try:
        import faiss
        
        metadata = load_embeddings_metadata()
        
        if not metadata:
            return
        
        embeddings = np.array([item["embedding"] for item in metadata], dtype='float32')
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        faiss.write_index(index, EMBEDDINGS_INDEX_FILE)
    except Exception as e:
        print(f"FAISSインデックス再構築エラー: {e}")


def search_similar_diaries(query: str, child_id: str, top_k: int = RAG_TOP_K) -> List[Dict]:
    """類似する日記を検索"""
    try:
        import faiss
        
        # クエリのEmbeddingを生成
        query_embedding = create_embedding(query)
        if not query_embedding:
            return []
        
        # メタデータを読み込み
        metadata = load_embeddings_metadata()
        if not metadata:
            return []
        
        # 対象の子どもの日記のみをフィルタリング
        diaries = load_diaries()
        child_diaries = [d for d in diaries if child_id in d.get("child_ids", [])]
        child_diary_ids = [d["diary_id"] for d in child_diaries]
        
        # メタデータをフィルタリング
        filtered_metadata = [m for m in metadata if m["diary_id"] in child_diary_ids]
        
        if not filtered_metadata:
            return []
        
        # FAISSで検索
        embeddings = np.array([item["embedding"] for item in filtered_metadata], dtype='float32')
        query_vec = np.array([query_embedding], dtype='float32')
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        k = min(top_k, len(filtered_metadata))
        distances, indices = index.search(query_vec, k)
        
        # 結果を日記情報に変換
        results = []
        for idx in indices[0]:
            if idx < len(filtered_metadata):
                diary_id = filtered_metadata[idx]["diary_id"]
                diary = next((d for d in child_diaries if d["diary_id"] == diary_id), None)
                if diary:
                    results.append(diary)
        
        return results
    
    except Exception as e:
        print(f"類似日記検索エラー: {e}")
        return []


# ===========================================
# LLM関連の関数
# ===========================================

def generate_advice(question: str, child_id: str) -> str:
    """育児アドバイスを生成"""
    try:
        # 子ども情報を取得
        child = get_child_by_id(child_id)
        if not child:
            return "子ども情報が見つかりません。"
        
        # 月齢を計算
        age_months = calculate_age_months(child["birth_date"])
        age_display = format_age_display(age_months)
        
        # 関連する日記を検索
        similar_diaries = search_similar_diaries(question, child_id)
        
        # 日記コンテキストを作成
        diary_context = ""
        if similar_diaries:
            for i, diary in enumerate(similar_diaries, 1):
                diary_context += f"\n【日記{i}】({diary['date']})\n{diary['content']}\n"
        else:
            diary_context = "関連する日記はありません。"
        
        # プロンプトを構築
        user_prompt = ADVICE_PROMPT_TEMPLATE.format(
            child_name=child["name"],
            age_months=age_months,
            age_display=age_display,
            notes=child.get("notes", "特になし"),
            diary_context=diary_context,
            question=question
        )
        
        # LLMに問い合わせ
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"アドバイス生成中にエラーが発生しました: {str(e)}"

"""
初期化処理
アプリ起動時に実行される初期設定
"""

import os
import json
from constants import (
    DATA_DIR, 
    CHILDREN_FILE, 
    DIARIES_FILE, 
    EMBEDDINGS_METADATA_FILE
)


def initialize_app():
    """
    アプリケーションの初期化処理
    - データディレクトリの作成
    - 初期データファイルの作成
    """
    # データディレクトリの作成
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 子どもデータファイルの初期化
    if not os.path.exists(CHILDREN_FILE):
        with open(CHILDREN_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 日記データファイルの初期化
    if not os.path.exists(DIARIES_FILE):
        with open(DIARIES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # Embeddingメタデータファイルの初期化
    if not os.path.exists(EMBEDDINGS_METADATA_FILE):
        with open(EMBEDDINGS_METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    initialize_app()
    print("アプリケーションの初期化が完了しました。")

"""
定数定義ファイル
アプリケーション全体で使用する固定値を定義
"""

# データファイルパス
DATA_DIR = "data"
CHILDREN_FILE = f"{DATA_DIR}/children.json"
DIARIES_FILE = f"{DATA_DIR}/diaries.json"
EMBEDDINGS_INDEX_FILE = f"{DATA_DIR}/embeddings.faiss"
EMBEDDINGS_METADATA_FILE = f"{DATA_DIR}/embeddings_metadata.json"

# OpenAI設定
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_DIMENSION = 1536

# アプリケーション設定
APP_TITLE = "🍼 子育てコンパニオン"
APP_ICON = "🍼"

# プロンプトテンプレート
SYSTEM_PROMPT = """あなたは経験豊富で優しい育児アドバイザーです。
親の悩みや困りごとに対して、共感的で肯定的なアドバイスを提供してください。

以下のルールを守ってください：
1. 親の気持ちに共感し、否定的な言葉は使わない
2. 具体的で実践的なアドバイスを提供する
3. 医療的な診断や判断は行わない（必要に応じて専門家への相談を勧める）
4. 子どもの個性や成長のペースを尊重する
5. 親自身のケアも大切であることを伝える
"""

ADVICE_PROMPT_TEMPLATE = """
【子どもの情報】
- 名前: {child_name}
- 月齢: {age_months}ヶ月（{age_display}）
- メモ: {notes}

【関連する過去の日記】
{diary_context}

【親の相談内容】
{question}

上記の情報を踏まえて、親に寄り添った育児アドバイスを提供してください。
"""

# RAG設定
RAG_TOP_K = 5  # 検索する関連日記の数
RAG_MIN_SIMILARITY = 0.5  # 最小類似度閾値

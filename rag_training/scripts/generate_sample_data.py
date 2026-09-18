"""ダミーの個人メモ/日記データを data/notes/ に生成する。"""
from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent.parent / "data" / "notes"

NOTES = {
    "2026-01-05_new_year_goals.md": """# 2026年の目標

今年はDockerとKubernetesをちゃんと触れるようになりたい。
あと機械学習アプリのバックエンド設計も勉強する。
FastAPIとPythonの型ヒントに慣れることも目標のひとつ。
""",
    "2026-01-12_docker_notes.md": """# Dockerメモ

Dockerfileはレイヤーキャッシュを意識して書くとビルドが速くなる。
requirements.txtを先にCOPYしてpip installしてから、
アプリのソースコードをCOPYするのが定石。

docker-composeを使うと複数コンテナの依存関係（depends_on）を
宣言的に書けて便利。
""",
    "2026-01-20_kubernetes_intro.md": """# Kubernetes入門メモ

Podはコンテナの最小デプロイ単位。
DeploymentがPodのレプリカ数を管理してくれる。
ConfigMapとSecretで設定と機密情報を分離するのがベストプラクティス。
minikubeやkindでローカルにクラスタを立てて練習できる。
""",
    "2026-02-02_rag_architecture.md": """# RAGアーキテクチャの整理

RAG（Retrieval-Augmented Generation）は、
質問をベクトル化してベクトルDBから関連文書を検索し、
その文書をコンテキストとしてLLMに渡して回答を生成する仕組み。

ベクトルDBの候補としてQdrant、pgvector、Chromaなどがある。
今回はQdrantを使うことにした。公式Dockerイメージがあって導入が楽。
""",
    "2026-02-10_embedding_memo.md": """# embeddingモデルのメモ

Claude自体にはembedding APIがないので、
sentence-transformersのようなローカルモデルか、
Voyage AIのようなクラウドAPIを別途使う必要がある。

all-MiniLM-L6-v2は軽量でCPUでも十分な速度が出る。
次元数は384で、精度と速度のバランスが良い。
""",
    "2026-02-18_fastapi_tips.md": """# FastAPI Tips

pydanticのBaseModelでリクエスト/レスポンスのスキーマを定義すると
自動でバリデーションとSwagger UIのドキュメントが生成される。

非同期処理はasync defで書けるが、
CPUバウンドな処理（embeddingの計算など）は
別スレッドやプロセスに逃がした方がいい場合もある。
""",
    "2026-02-25_weekend_hiking.md": """# 週末のハイキング記録

近くの低山に登った。天気が良くて富士山がよく見えた。
標高差は400mくらいで、初心者にもちょうどいいコースだった。
下山後に食べたそばがとても美味しかった。
""",
    "2026-03-03_book_review_clean_architecture.md": """# 読書メモ: Clean Architecture

依存関係の方向を内側に向けるという原則が印象的だった。
ビジネスロジックをフレームワークやDBの詳細から切り離すことで、
テストがしやすくなり、技術選定の変更にも強くなる。

マイクロサービス設計にもこの考え方は応用できそう。
""",
    "2026-03-11_qdrant_setup.md": """# Qdrantセットアップメモ

docker run -p 6333:6333 qdrant/qdrant で起動できる。
コレクションを作成するときはベクトルの次元数と距離関数
（Cosine, Euclid, Dotなど）を指定する必要がある。

Pythonクライアントはqdrant-clientパッケージを使う。
upsertでポイント（id, vector, payload）を登録する。
""",
    "2026-03-19_cooking_curry.md": """# カレーを作った

玉ねぎをじっくり炒めるのがコツだと聞いたので、
今回は40分くらいかけて飴色になるまで炒めた。
いつもよりコクが出て美味しくできた。
""",
    "2026-03-27_llm_prompt_design.md": """# LLMプロンプト設計メモ

RAGでは検索結果をどうプロンプトに埋め込むかが重要。
出典（ファイル名など）を明示させることで、
回答の根拠を後から確認できるようにするのが良い設計。

システムプロンプトで「わからない場合はわからないと答える」
と指示しておくとハルシネーションを減らせる。
""",
    "2026-04-02_job_hunting_notes.md": """# 転職活動メモ

求人票でよく見る要件: LLM/AIを使ったアプリ開発経験、
バックエンドのAPI設計、Docker/Kubernetesの実務経験。

ポートフォリオとして個人用RAGアシスタントを
Docker化して公開するのが良さそう。
""",
    "2026-04-09_running_log.md": """# ランニング記録

朝5kmを25分で走った。ペースは以前より少し上がってきた。
週3回のペースを維持できている。
""",
    "2026-04-15_microservice_design.md": """# マイクロサービス設計メモ

サービスごとに責務を分離すると、デプロイやスケーリングを
独立して行えるメリットがある。一方でサービス間通信の
複雑さやデータの一貫性の管理が課題になる。

データ処理（ingest）と配信（API）を分けるのは
よくあるパターンのひとつ。
""",
    "2026-04-22_coffee_notes.md": """# コーヒーのメモ

浅煎りの豆はフルーティーな酸味が強く出る。
ハンドドリップではお湯の温度を90度前後にすると
雑味が出にくいと感じた。
""",
}


def main() -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in NOTES.items():
        (NOTES_DIR / filename).write_text(content, encoding="utf-8")
    print(f"Generated {len(NOTES)} sample notes in {NOTES_DIR}")


if __name__ == "__main__":
    main()

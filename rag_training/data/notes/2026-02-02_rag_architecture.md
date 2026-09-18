# RAGアーキテクチャの整理

RAG（Retrieval-Augmented Generation）は、
質問をベクトル化してベクトルDBから関連文書を検索し、
その文書をコンテキストとしてLLMに渡して回答を生成する仕組み。

ベクトルDBの候補としてQdrant、pgvector、Chromaなどがある。
今回はQdrantを使うことにした。公式Dockerイメージがあって導入が楽。

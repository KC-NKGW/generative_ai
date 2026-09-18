# Qdrantセットアップメモ

docker run -p 6333:6333 qdrant/qdrant で起動できる。
コレクションを作成するときはベクトルの次元数と距離関数
（Cosine, Euclid, Dotなど）を指定する必要がある。

Pythonクライアントはqdrant-clientパッケージを使う。
upsertでポイント（id, vector, payload）を登録する。

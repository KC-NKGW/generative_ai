# Dockerメモ

Dockerfileはレイヤーキャッシュを意識して書くとビルドが速くなる。
requirements.txtを先にCOPYしてpip installしてから、
アプリのソースコードをCOPYするのが定石。

docker-composeを使うと複数コンテナの依存関係（depends_on）を
宣言的に書けて便利。

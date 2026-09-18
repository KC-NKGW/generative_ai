# FastAPI Tips

pydanticのBaseModelでリクエスト/レスポンスのスキーマを定義すると
自動でバリデーションとSwagger UIのドキュメントが生成される。

非同期処理はasync defで書けるが、
CPUバウンドな処理（embeddingの計算など）は
別スレッドやプロセスに逃がした方がいい場合もある。

# embeddingモデルのメモ

Claude自体にはembedding APIがないので、
sentence-transformersのようなローカルモデルか、
Voyage AIのようなクラウドAPIを別途使う必要がある。

all-MiniLM-L6-v2は軽量でCPUでも十分な速度が出る。
次元数は384で、精度と速度のバランスが良い。

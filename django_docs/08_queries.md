# クエリ

クエリは、`types.py`ファイルに定義されたフィールドを読み込むために`strawberry_django.filed()`を使用して記述できます。

```python
import strawberry
import strawberry_django

from .types import Fruit


@strawberry.type
class Query:
    fruit: Fruit = strawberry_django.field()
    fruits: list[Fruit] = strawberry_django.field()


schema = strawberry.Schema(query=Query)
```

---

💡 Tip

クエリクラスを`"Query"`と名付けるか、単一のクエリのデフォルトのプライマリーフィルタを機能させるために、`@strawberry.type(name="Query")`とデコレートしなくてはなりません。

---

上記`Fruit`のように単一クエリのために、`strawberry`はGraphQLインターフェイス内にデフォルトのプライマリーキー検索フィルターがあります。
`fruits`クエリはデフォルトで果物のすべてのオブジェクトを取得します。
特定のオブジェクトの集合を問い合わせするために、`types.py`ファイル内にフィルターが追加される必要があります。

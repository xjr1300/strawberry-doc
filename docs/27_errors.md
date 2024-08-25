# Strawberryにおけるエラー

`Strawberry`は、スキーマの作成または使用で何かがうまくいかないときのために、組み込みのエラーがあります。

また、`Strawberry`は、エラーが出力される方法を改善したり、例外の原因を見つけることを容易にするために、カスタムの例外ハンドラーを提供しています。
例えば、次のコードは・・・

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello_world(self);
        return "Hello there!"


schema = strawberry.Schema(query=Query)
```

コマンドラインに次の例外を表示します。

```text
  error: Missing annotation for field `hello_world`

       @ demo.py:7

     6 |     @strawberry.field
  ❱  7 |     def hello_world(self):
                 ^^^^^^^^^^^ resolver missing annotation
     8 |         return "Hello there!"


  To fix this error you can add an annotation, like so `def hello_world(...) -> str:`

  Read more about this error on https://errors.strawberry.rocks/missing-return-annotation
```

これらのエラーは、`rich`と`libcst`がインストールされているときのみ有効になります。
次を実行すると、エラーを有効にした`Strawberry`をインストールできます。

```sh
pip install "strawberry-graphql[cli]"
```

もし、エラーを無効にしたい場合、`STRAWBERRY_DISABLE_RICH_ERRORS`環境変数を`1`に設定することでできます。

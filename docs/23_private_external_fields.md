# プライベートフィールド

プライベート（エクスターナル）フィールドは、後の解決でローカルコンテキストとして提供できます。
これらのフィールドは、単なるフィールドのように機能するため、GraphQL APIで公開されません。

用途としては次のようなものがあります。

1. フィールドの入力に依存するコンテキスト
2. オブジェクト階層の完全な実体化の回避（遅延解決）

## プライベートフィールドの定義

`strawberry.Private[...]`でフィールドを指定することは、GraphQLではなく内部フィールドとして指定されます。

`designate`:【動詞】指名する、任命する、意味する、呼ぶ

## 例

```python
@strawberry.type
class Stringable:
    value: strawberry.Private[object]

    @strawberry.field
    def string(self) -> str:
        return str(self.value)

    @strawberry.field
    def repr(self) -> str:
        return repr(self.value)

    @strawberry.field
    def format(self, template: str) -> str:
        return template.format(my=self.value)
```

`Private[...]`型は、このフィールドがGraphQLのフィールドではないことを`Strawberry`に伝えます。
"value"はクラスの普通のフィールドですが、GraphQL APIで公開されません。

```python
@strawberry.type
class Query:
    @strawberry.field
    def now(self) -> Stringable:
        return Stringable(value=datetime.datetime.now())
```

クエリはフィールドと望んだ書式を選択できますが、書式化はリクエストとしてのみ発生します。

```graphql
{
  now {
    format(template: "{my.year}")
    string
    repr
  }
}
```

```json
{
  "data": {
    "now": {
      "format": "2022",
      "string": "2022-09-03 17:03:04.923068",
      "repr": "datetime.datetime(2022, 9, 3, 17, 3, 4, 923068)"
    }
  }
}
```

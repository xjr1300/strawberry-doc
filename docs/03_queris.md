# クエリ

GraphQLにおいてサーバーからデータを取得するためにクエリを使用します。
`Strawberry`において、クエリ型を定義刷ることによって、サーバーが提供するデータを定義できます。

デフォルトでAPIが公開するすべてのフィールドは、ルートクエリ型の配下にネストされます。

`Strawberry`でルートクエリ型を定義する方法を次に示します。

```python
@strawberry.type
class Query:
    name: str


schema = strawberry.Schema(query=Query)
```

これは、`name`と呼ばれるフィールドを1つ持つルートクエリ型でスキーマを作成します。

気付いたように、データを取得する方法を定義していません。
データを取得する方法を定義するために、特定のフィールドのデータを取得する方法を理解する関数である`resolver`を提供する必要があります。

この場合の例として、同じ名前を常に返す関数を持てます。

```python
def get_name() -> str:
    return "Strawberry"


@strawberry.type
class Query:
    name: str = strawberry.field(resolver=get_name)


schema = strawberry.Schema(query=Query)
```

これにより、`name`フィールドをリクエストしたとき、`get_name`関数が呼び出されます。

代わりに、フィールドはデコレーターを使用して定義されます。

```python
@strawberry.type
class Query:
    @strawberry.field
    def name(self) -> str:
        return "Strawberry"
```

> デコレーターを使用すると、クエリ型の定義内にデータを取得するロジックなどが入るため、クエリ型の定義の見通しが悪くなる可能性がある。
> クエリ型の定義を簡潔にするために、デコレーターを使用することを避けるべきだと考えられる。

## 引数

GraphQLのフィールドは、通常特定のオブジェクトを除外または取得するために引数を受け付れます。

```python
FRUITS = [
    "Strawberry",
    "Apple",
    "Orange",
]


@strawberry.type
class Query:
    @strawberry.field
    def fruit(self, startswith: str) -> str | None:
        for fruit in FRUITS:
            if fruit.startswith(startswith):
                return fruit
        return None
```

`typing.Annotated`を持つ`strawberry.argument`を使用して独自の名前と説明など、追加のメタデータは引数に追加されます。

```python
@strawberry.type
class Query:
    @strawberry.field
    def fruits(
        self,
        is_tasty: Annotated[
            bool | None,
            strawberry.argument(
                description="Filters out fruits by whenever they're tasty or not",
                deprecation_reason="isTasty argument is deprecated, "
                "use fruits(taste:SWEET) instead",
            ),
        ] = None,
    ) -> list[str]:
        ...
```

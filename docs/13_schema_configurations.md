# スキーマの設定

`Strawberry`は、設定を渡すことでスキーマが生成される方法をカスタマイズできます。

スキーマをカスタマイズするために、例として下に示した`StrawberryConfig`のインスタンスを作成できます。

```python
import strawberry
from strawberry.schema.config import StrawberryConfig


@strawberry.type
class Query:
    example_field: str


schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
```

この場合、自動キャメルケース変換を無効にするため、出力されるスキーマは次のようになります。

```graphql
type Query {
  example_field: String!
}
```

## 利用可能な設定

ここに利用可能な設定をリスとします。

### auto_camel_case

デフォルトで`Strawberry`はフィールド名をキャメルケースに変換するため、`example_field`のようなフィールドは`exampleField`に変換されます。
`auto_camel_case`を`False`に設定することで、この機能を無効にできます。

```python
schema = strawberry.Schema(query=Query, config=StrawberryConfig(auto_camel_case=False))
```

### default_resolver

デフォルトで`Strawberry`はデフォルトのリゾルバーとして`getattr`関数を使用します。
`default_resolver`設定を設定することでこれをカスタマイズできます。

これは、リゾルバーから辞書を返したい場合に便利です。

```python
import strawberry
from strawberry.schema.config import StrawberryConfig


def custom_resolver(obj, field):
    try:
        return obj[field]
    except (KeyError, TypeError):
        return getattr(obj, field)


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self, info) -> User: # これは型チェックではありませんが、実行時に機能します。
        return {"name": "Patrick"}


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(default_resolver=custom_resolver)
)
```

### relay_max_results

デフォルトで`Strawberry`の`relay`接続の最大制限は100です。
`relay_max_results`設定を設定することでこれをカスタマイズできます。

```python
schema = strawberry.Schema(query=Query, config=StrawberryConfig(relay_max_results=50))
```

### disable_field_suggestions

デフォルトで`Strawberry`は、スキーマ内にフィールドが存在しないときフィールドを提案します。
`disable_field_suggestions`を`True`に設定することでこの機能を無効にできます。

```python
scheme = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(disable_field_suggestions=True)
)
```

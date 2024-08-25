# スキーマのコード生成

`Strawberry`は、SDLファイルからコードを生成することをサポートしています。

次のSDLファイルがあることを想定してください。

```graphql
type Query {
  user: User
}

type User {
  id: ID!
  name: String!
}
```

次のコマンドを実行することによって・・・

```sh
strawberry schema-codegen schema.graphql
```

次の出力を得られます。

```python
import strawberry


@strawberry.type
class Query:
    user: User | None


@strawberry.type
class User:
    id: strawberry.ID
    name: str


schema = strawberry.Schema(query=Query)
```

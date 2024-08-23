# よく尋ねられる質問

## どのようにGraphQLからフィールドを隠すことができるか？

`Strawberry`は、GraphQLからフィールドを隠すために使用できる`Private`型を提供しています。
例えば、次のコードを見てください。

```python
import strawberry


@strawberry.type
class User:
    name: str
    age: int
    password: strawberry.Private[str]


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, password="This is fake")


schema = strawberry.Schema(query=Query)
```

上記は結果として次のスキーマになります。

```graphql
type Query {
  user: User!
}

type User {
  name: String!
  age: Int!
}
```

## 循環インポートをどのように処理できるか？

循環インポートを持つ場合において、循環インポートを解決するために`strawberry.lazy`を使用できます。

```python
# posts.py
from typing import TYPE_CHECKING, Annotated

import strawberry


if TYPE_CHECKING:
    from .user import User


@strawberry.type
class Post:
    title: str
    author: Annotated["User", strawberry.lazy(".users")]
```

詳細な情報は、[Lazy型](https://strawberry.rocks/docs/types/lazy)ドキュメントを参照してください。

## 入力オブジェクトでオブジェクト型を再利用できるか？

[GraphQL仕様](https://spec.graphql.org/June2018/#sec-Input-Objects)の指定として、オブジェクト型と入力型は異なるため、不運にもできません。

> 上記で定義したGraphQLオブジェクト型(`ObjectTypeDefinition`)は、ここでの再利用には適していません。
> これは、オブジェクト型には引数を定義するフィールドや、インターフェースやユニオンへの参照が含まれることがあるためです。
> これらはいずれも入力引数として使用するには適していません。
> このため、入力オブジェクトにはシステム内で別の型があります。

そして、これはまた入力型のフィールドについても真実です。
`Strawberry`の入力型またはスカラーのみを使用できます。

[入力型](https://strawberry.rocks/docs/types/input-types)のドキュメントを参照してください。

## StrawberryとDjangoでasyncioを使用できるか？

使用できます。
`Strawberry`は`Django`で使用される非同期ビューを提供しています。
詳細は[非同期Django](https://strawberry.rocks/docs/integrations/django#async-django)を確認してください。

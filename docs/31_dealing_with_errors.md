# エラーを処理する

GraphQLには多くのさまざまな型のエラーがあり、それぞれは異なる処理がされます。

このガイドにおいて、GraphQLサーバーを構築するときに遭遇するさまざまな種類のエラーの概要を説明します。

---

注意事項

デフォルトで、`Strawberry`は[`strawberry.execution`](https://strawberry.rocks/docs/types/schema)ロガーにすべての実行エラーをログに出力します。

---

## GraphQL検証エラー

GraphQLは強く型付けされているため、`Strawberry`はクエリを実行する前にすべてのクエリを検証します。
もしクエリが不正な場合、それは実行されず、代わりにレスポンスは`errors`リストを含みます。

```graphql
{
  hi
}
```

```json
{
  "data": null,
  "errors": [
    {
      "message": "Cannot query field 'hi' on type 'Query'.",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": null
    }
  ]
}
```

それぞれのエラーは、クエリのどの部分がエラーを引き起こしたかを識別することを支援するために、メッセージ、行、列そしてパスを持ちます。

検証ルールはGraphQL仕様の一部であり、`Strawberry`に組み込まれているため、この動作をカスタマイズする方法はありません。
[DisableValidation](https://strawberry.rocks/docs/extensions/disable-validation)エクステンションを使用することで、すべての検証を無効化できます。

## GraphQL型エラー

クエリが実行されるとき、それぞれのフィールドは正確な型に解決される必要があります。
例えば、非nullフィールドは`None`を返せません。

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return None


schema = strawberry.Schema(query=Query)
```

```graphql
{
  hello
}
```

```json
{
  "data": null,
  "errors": [
    {
      "message": "Cannot return null for non-nullable field Query.hello.",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": ["hello"]
    }
  ]
}
```

それぞれのエラーは、クエリのどの部分がエラーを引き起こしたかを識別することを支援するために、メッセージ、行、列そしてパスを持ちます。

## 処理されていない実行エラー

時々、リゾルバーは、プログラミングエラーまたは不正な想定のために、予期しないエラーをすろーします。
これが発生sたとき、`Strawberry`はエラーをキャッチして、レスポンス内の最上位の`errors`フィールド内に公開します。

```python
import strawberry


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user() -> User:
        raise Exception("Can't find user")


schema = strawberry.Schema(query=Query)
```

```graphql
{
  user {
    name
  }
}
```

```json
{
  "data": null,
  "errors": [
    {
      "message": "Can't find user",
      "locations": [
        {
          "line": 2,
          "column": 2
        }
      ],
      "path": ["user"]
    }
  ]
}
```

## 予期されたエラー

エラーが予想される場合、よくそれをスキーマで表現することが最善です。
これは強固な方法でクライアントがエラーを処理できるようにします。

データ顔存在しない可能性があるときに、フィールドをオプションにすることで、これを得ることができます。

```python
from typing import Optional

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def get_user(self, id: str) -> Optional[User]:
        try:
            user = get_a_user_by_their_id(id)
            return user
        except UserDoesNotExist:
            return None
```

予期されたエラーがより複雑な場合、代わりにエラーまたは成功レスポンスのどちらかを表現するユニオン型を返すことが良いパターンです。
このパターンは、クライアントにより複雑なエラーの詳細を返すことが重要なミューテーションによく採用されます。

例えば、ユーザーがすでに存在するユーザー名で登録することを試みる可能性を扱う必要がある、`registerUser`ミューテーションがあるとします。
次のようにミューテーションの方を構築するかもしれません。

```python
from typing import Annotated, Union

import strawberry


@strawberry.type
class RegisterUserSuccess:
    user: User


@strawberry.Type
class UsernameAlreadyExistsError:
    username: str
    alternative_username: str


# ミューテーションから返される2つの結果を表現するユニオン型を作成します。
Response = Annotated[
    Union[RegisterUserSuccess, UsernameAlreadyExistsError],
    strawberry.union("RegisterUserResponse"),
]


@strawberry.mutation
def register_user(username: str, password: str) -> Response:
    if username_already_exists(username):
        return UsernameAlreadyExistsError(
            username=username, alternative_username=generate_username_suggestion(username),
        )

    user = create_user(username, password)
    return RegisterUserSuccess(user=user)
```

そして、クライアントは次に何をするかを決定するために、結果の`__typename`を確認できます。

```graphql
mutation RegisterUser($username: String!, $password: String!) {
  registerUser(username: $username, password: $password) {
    __typename
    ... on UsernameAlreadyExistsError {
      alternativeUsername
    }
    ... on RegisterUserSuccess {
      id
      username
    }
  }
}
```

この手段はスキーマ内に可能性のあるエラーの状態を表現できるようにして、ミューテーションから得られるすべての可能性のある結果をクライアントに説明する強固なインターフェイスを提供できるようにします。

## 追加リソース

* [GraphQLのエラーガイド](https://productionreadygraphql.com/2020-08-01-guide-to-graphql-errors/)
* [200 OK! GraphQLのエラー処理](https://sachee.medium.com/200-ok-error-handling-in-graphql-7ec869aec9bc)

`adopt`:【動詞】採用する、選定する、可決する、承認する、養子にする

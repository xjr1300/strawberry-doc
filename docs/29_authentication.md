# 認証

認証は、ユーザーが本人であることを確認するプロセスであり、使用しているフレームワークによって処理される必要があります。
Djangoのようにいくつかは認証システムを組み込みで持っていますが、ほかは手動で提供しなければなりません。
ユーザーを認証することは`Strawberry`の責任ではありませんが、認証プロセスを処理するミューテーションを作成するために使用できます。
また、認証と認可を混同しないことはとても重要です。
認可は認証されたユーザーができること、または彼らがどのデータにアクセスできるかを決定します。
`Strawberry`において、これは`Permissions`クラスで管理されます。

これらの概念をまとめることを例で確認しましょう。
最初に、資格情報を認証して、ユーザーが認証に成功するかしないかによって`LoginSuccess`または`LoginError`型を返す`login`ミューテーションを定義します。

```python
from typing import Annotated, Union

import strawberry

from .types import User

@strawberry.type
class LoginSuccess:
    user: User


@strawberry.type
class LoginError:
    message: str


LoginResult = Annotated[
    Union[LOginSuccess, LoginError], strawberry.union("LoginResult")
]


@strawberry.mutation
class Mutation:
    @strawberry.field
    def login(self, username: str, password: str) -> LoginResult:
        # ドメイン特有の認証ロジックをここに追加します。
        user = ...

        if user is None:
            return LoginError(message="Something went wrong")

        return LoginSuccess(user=User(username=username))
```

`put together`:【動詞】まとめる

## リゾルバー内で認証されたユーザーにアクセスする

リゾルバー内で、ユーザー情報が必要なことはとても一般的です。
カスタムコンテキストデータクラスを使用して、型セーフな方法でそれをできます。

例えば、FastAPIでは次のようになります。

```python
from functools import cached_property

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import BaseContext, GraphQLRouter


@strawberry.type
class User:
    # これは実際のユーザーオブジェクトの単なるスタブです。


class Context(BaseContext):
    @cached_property
    def user(self) -> User | None:
        if not self.request:
            return None
        authorization = self.request.headers.get("Authorization", None)
        return authorization_service.authorize(authorization)



@strawberry.type
class Query:
    @strawberry.field
    def get_authenticated_user(self, info: strawberry.Info[Context]) -> User | None:
        return info.context_user


async def get_context() -> Context:
    return Context()


schema = strawberry.Schema(query=Query)


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

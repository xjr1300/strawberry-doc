# DataLoader

`Strawberry`は、リクエストをバッチまたはキャッシュすることにより、データベースまたはサードパーティへのリクエストの数を減らすために使用できる一般的なユーティリティである組み込みの`DataLoader`が付いてきます。

---

注意事項

`DataLoader`は非同期APIを提供しているため、それらは非同期コンテキスト内でのみ機能します。

---

`DataLoader`の高度なガイドとして、公式の`DataLoader`の[仕様](https://github.com/graphql/dataloader)を参照してください。

## 基本的な使用方法

ここに`DataLoader`の使用方法を示します。
最初に、バッチでデータを取得する関数を定義する必要があります。
IDのみを持つユーザー型があるとします。

```python
import strawberry


@strawberry.type
class User:
    id: strawberry.ID
```

渡されたキーのリストに基づいてユーザーのリストを返す関数を定義する必要があります。

```python
from typing import List


async def load_users(keys: List[int]) -> List[User]:
    return [User(id=key) for key in keys]
```

通常、この関数はデータベースまたはサードパーティAPIと相互作用しますが、例ではそれを必要としません。

ここで、読み込み関数を持つ、`DataLoader`を定義して、それを使用できます。

```python
from strawberry.dataloader import DataLoader

loader = DataLoader(load_fn=load_users)

user = await loader.load(1)
```

これは、`load_users`を`[1]`と等しいキーで呼び出す結果になります。
これは、次の例のように複数のリクエストをするとき、とても強力になります。

```python
import asyncio

[user_a, user_b] = await asyncio.gather(loader.load(1), loader.load(2))
```

これは、`load_users`を`[1, 2]`と等しいキーで呼び出す結果になります。
よって、データベースまたはサードパティへの呼び出しを1回に減ります。

さらに、デフォルトで、`DataLoader`は読み込みをキャッシュするため、例えば次のようなコードは・・・

```python
await loader.load(1)
await loader.load(1)
```

たった1回の`load_users`呼び出しになります。

そして最後に、時々、同時に1つより多きキーを読み込む必要があります。
そのような場合、`load_many`メソッドを使用できます。

```python
[user_a, user_b, user_c] = await loader.load_many([1, 2, 3])
```

## エラー

特定のキーに関連したエラーは、返されたリストの対応した位置に例外値を含めることにより示すことができます。
この例外は、そのキーで`load`を呼び出すことによってスローされます。
上と同じ`User`クラスを使用して・・・

```python
from typing import List, Union

from strawberry.dataloader import DataLoader

users_database = {
    1: User(id=1),
    2: User(id=2),
}


async def load_users(keys: List[int]) -> List[Union[User, ValueError]]:
    def lookup(key: int) -> Union[User, ValueError]:
        if user := users_database.get(key):
            return user
        return ValueError("not found")

    return [lookup(key) for key in keys]


loader = DataLoader(load_fn=load_users)
```

このローダーに対して、`await loader.load(1)`のような呼び出しは、`User(id=1)`を返す一方で、`await loader.load(3)`は`ValueError("not found")`が発生します。

`load_users`関数はリスト内のそれぞれの誤ったキーに対して例外値を返すことは重要です。
`key==[1, 3]`での呼び出しは、`[User(id=1), ValueError("not found")]`を返し、直接`ValueError`を返しません。
もし、`load_users`関数が例外を発生した場合、`await loader.load(1)`のような他の有効なキーを含む`load`は、例外を発生させます。

## キャッシュのキーの上書き

デフォルトで、入力はキャッシュのキーに使用されます。
上記例において、キャッシュのキーは常にスカラー（int、float、stringなど）で、入力に対してデータを一意に解決します。

特定のアプリケーションにおいて、データを一意に識別するためにフィールドの組み合わせが必要な状況があります。
`DataLoader`に`cache_key_fn`引数を提供することで、キーを生成する動作は変更されます。
オブジェクトがキーで2つのオブジェクトが等しいとみなされなくてはならないとき、それはとても便利です。
関数定義は、入力引数を受け取り、`HashTable`型を返します。

```python
from typing import List, Union

from strawberry.dataloader import DataLoader


class User:
    def __init__(self, custom_id: int, name: str):
        self.id: int = custom_id
        self.name: str = name


async def loader_fn(keys):
    return keys


def custom_cache_key(key):
    return key.id


loader = DataLoader(load_fn=loader_fn, cache_key_fn=custom_cache_key)
data1 = await loader.load(User(1, "Nick"))
data2 = await loader.load(User(1, "Nick"))
assert data1 == data2   # Trueを返します。
```

`loader.load(User(1, "Nick"))`は内部で`custom_cache_key`を呼び出し、`User.id`をキーとして1を返す関数へのパラメーターとしてオブジェクトを渡します。
その2回目の呼び出しは、`custom_cache_key`によって返されたキーでキャッシュを確認して、ローダーのキャッシュからキャッシュデータを返します。

実装は、キャッシュキーを生成した間に衝突を処理するユーザーに依存します。
衝突の場合、データはそのキーのために上書きされます。

## キャッシュの無効化

デフォルトで、`DataLoader`は内部キャッシュを使用します。
それは良い性能ですが、例えばミューテーションなど、キャッシュされたデータはもはや無効なため、データが修正されたときに問題を引き起こす可能性があります。

それを修正するために、3つの方法の内1つを使用して、キャッシュ内のデータを明示的に無効にできます。

1. `loader.clear(id)`でキーを指定する。
2. `loader.clear_many([id1, id2, id3, ...])`でいくつかのキーを指定する。
3. `loader.clear_all()`でキャッシュ全体を無効化する。

## キャッシュにデータをインポートする

`DataLoader`は強力で効率的な一方で、複雑なクエリをサポートしていません。

アプリがそれらを必要とする場合、多分`DataLoader`と直接的なデータベース呼び出しを混在させるでしょう。

このようなシナリオにおいて、後でデータを再読込することを避けるために、外部から取得したデータを`DataLoader`にインポートすることは便利です。

```python
@strawberry.type
class Person:
    id: strawberry.ID
    friends_ids: strawberry.Private[List[strawberry.ID]]

    @strawberry.field
    async def friends(self) -> List[Person]:
        return await loader.load_many(self.friends_ids)


@strawberry.type
class Query:
    @strawberry.field
    async def get_all_people(self) -> List[Person]:
        # DataLoaderの抽象化を介すことなく、データベースからすべての人々を取得します。
        people = await database.get_all_people()

        # 取得した人々をDataLoaderキャッシュに挿入します。
        # 現在、「すべての人々」はキャッシュ内にあるため、`Person.friends`のアクセスは
        # 追加のデータベースアクセスを発しません。
        loader.prime_many({person.id: person for person in people})

        return people
```

```graphql
{
  getAllPeople {
    id
    friends {
      id
    }
  }
}
```

## カスタムキャッシュ

`DataLoader`のデフォルトキャッシュはリクエストごとで、それはメモリ内にデータをキャッシュします。
この戦略は、最適またはすべての場面で安全でないかもしれません。
例えば、分散された環境で`DataLoader`を使用する場合、分散されたキャッシュを使用する必要があるかもしれません。
`DataLoader`は独自のキャッシュロジックを上書きできるようにしており、例えばRedisなど、それは他の永続的なキャッシュからデータを得ることができます。

`DtaLoader`は`cache_map`引数を提供しています。
それは、`AbstractCache`抽象インターフェイスを実装したクラスのインスタンスを受け取ります。
そのインターフェイスメソッドは、`get`、`set`、`delete`そして`clear`です。

もし両方の引数が提供された場合、`cache_map`引数は、`cache_key_fn`を上書きします。

```python
from typing import List, Union, Any, Optional

import strawberry
from strawberry.asgi import GraphQL
from strawberry.dataloader import DataLoader, AbstractCache

from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response


class UserCache(AbstractCache):
    def __init__(self):
        self.cache = {}

    def get(self, key: Any) -> Union[Any, None]:
        return self.cache.get(key)  # fetch data from persistent cache

    def set(self, key: Any, value: Any) -> None:
        self.cache[key] = value  # store data in the cache

    def delete(self, key: Any) -> None:
        del self.cache[key]  # delete key from the cache

    def clear(self) -> None:
        self.cache.clear()  # clear the cache


@strawberry.type
class User:
    id: strawberry.ID
    name: str


async def load_users(keys) -> List[User]:
    return [User(id=key, name="Jane Doe") for key in keys]


class MyGraphQL(GraphQL):
    async def get_context(
        self, request: Union[Request, WebSocket], response: Optional[Response]
    ) -> Any:
        return {"user_loader": DataLoader(load_fn=load_users, cache_map=UserCache())}


@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, info: strawberry.Info, id: strawberry.ID) -> User:
        return await info.context["user_loader"].load(id)


schema = strawberry.Schema(query=Query)
app = MyGraphQL(schema)
```

## GraphQLで使用する

GraphQLで`DataLoader`を使用する方法を示した例を確認します。

```python
from typing import List

from strawberry.dataloader import DataLoader
import strawberry


@strawberry.type
class User:
    id: strawberry.ID


async def load_users(keys) -> List[User]:
    return [User(id=key) for key in keys]


loader = DataLoader(load_fn=load_users)


@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, id: strawberry.ID) -> User:
        return await loader.load(id)


schema = strawberry.Schema(query=Query)
```

ここでは、IDによって単一のユーザーを取得するGraphQLクエリとともに、前に定義した同じローダを定義しました。

次のリクエストをすることによって、このクエリを使用できます。

```graphql
{
  first: getUser(id: 1){
    id
  }
  second: getUser(id: 2) {
    id
  }
}
```

```json
{
  "data": {
    "first": {
      "id": 1
    },
    "second": {
      "id": 2
    }
  }
}
```

このクエリは2つのユーザーを取得しているにもかかわらず、それは1回の`load_users`呼び出しになります。

## コンテキストと使用する

上記コードで確認した通り、`DataLoader`はリゾルバーの外部で初期化されるため、複数のリゾルバー間、または複数のリゾルバーの呼び出し間で共有する必要があります。
しかし、`DataLoader`はサーバーが実行している限り結果をキャッシュするため、サーバー内部でスキーマを使用しているとき、これは推奨されないパターンです。

代わりに、一般的なパターンは、GraphQLコンテキストが作成されたときに`DataLoader`を作成することで、単一リクエストの結果のみをキャッシュします。
ASGIビューでこれを使用する例を確認しましょう。

```python
from typing import List, Union, Any, Optional

import strawberry
from strawberry.asgi import GraphQL
from strawberry.dataloader import DataLoader

from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import Response


@strawberry.type
class User:
    id: strawberry.ID


async def load_users(keys) -> List[User]:
    return [User(id=key) for key in keys]


class MyGraphQL(GraphQL):
    async def get_context(
        self, request: Union[Request, WebSocket], response: Optional[Response]
    ) -> Any:
        return {"user_loader": DataLoader(load_fn=load_users)}


@strawberry.type
class Query:
    @strawberry.field
    async def get_user(self, info: strawberry.Info, id: strawberry.ID) -> User:
        return await info.context["user_loader"].load(id)


schema = strawberry.Schema(query=Query)
app = MyGraphQL(schema)
```

これで、ASGIサーバーで上記例を実行できます。
ASGIを読んで、アプリの実行方法を詳細に得られます。
uvicornを選択した場合、次のようにインストールできます。

```sh
pip install uvicorn
```

そしてその後、アプリを開始する上記`schema.py`と名付けたファイルを仮定します。

```sh
uvicorn schema:app
```

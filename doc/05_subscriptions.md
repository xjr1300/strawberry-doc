# サブスクリプション

GraphQLにおいて、サーバーからデータをストリーミングするためにサブスクリプションを使用できます。
これを`Strawberry`で可能にするために、サーバーは`ASGI`と`WebSocket`をサポートするか、`AIOHTTP`統合を使用しなければなりません。

次は、サブスクリプション可能なリゾルバーの定義です。

```python
import asyncio
from typing import AsyncGenerator

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> AsyncGenerator[int, None]:
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)


schema = strawberry.Schema(query=Query, subscription=Subscription)
```

クエリとミューテーションと同様に、サブスクリプションはクラス内に定義され、`Schema`関数に渡されます。
0からカウントして、それぞれのループイテレーション間でスリープさせる、初歩的なカウントする関数を作成しました。

---

注意事項

`count`の戻り値の型は`AsyncGenerator`で、それは最初のジェネリック引数はレスポンスの実際の型です。
ほとんどの場合、2番目のパラメーターは`Non`として残すべきです（詳細は[ジェネリックの型注釈](https://docs.python.org/3/library/typing.html#typing.AsyncGenerator)を参照してください）。

---

このデータストリーミングを購読するためにサーバーに次のGraphQLドキュメントを送信します。

```graphql
subscription {
  count(target: 5)
}
```

この例において、WebSocketを通過するデータは次のようになります。

![サブスクリプションのデータ](https://strawberry.rocks/_astro/subscriptions-count-websocket.D5io8Aym_1ByWbb.webp)

これは何が可能であるかを示すとても短い例です。
クエリとミューテーションの使用と同様に、サブスクリプションは任意のGraphQLの型を返すだけでなく、ここで紹介したようにスカラーも返せます。

`rudimentary`:【形容詞】根本の、基本の、初歩の、始まりの、未熟な
`pass over`:【動詞】通過する、託す、順番を回す、追い越される

## サブスクリプションの認証

理由については詳しく説明しませんが、ブラウザから発信されるWebSocketリクエストにカスタムヘッダーを設定することはできません。
よって、WebSocketに依存した任意のGraphQLリクエストを作成するとき、ヘッダを基盤とした認証は不可能です。

例えば`Apollo`のような他の人気のあるGraphQLの解決策は、WebSocketの接続の初期化時点で、クライアントからサーバーに情報を渡す機能を実装することです。
この方法において、WebSocket接続の初期化と接続の生存期間全体に関連する情報は、サーバーによってデーターがストリーミング返送される前に渡されます。
このように、これは認証資格情報のみに制限されません。

`Strawberry`の実装は、最初のWebSocket接続メッセージの内容を`info.context`オブジェクトに読み取ることによって、[クライアント](https://www.apollographql.com/docs/react/data/subscriptions/#5-authenticate-over-websocket-optional)と[サーバー](https://www.apollographql.com/docs/apollo-server/data/subscriptions/#operation-context)の実装のドキュメントとして`Apollo`の実装に従っています。

この初期接続情報を送信する方法の例として、`Apollo`クライアントを使用すると、`ws-link`を次のように定義します。

```js
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { createClient } from "graphql-ws";

const wsLink = new GraphQLWsLink(
  createClient({
    url: "ws://localhost:4000/subscriptions",
    connectionParams: {
      authToken: "Bearer I_AM_A_VALID_AUTH_TOKEN",
    },
  }),
);
```

その後、サブスクリプションリクエストと基盤となるWebSocket接続の確立時に、`Strawberry`は次の通りこの`connectionParams`オブジェクトを注入します。

```python
import asyncio
from typing import AsyncGenerator

import strawberry

from .auth import authenticate_token


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(
        self, info: strawberry.Info, target: int = 100
    ) -> AsyncGenerator[int, None]:
        connection_params: dict = info.context.get("connection_params")
        token: str = connection_params.get(
            "authToken
        )   # "Bearer I_AM_A_VALID_AUTH_TOKEN"に等しい
        if not authenticate_token(token):
            raise Exception("禁止されています！")
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)


schema = strawberry.Schema(query=Query, subscription=Subscription)
```

`Strawberry`は`connection_params`オブジェクトを任意の型であることを予期しているため、クライアントは、`Apollo`クライアント内の`connectionParams`として抽象化されたWebSocketの初期メッセージとして、自由に任意の有効なJSONオブジェクトを送信でき、それは`info.context`オブジェクト内に正常に注入されます。
それを正しく処理するかどうかは実装次第です。

## 高度なサブスクリプションのパターン

典型的に、GraphQLサブスクリプションは、より興味のある何かをストリーミングします。
それを念頭に置いて、サブスクリプション関数は次の1つを返せます。

1. `AsyncIterator`、または
2. `AsyncGenerator`

これらの型両方は[PEP-525](https://www.python.org/dev/peps/pep-0525/)でドキュメント化されています。
これらの型のリゾルバーから生成されるものは、WebSocketをまたがって運ばれます。
返される値がGraphQLスキーマと一致することを保証するように注意が必要です。

イテレーターと比較した`AsyncGenerator`の利点は、複雑なビジネスロジックがコードベース内の分離したモジュールに分割されることです。
リゾルバーのロジックを完結に維持できるようになります。

次の例は、ジェネレーターが終了するまでサブスクリプション結果をストリーミングする責任を持つASGIサーバーに`AsyncGenerator`を返すことを除いて、上のものと似ています。

`conform`:【動詞】〜と一致する、同じである、適合する、順応する、準拠する、従う
`succinct`:【形容詞】簡潔明瞭な、簡潔さを特徴とする、ぴったりあった

```python
import strawberry
import asyncio
import asyncio.subprocess as subprocess
from asyncio import streams
from typing import Any, AsyncGenerator, AsyncIterator, Coroutine, Optional


async def wait_for_call(coro: Coroutine[Any, Any, bytes]) -> Optional[bytes]:
    """
    wait_for_callは、wait_forブロック内で供給されたコルーチンを呼び出します。

    これは、コルーチンのタスクを終了するまで何も生み出さないコルーチンの場合を軽減します。
    この場合、StreamReaderから行を読み込み、もしストリーム内に`\n`行文字がない場合、関数は決して終了しません。
    """
    try:
        return await asyncio.wait_for(coro(), timeout=0.1)
    except asyncio.TimeoutError:
        pass


async def lines(stream: streams.StreamReader) -> AsyncIterator[str]:
    """
    lines（関数）は提供されたストリームからすべての行を、UTF-8文字列としてデコードして読み込みます。
    """
    while True:
        b = await wait_for_call(stream.readline)
        if b:
            yield b.decode("UTF-8").rstrip()
        else:
            break


async def exec_proc(target: int) -> subprocess.Process:
    """
    exec_procはサブプロセスを開始して、そのサブルプロセスへのハンドルを返します。
    """
    return await asyncio.create_subprocess_exec(
        "/bin/bash",
        "-c",
        f"for ((i = 0 ; i < {target} ; i++)); do echo $i; sleep 0.2; done",
        stdout=subprocess.PIPE,
    )


async def tail(proc: subprocess.Process) -> AsyncGenerator[str, None]:
    """
    tailはプロセスが終了するまでstdoutから読み込みます。
    """
    # 注意事項: サブプロセス内のため、ここで競合する可能性があります。
    # この場合、プロセスはループ述語とstdoutから行を読み込む呼び出しの間に終了する可能性があります。
    # これは、wait_for_call()内でasyncio.wait_forを使用して防御的である必要がある理由の良い例です。
    while proc.returncode is None:
        async for l in lines(proc.stdout):
            yield l
    else:
        # プロセスが終了したあとにパイプの左を読み込みます。
        async for l in lines(proc.stdout):
            yield l


@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "world"


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def run_command(self, target: int = 100) -> AsyncGenerator[str, None]:
        proc = await exec_proc(target)
        return tail(proc)


schema = strawberry.Schema(query=Query, subscription=Subscription)
```

## WebSocketプロトコル上のGraphQL

`Strawberry`は従来からの`graphql-ws`と新しく推奨される`graphql-transport-ws`のWebSocketのサブプロトコルをサポートしています。

---

注意事項

`graphql-transport-ws`プロトコルのリポジトリは`graphql-ws`と呼ばれています。
しかし、`graphql-ws`は従来のプロトコルの名前でもあります。
このドキュメントは常にプロトコルの名前で指し示します。

---

`graphql-ws`サブプロトコルは主に後方互換のためにサポートしていることに注意してください。
新しいプロトコルが推奨される理由について、詳しくは[graphql-ws-transportプロトコルの発表](https://the-guild.dev/blog/graphql-over-websockets)を読んでください。

`Strawberry`は受け付けしたいプロトコルを選択できるようにします。
サブスクリプションをサポートしているすべての統合は、受付する`subscription_protocol`のリストを使用して構成できます。
デフォルトでは、すべてのプロトコルが受け付けられます。

## AIOHTTP

```python
from strawberry.aiohttp.views import GraphQLView
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from api.schema import schema


view = GraphQLView(
    schema, subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)
```

## ASGI

```python
from strawberry.asgi import GraphQL
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from api.schema import schema


app = GraphQL(
    schema,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ],
)
```

## Django + Channels

```python
import os

from django.core.asgi import get_asgi_application
from strawberry.channels import GraphQLProtocolTypeRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_asgi_app = get_asgi_application()

# DjangoのASGIアプリケーションを作成した後にStrawberryスキーマをインポートしてください。
# これは、スキーマのために、django.setup()が任意のORMモデルをインポートする前に呼び出されることを保証します。
from mysite.graphql import schema


application = GraphQLProtocolTypeRouter(
    schema,
    django_application=django_asgi_app,
)
```

注意事項: 詳細については[チャネルの統合](https://strawberry.rocks/docs/integrations/channels)ページを確認してください。

## FastAPI

```python
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from fastapi import FastAPI
from api.schema import schema

graphql_router = GraphQLRouter(
    schema,
    subscription_protocols=[
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    ],
)
app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")
```

## 単一結果の操作

ストリーミング操作（例えばサブスクリプション）に加えて、`graphql-transport-ws`プロトコルは単一結果の操作をサポートしています（例えばクエリやミューテーション）。

これは、クライアントがクエリ、ミューテーションそしてサブスクリプションに対して、1つのプロトコルと1つの接続を使用すること可能にします。
選択したGraphQLクライアントを正しく設定する方法を学ぶために、[プロトコルリポジトリ](https://github.com/enisdenjo/graphql-ws)を参照してください。

`Strawberry`は、`graphql-transport-ws`プロトコルが有効なとき、組み込みで単一結果の操作をサポートしています。
単一結果の操作は通常クエリとミューテーションであるため、任意のリゾルバーを調整する必要はありません。

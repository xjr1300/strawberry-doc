# クエリのコード生成

`Strawberry`は、GraphQLクエリのコード生成をサポートしています。

---

注意事項

スキーマコード生成は将来のリリースでサポートされる予定です。
すばらしいAPIを作成するためにクエリ生成をテストしています。

---

`Strawberry`で構築された次のGraphQLスキーマがあることを想定してください。

```python
from typing import List

import strawberry


@strawberry.type
class Post:
    id: strawberry.ID
    title: str


@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str

    @strawberry.field
    def post(self) -> Post:
        return Post(id=self.id, title=f"Post for {self.name}")


@strawberry.type
class Query:
    @strawberry.field
    def user(self, into) -> User:
        return User(id=strawberry.ID("1"), name="John", email="abc@bac.com")

    @strawberry.field
    def all_users(self) -> List[User]:
        return [
            User(id=strawberry.ID("1"), name="John", email="abc@bac.com"),
        ]


schema = strawberry.Schema(query=Query)
```

そして、型に基づいた次のクエリを生成する必要があります。

```graphql
query MyQuery {
  user {
    post {
      title
    }
  }
}
```

次のコマンドで・・・

```sh
strawberry codegen --schema schema --out-dir ./output -p python query.graphql
```

`./output/query.py`に次の出力が得られます。

```python
class MyQueryResultUserPost:
    title: str


class MyQueryResultUser:
    post: MyQueryResultUserPos


class MyQueryResult:
    user: MyQueryResultUser
```

`come up with`:【動詞】追いつく、考え出す、作り出す

## なぜこれが便利なのか？

クエリコード生成は、通常GraphQL APIを使用するクライアントに対して、型を生成するために使用されます。

[GraphQLコード生成](https://www.graphql-code-generator.com/)のようなツールは、クライアントに対して型とコードを作成するために存在します。
`Strawberry`のコード生成機能は、異なるツールをインストールする必要なしに、同様の問題に対処することを目的としています。

## プラグインシステム

`Strawberry`のコード生成はプラグインをサポートしており、上記例において`python`のプラグインを使用しています。
コード生成ツールに多くのプラグインを渡すために、`-p`フラグを使用できます。

```sh
strawberry codegen --schema schema --output-dir ./output -p python -p typescript query.graphql
```

プラグインは、Pythonのパスとして指定できます。

## カスタムプラグイン

プラグインのインターフェイスは次のようになっています。

```python
from strawberry.codegen import CodegenPlugin, CodegenFile, CodegenResult
from strawberry.codegen.types import GraphQLType, GraphQLOperation


class QueryCodegenPlugin:
    def __init__(self, query: Path) -> None:
        """プラグインを初期化します。

        1つの引数は、このプラグインによって処理されるファイルへのパスです。
        """
        self.query = query

    def on_start(self) -> None:
        ...

    def on_end(self, result: CodegenResult) -> None:
        ...

    def generate_code(
        self, types: List[GraphQLType], operation: GraphQLOperation
    ) -> List[CodegenFile]:
        return []
```

1. `on_start`はコード生成が開始する前に呼び出されます。
2. `on_end`はコード生成が終了して、コード生成から結果を受け取った後に呼び出されます。
   これをコードをフォーマットするため、またはファイルにライセンスを追加するなどできます。
3. `generate_code`はコード生成が開始して型と操作を受け取ったときに呼び出されます。
   これをそれぞれの型と操作に対してコードを生成するために使用できます。

## コンソールプラグ民

コード生成プロセスを調整して、現在のコード生成処理がしていることをを通知することを支援するプラグインもあります。

コンソールプラグインのインターフェイスは次のようになります。

```python
class ConsolePlugin:
    def __init__(self, output_dir: Path):
        """プラグインを初期化して、出力が書き込まれる場所を伝えます。"""
        ...

    def before_any_start(self) -> None:
        """このメソッドは任意のプラグインが呼び出されるか、任意のクエリが処理された後に呼び出されます。"""
        ...

    def after_all_finished(self) -> None:
        """このメソッドはすべてのコード生成が完了した後に呼び出されます。

        コード生成の間に発生したすべてのことをリポートするたために使用できます。
        """
        ...

    def on_start(self, plugins: Iterable[QueryCodegenPlugin], query: Path) -> None:
        """このメソッドは任意の個々のプラグインが開始される前に呼び出されます。"""
        ...

    def on_end(self, result: CodegenResult) -> None:
        """通常、このメソッドは1つのクエリから出力ディレクトリに結果を永続化します。"""
        ...
```

`orchestrate`:【動詞】作曲する、編曲する、調整する、組織化する、画策する

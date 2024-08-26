# Relayガイド

## Relayとは

`Relay`仕様は、クライアントがより効率的な方法でサーバーと相互作用するために、GraphQLサーバーが従ういくつかのインターフェイスを定義しています。
その仕様は、GraphQLサーバーについて2つの主要な仮定をしています。

1. それはオブジェクトを再取得するための機構を提供します。
2. それは接続を介してページングする方法を説明します。

`Relay`仕様についての詳細は[ここ](https://relay.dev/docs/guides/graphql-server-specification/)を読んでください。

## Relay実装例

次の型があることを想定します。

```python
@strawberry.type
class Fruit
    name: str
    weight: str
```

`Fruit`にグローバルに一意なID、ページ分割された結果リストを取得する方法、そして必要に応じて再取得する方法が必要です。
そのために、`Fruit`が`Node`インターフェイスを継承して、`GlobalID`生成に使用される属性に`relay.NodeID`で注釈して、`resolve_nodes`抽象メソッドを実装する必要があります。

```python
import strawberry
from strawberry import relay


@strawberry.type
class Fruit(relay.Node):
    code: relay.NodeId[int]
    name: str
    weight: float

    @classmethod
    def resolve_nodes(
        cls, *, info: strawberry.Info, node_ids: Iterable[str], required: bool = False,
    ):
        return [
          all_fruits[int(nid)] if required else all_fruits.get(nid)
          for nid in node_ids
        ]

# この例において、フルーツコードをフルーツオブジェクト自身にマッピングする辞書を持っていると想定しています。
all_fruits: Dict[int, Fruit]
```

ここで何をしているか説明します。

1. `relay.NodeID[int]`を使用してコードを注釈しています。
   これは、`code`を[プライベート](https://strawberry.rocks/docs/types/private)型にして、それはGraphQL APIに公開されず、`Fruit`型に対して`id: GlobalID!`を生成するためにその値を使用すべきであることを`Node`インターフェイスに伝えています。
2. また、`resolve_nodes`抽象メソッドを実装しています。
   このメソッドは、与えられたその`id`で`Fruit`インスタンを取得する責任を持ちます。
   `code`がidであるため、`node_ids`は文字列としてコードのリストになります。

---

注意事項

`GlobalID`は、base64エンコードした文字列`<TypeName>:<NodeID>`を得ることで生成されます。
上記例において、`1`をコードとして持つ`Fruit`は、`base64("Fruit:1") = RnJaXQ6MQ==`としてその`GlobalID`を持ちます。

---

これで、取得とページ分割のためにスキーマでそれを公開できます。

```python
@strawberry.type
class Query:
    node: relay.Node = relay.node()

    @relay.connection(relay.ListConnection[Fruit])
    def fruits(self) -> Iterable[Fruit]:
        # これは、データベース問い合わせ、ジェネレーター、非同期ジェネレーターなどにできます。
        return all_fruits.values()
```

これは次のスキーマを生成します。

```graphql
scalar GlobalID

interface Node {
  id: GlobalID!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Fruit implements Node {
  id: GlobalID!
  name: String!
  weight: Float!
}

type FruitEdge {
  cursor: String!
  node: Fruit!
}

type FruitConnection {
  pageInfo: PageInfo!
  edges: [FruitEdge]!
}

type Query {
  node(id: GlobalID!): Node!
  fruits(
    before: String = null
    after: String = null
    first: Int = null
    last: Int = null
  ): FruitConnection!
}
```

これだけで、スキーマ内で任意の`Node`を実装した型（`Fruit`型を含む）を取得するために`node`を問い合わせる方法と、ページ区切りを使用してフルーツのリストする方法を持ちました。

例えば、そのユニークなIDを与えて単独のフルーツを取得するためには、次のクエリを実行します。

```graphql
query {
  node(id: "<some id>") {
    id
    ... on Fruit {
      name
      weight
    }
  }
}
```

または存在する最初のフルーツ10個を取得するためには、次のクエリを実行します。

```graphql
query {
  fruits(first: 10) {
    pageInfo {
      firstCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      # ここのノードはFruit型です。
      node {
        id
        name
        weight
      }
    }
  }
}
```

`relay.ListConnection`のためのコネクションリゾルバーは、次の1つを返さなくてはなりません。

1. `List[<NodeType>]`
2. `Iterator[<NodeType>]`
3. `Iterable[<NodeType>]`
4. `AsyncIterator[<NodeType>]`
5. `AsyncIterable[<NodeType>]`
6. `Generator[<NodeType>, Any, Any]`
7. `AsyncGenerator[<NodeType>, Any, Any]`

## ノードフィールド

上記実演に置いて、`Node`フィールドは`Node`インターフェイスを実装したスキーマ内の任意のオブジェクトを取得／再取得するために使用されます。

それは、4つの方法で`Query`オブジェクト内に定義されます。

1. `node: Node`: これは`GlobalID!`を受け取り、`Node`インスタンスを返すフィールドを定義します。
   これはそれを定義する最も基本的な方法です。
2. `node: Optional[Node]`: `Node`と同じですが、もし与えられたオブジェクトが存在しない場合、それは`null`を返します。
3. `node: List[Node]`: これは`[GlobalID!]!`を受け取り、`Node`インスタンスのリストを返すフィールドを定義します。
4. `node: List[Optional[Node]]`: `List[Node]`と同じですが、もし与えられたオブジェクトが存在しない場合、返されるリストは`null`値を含みます。

## カスタムコネクションページネーション

デフォルトの`relay.Connection`クラスは、任意のページネーションロジックを実装していないため、独自のページネーションロジックを実装した基本クラスとして使用されなくてはなりません。
行う必要があるすべてのことは、`resolve_connection`クラスメソッドを実装することです。

統合は`relay.ListConnection`を提供していて、それは結果をページ区切りするために限界／オフセット手法を実装しています。
これは、基本的な手法で、ほとんどのユースケースで十分かもしれません。

---

注意事項

`relay.ListConnection`は、スライスを使用することによって限界／オフセットを実装しています。
それは、ノードのリゾルバーによって返されたオブジェクトの`__getitem__`メソッドをカスタマイズすることで、スライスする方法を上書きできることを意味します。

例えば、`Django`を使用する場合、`resolve_nodes`は`QuerySet`を返して、`QuerySet`のスライスはSQLクエリの`LIMIT`／`OFFSET`に翻訳され、データベースから必要とされるデータのみを取得することを意味します。

また、もしオブジェクトが`__getitem__`属性を持っていない場合、`relay.ListConnection`はページ区切りするために`itertools.islice`を使用して、それはジェネレーターが解決されるとき、ジェネレーターは与えられたページ区切りに必要なだけの結果を生成して、最悪のシナリオは返される必要のある最後の結果になります。

---

ここで、前の例で、独自のカーソルに基づいたページネーションを実装しなくてはならないことを想定します。
次のようにできます。

```python
import strawberry
from strawberry import relay


@strawberry.type
class FruitCustomPaginationConnection(relay.Connection[Fruit]):
    @classmethod
    def resolve_connection(
        cls,
        nodes: Iterable[Fruit],
        *,
        info: Optional[Info] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None
    ):
    # 注意事項: これは実装の展示であり、性能良く最適化されていません。
    edges_mapping = {
        relay.to_base64("fruit_name", n.name): relay.Edge(
            node=n,
            cursor=relay.to_base64("fruit_name", n.name),
        )
        for n in sorted(nodes, key=lambda f: f.name)
    }
    edges = list(edges_mapping.values())
        first_edge = edges[0] if edges else None
        last_edge = edges[-1] if edges else None

        if after is not None:
            after_edge_idx = edges.index(edges_mapping[after])
            edges = [e for e in edges if edges.index(e) > after_edge_idx]

        if before is not None:
            before_edge_idx = edges.index(edges_mapping[before])
            edges = [e for e in edges if edges.index(e) < before_edge_idx]

        if first is not None:
            edges = edges[:first]

        if last is not None:
            edges = edges[-last:]

        return cls(
            edges=edges,
            page_info=strawberry.relay.PageInfo(
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
                has_previous_page=(
                    first_edge is not None and bool(edges) and edges[0] != first_edge
                ),
                has_next_page=(
                    last_edge is not None and bool(edges) and edges[-1] != last_edge
                ),
            ),
        )


@strawberry.type
class Query:
    @relay.connection(FruitCustomPaginationConnection)
    def fruits(self) -> Iterable[Fruit]:
        # This can be a database query, a generator, an async generator, etc
        return all_fruits.values()
```

上記例において、`relay.Connection[Fruit]`から継承することで`FruitCustomPaginationConnection`を特殊化しました。
それを`relay.Connection[relay.NodeType]`から継承することでジェネリックを維持して、フィールドを定義するときに特殊化することで、カスタムページネーションロジックを1つ以上の型に使用することを可能にします。

## カスタムコネクション引数

デフォルトで、コネクションは、結果をページ区切りできるようにするために、自動的にいくつかの引数を挿入します。

1. `before`: 指定されたカーソルの前のリスト内のアイテムを返します。
2. `after`: 指定されたカーソルの後のリスト内のアイテムを返します。
3. `first`: リストから最初の`n`個のアイテムを返します。
4. `last`: リストから最後の`n`個のアイテムを返します。

> `after=<cursor>&first=<n>`の場合は、前方へ（コレクションの末尾に向かって）ページ区切りして、`<cursor>`で示されたリスト内の位置より後の、最初の`<n>`個のアイテムを返す。
> `before=<cursor>&last=<n>`の場合は、後方へ（コレクションの前方に向かって）ページ区切りして、`<cursor>`で示されたリスト内の位置より前の、最初の`<n>`個のアイテムを返す。

独自のリゾルバーやカスタムページネーションロジックによって使用される追加の引数を定義することもできます。
例えば、名前が与えられた文字列で開始するすべてのフルーツをページ区切りして返すことを想定します。
それは次のようにできます。

```python
@strawberry.type
class Query:
    @relay.connection(relay.ListConnection[Fruit])
    def fruits_with_filter(
        self,
        info: strawberry.Info,
        name_startswith: str,
    ) -> Iterable[Fruit]:
        for f in fruits.values():
            if f.name.startswith(name_startswith):
                yield f
```

これは次のようなスキーマを生成します。

```graphql
type Query {
  fruitsWithFilter(
    nameStartswith: String!
    before: String = null
    after: String = null
    first: Int = null
    last: Int = null
  ): FruitConnection!
}
```

## コネクションが解決されたときにノードを適切な型に変換する

コネクションは、リゾルバーが`NodeType`のサブクラスのオブジェクトのリストを返すことを想定しています。
しかし、ORMモデルのように、適切な型に変換する必要があるものを解決する状況があるかもしれません。

この場合、`relay.Connection`／`relay.ListConnection`をサブクラス化して、それにデフォルトでノードをそのまま返す独自の`resolve_node`メソッドを提供します。

```python
import strawberry
from strawberry import relay

from db import models


# ORMモデル
class Fruit(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    weight = models.FloatField()


# relayノード
@strawberry.type
class FruitDB(relay.Node):
    code: relay.NodeID[int]
    name: str
    weight: float


@strawberry.type
class FruitDBConnection(relay.ListConnection[Fruit]):
    @classmethod
    def resolve_node(cls, node: FruitDB, *, info:strawberry.Info, **kwargs) -> Fruit:
        return Fruit(
            code=node.code,
            name=node.name,
            weight=node.weight,
        )


@strawberry.type
class Query:
    @relay.connection(FruitDBConnection)
    def fruits_with_filter(
        self,
        info:strawberry.Info,
        name_endswith:str,
    ) -> Iterable[models.Fruit]:
        return Fruit.objects.filter(name__endswith=name_endswith)
```

カスタムリゾルバーの中で変換する代わりに、この手法を使用する主な利点は、まず`Connection`は`QuerySet`をページ区切りします。
Djangoの場合、ページ分割された結果のみがデータベースから取得されることを保証します。
その後、`resolve_node`関数が、正確なオブジェクトを取得するために、それぞれの結果に対して呼び出されます。

この例ではDjangoを使用しましたが、同じことは、SQLAlchemyなど他の同様なユースケースでも適用できます。

## GlobalIDスカラー

`GlobalID`スカラーは、`Node`インターフェイスを実装した与えられたオブジェクトを識別して取得するために必要なすべての情報を含んだ特別なオブジェクトです。

例えば、それはミューテーションで受け取り、オブジェクト化して、そのリゾルバーないで取得するときに便利です。

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_fruit_weight(
        self,
        info: strawberry.Info,
        id: relay.GlobalID,
        weight: float,
    ) -> Fruit:
        # resolve_nodeはFruitオブジェクトを返すawaitableを返します。
        fruit = await id.resolve_node(info, ensure_type=Fruit)
        fruit.weight = weight
        return fruit

    @strawberry.mutation
    def update_fruit_weight_sync(
      self,
      info: strawberry.Info,
      id: relay.GlobalID,
      weight: float,
    ) -> Fruit:
        # resolve_nodeはFruitオブジェクトを返します。
        fruit = id.resolve_node_sync(info, ensure_type=Fruit)
        fruit.weight = weight
        return fruit
```

上記例において、`id_type_name`で型名に、`id.id`で生のノードIDに直接アクセスでき、また`id.resolve_type(info)`で型それ自身も解決できます。

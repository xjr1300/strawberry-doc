# 列挙型

列挙型は、特定の値の集合に制限する特別な種類の型です。

例えば、いくつかアイスクリームの選択肢があり、そしてユーザーにそれらの選択肢から1つを選択させる必要がある場合です。

`Strawberry`は、Pythonの標準ライブラリにある列挙型を使用して列挙型を定義することをサポートしています。
ここに、`Strawberry`で列挙型を作成する方法を簡単に示します。

最初に、新しい方のために新しいクラスを作成して、それは`Enum`クラスを拡張します。

```python
from enum import Enum


class IceCreamFlavour(Enum):
    ...
```

そして、クラス内に変数として選択肢をリスとします。

```python
class IceCreamFlavour(Enum):
    VANILLA = "vanilla"
    STRAWBERRY = "strawberry"
    CHOCOLATE = "chocolate"
```

最後に、`Strawberry`の型としてっクラスを登録する必要があります。
それは、`@strawberry.enum`デコレーターで行われます。

```python
@strawberry.enum
class IceCreamFlavour(Enum):
    VANILLA = "vanilla"
    STRAWBERRY = "strawberry"
    CHOCOLATE = "chocolate"
```

スキーマで列挙型を使用する方法を確認しましょう。

```python
@strawberry.type
class Query:
    @strawberry.field
    def best_flavour(self) -> IceCreamFlavour:
        return IceCreamFlavour.STRAWBERRY
```

上記で定義された列挙型は、次のGraphQLスキーマを生成します。

```graphql
enum IceCreamFlavour {
  VANILLA
  STRAWBERRY
  CHOCOLATE
}
```

ここに、この新しく作成したクエリを使用する方法の例を示します。

```graphql
query {
  bestFlavour
}
```

ここに、クエリを実行した結果を示します。

```json
{
  "data": {
    "bestFlavour": "STRAWBERRY"
  }
}
```

また、オブジェクト型（`@strawberry.type`を使用した）を定義するときにも列挙型を使用できます。
ここに`Enum`を使用したフィールドを持つオブジェクトの例を示します。

```python
@strawberry.type
class Cone:
    flavour: IceCreamFlavour
    num_scoops: int


@strawberry.type
class Query:
    @strawberry.field
    def cone(self) -> Cone:
        return Cone(flavour=IceCreamFlavour.STRAWBERRY, num_scoops=4)
```

そして、ここにこのクエリを使用する方法の例を示します。

```graphql
query {
  cone {
    flavour
    numScoops
  }
}
```

ここにクエリの結果を示します。

```json
{
  "data": {
    "cone": {
      "flavor": "STRAWBERRY",
      "numScoops": 4
    }
  }
}
```

---

注意事項

GraphQLの型は、Pythonの列挙型のように、`name: value`のマップではありません。
`Strawberry`はGraphQL型を作成するために列挙型のメンバーの名前を使用します。

---

また、列挙型の値を廃止できます。
それを行うために、`@strawberry.enum_value`と`@deprecation_reason`を使用したより長い構文が必要です。
文字列と長い構文を混ぜて使用できます。

```python
@strawberry.enum
class IceCreamFlavour(Enum):
    VANILLA = strawberry.enum_value("vanilla")
    CHOCOLATE = "chocolate"
    STRAWBERRY = strawberry.enum_value(
        "strawberry",
        deprecation_reason="Let's call the whole thing off"
    )
```

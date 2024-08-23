# スキーマディレクティブ

`Strawberry`は[スキーマディレクティブ](https://spec.graphql.org/June2018/#TypeSystemDirectiveLocation)をサポートしており、それはGraphQLスキーマの動作を変更しませんが、代わりにスキーマに追加のメタデータを追加する方法を提供するディレクティブです。

> 例えば、`Apollo`フェデレーション統合は、スキーマディレクティブに基づいています。

`Strawberry`でスキーマディレクティブを実装する方法を確認します。
ここで、[オブジェクト型の定義](https://strawberry.rocks/docs/types/object-types)に適用される`keys`と呼ばれるディレクトリを作成して、`fields`と呼ばれる1つの引数を受け付けます。
デフォルトで、ディレクティブの名前はGraphQLスキーマでキャメルケースに変換されることに注意してください。

スキーマ内でスキーマディレクティブを使用する方法を次に示します。

```python
import strawberry
from strawberry.schema_directive import Location


@strawberry.schema_directive(locations=[Location.OBJECT])
class Keys:
    fields: str
```

```python
from .directives import Keys


@strawberry.type(directives=[Keys(fields="id")])
class User:
    id: strawberry.ID
    name: str
```

これは次のスキーマになります。

```graphql
type User @keys(fields: "id") {
  id: ID!
  name: String!
}
```

## フィールド名の上書き

フィールドの名前を上書きするために`strawberry.directive_field`を使用できます。

```python
@strawberry.schema_directive(locations=[Location.OBJECT])
class Keys:
    fields: str = strawberry.directive_field(name="as")
```

## 場所

スキーマディレクティブはスキーマのさまざまな部分に適用できます。
ここに、すべての許可されば場所をリスとします。

| 名前 | 指定方法 | 説明 |
| --- | --- | --- |
| SCHEMA | `strawberry.schema` | スキーマの定義 |
| SCALAR | `strawberry.scaler` | スカラーの定義 |
| OBJECT | `strawberry.type` | オブジェクト型の定義 |
| FIELD_DEFINITION | `strawberry.field` | オブジェクト型またはインターフェイスのフィールドの定義 |
| ARGUMENT_DEFINITION | `strawberry.argument` | 引数の定義 |
| INTERFACE | `strawberry.interface` | インターフェイスの定義 |
| UNION | `strawberry.union` | ユニオンの定義 |
| ENUM | `strawberry.enum` | 列挙型の定義 |
| ENUM_VALUE | `strawberry.enum_value` | 列挙型の値の定義 |
| INPUT_OBJECT | `strawberry.input` | 入力オブジェクト型の定義 |
| INPUT_FIELD_DEFINITION | `strawberry.input_field` | 入力オブジェクト型のフィールドの定義 |

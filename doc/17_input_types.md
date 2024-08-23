# 入力型

オブジェクト型に加えてGraphQLは入力型もサポートしています。
オブジェクト型に似ている一方で、入力型はフィールドに使用できる型の種類を制限する入力データに適しています。

次はGraphQL仕様がオブジェクト型と入力型の違いを定義する方法です。

> GraphQLオブジェクト型は、引数に定義されるかインターフェイスとユニオンへの参照を含み、どちらも入力引数として使用されないため、入力として再利用するために不適切です。

## 入力型の定義

`Strawberry`において、次のように`@strawberry.input`デコレーターを使用して入力型を定義できます。

```python
import strawberry


@strawberry.input
class Point2D:
    x: float
    y: float
```

```graphql
input Point2D {
  x: Float!
  y: Float!
}
```

これで、フィールドまたはミューテーションの引数として入力型を使用できます。

```python
import strawberry


@strawberry.type
class Mutation:
    @strawberry.mutation
    def store_point(self, a: Point2D) -> bool:
        return True
```

オプションの引数を含めたい場合、それらのデフォルトを提供する必要があります。
例えば、上記例を拡張して、ポイントのラベルをオプションにしたい場合、次のようにできます。

```python
import strawberry
from typing import Optional


@strawberry.input
class Point2D:
    x: float
    y: float
    label: Optional[str] = None
```

```graphql
type Point2D {
  x: Float!
  y: Float!
  label: String = null
}
```

代わりに、`None`のデフォルト値の代わりに`strawberry.UNSET`も使用でき、それはスキーマでフィールドをオプションにします。

```python
from typing import Optional

import strawberry


@strawberry.input
class Point2D:
    x: float
    y: float
    label: Optional[str] = strawberry.UNSET
```

```graphql
type Point2D {
  x: Float!
  y: Float!
  label: String
}
```

## API

```python
@strawberry.input(name: str = None, description: str = None)
```

クラス定義から入力型を作成します。

1. `name`: これが設定されている場合はGraphQLの名前になり、設定されていない場合はクラス名をキャメルケースにすることで名前が生成されます。
2. `description`: これはスキーマを内観したとき、またはGrapiQLを使用してスキーマを案内するときに返されるGraphQLの説明です。

## 1つの入力型

`Strawberry`はフィールド集合の1つのみを持つ入力型も定義することをサポートしています。
これは[1つの入力オブジェクトRFC](https://github.com/graphql/graphql-spec/pull/825)に基づいています。

1つの入力型を定義するために、`@strawberry.input`デコレーターに`one_of`フラグを使用できます。

```python
import strawberry


@strawberry.input(one_of=True)
class SearchBy:
    name: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
```

```graphql
input SearchBy @oneOf {
  name: String
  email: String
}
```

## 廃止フィールド

`@strawberry.deprecation_reason`デコレーター引数を使用して、フィールドを廃止できます。

---

注意事項

これはフィールドが使用されることを妨げず、ドキュメントのためだけです。
[GraphQLフィールドの廃止](https://spec.graphql.org/June2018/#sec-Field-Deprecation)を参照してください。

---

```python
from typing import OPtional

import strawberry


@strawberry.input
class Point2D:
    x: float
    y: float
    z: Optional[float] = strawberry.field(deprecation_reason="3D coordinates are deprecated")
    label: Optional[str] = strawberry.UNSET
```

```graphql
input Point2D {
  x: Float!
  y: Float!
  z: Float @deprecated(reason: "3D coordinates are deprecated")
  label: String
}
```

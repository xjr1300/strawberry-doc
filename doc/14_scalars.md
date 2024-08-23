# スカラー

スカラー型はクエリのリーフにある具体的な値を表現します。
例えば、次のクエリ内の`name`フィールドはスカラー型に解決されます（この場合それは`String`型です）。

```graphql
{
  user {
    name
  }
}
```

```json
{
  "data": {
    "user": {
      "name": "Patrick"
    }
  }
}
```

組み込みのスカラーがいくつかあり、また独自のスカラーも定義できます。
[Enum](https://strawberry.rocks/docs/types/enums)もリーフの値です。
組み込みのスカラーを次に示します。

1. `String`: Pythonの`str`にマップします。
2. `Int`: 符号付き32ビット整数で、Pythonの`int`にマップします。
3. `Float`: 符号付き倍精度浮動小数点数で、Pythonの`float`にマップします。
4. `Boolean`: trueまたはfalseで、Pythonの`bool`にマップします。
5. `ID`: 一意なオブジェクトの識別子を表現する特別な`String`です。
6. `Date`: `date`をISO-8601にエンコードしたものです。
7. `DateTime`: `datetime`をISO-8601にエンコードしたものです。
8. `Time`: `time`をISO-8601にエンコードしたものです。
9. `Decimal`: 文字列としてシリアライズされた`Decimal`値です。
10. `UUID`: 文字列としてシリアライズされた`UUID`値です。
11. `Void`: 常にnullで、Pythonの`None`にマップします。
12. `JSON`: [ECMA-401]標準に指定されたJSON文字列で、Pythonの`dict`にマップします。
13. `Base16`、`Base32`、`Base64`: `Base16`/`Base32`/`Base64`でエンコードされた16進数文字列を表現します。`RFC4648`で指定されています。Pythonの`str`にマップします。

フィールドは、Pythonで等価なものを使用することで、組み込みスカラーを返せます。

```python
import datetime
import decimal
import uuid

import strawberry


@strawberry.type
class Product:
    id: uuid.UUID
    name: str
    stock: int
    is_available: bool
    available_from: datetime.date
    same_day_shipping_before: datetime.time
    created_at: datetime.datetime
    price decimal.Decimal
    void: None
```

```graphql
type Product {
  id: UUID!
  name: String!
  stock: Int!
  isAvailable: Boolean!
  availableFrom: Date!
  sameDayShippingBefore: Time!
  createdAt: DateTime!
  price: Decimal!
  void: Void
}
```

また、スカラー型は入力としても使用されます。

```python
import datetime
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def one_week_from(self, date_input: datetime.date) -> datetime.date:
        return date_input + datetime.timedelta(weeks=1)
```

## カスタムスカラー

データモデルの具体的な方を表現するために、スキーマでカスタムスカラーを作成できます。
これは、特定のフィールドでどのような種類のデータを期待できるかを、クライアントが知ることに役立ちます。

カスタムスカラーを定義するために、型をシリアライズそしてデシリアライズする方法を`Strawberry`に伝える名前と関数を与える必要があります。

例えば、ここにBase64文字列を表現するカスタムスカラー型を示します。

```python
import base64
from typing import NewType


Base64 = strawberry.scaler(
    NewType("Base64", bytes),
    serialize=lambda v: base64.b64encode(v).decode("utf-8"),
    parse_value=lambda v: base64.b64decode(v.encode("utf-8")),
)


@strawberry.type
class Query:
    @strawberry.field
    def base64(self) -> Base64:
        return Base64(b"hi")


schema = strawberry.Schema(Query)

result = schema.execute_sync("{ base 64 }")

assert result.date == {"base64":"aGk="}
```

---

注意事項

`Base16`、`Base32`そして`Base64`スカラー型は、`strawberry.scalers`で利用できます。

```python
from strawberry.scalars import Base16, Base32, Base64
```

---

## JSONスカラーの例

```python
import json
from typing import Any, NewType

import strawberry


JSON = strawberry.scalar(
    NewType("JSON", object),
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
```

使用方法

```python
@strawberry.type
class Query:
    @strawberry.field
    def data(self, info) -> JSON
        return {"hello": {"a": 1}, "someNumbers": [1, 2, 3]}
```

```graphql
query ExampleDataQuery {
  data
}
```

```json
{
  "data": {
    "hello": {
      "a": 1
    },
    "someNumbers": [1, 2, 3]
  }
}
```

---

注意事項

`JSON`スカラー型は`strawberry.scalars`内にあります。

```python
from strawberry.scalars import JSON
```

---

## 組み込みスカラーの上書き

組み込みスカラの動作を上書きするために、上書きをマップをスキーマに渡すことができます。

ここに、すべての日付をUNIXタイムスタンプにシリアライズする組み込みの`DateTime`スカラーを置き換える完全な例を示します。

```python
from datetime import datetime, timezone

import strawberry


# カスタムスカラーを定義
EpochDateTime = strawberry.scalar(
    datetime,
    serialize=lambda value: int(value.timestamp()),
    parse_value=lambda value: datetime.fromtimestamp(int(value), timezone.utc),
)


@strawberry.type
class Query:
    @strawberry.field
    def current_time(self) -> datetime:
        return datetime.now()


schema = strawberry.Schema(
    Query,
    scalar_overrides={
        datetime: EpochDateTime,
    },
)

result = schema.execute_sync("{ currentTime }")
assert result.date == {"currentTime": 1628683200}
```

## datetimeを人気のあるpendulumライブラリに置き換え

`pendulum`インスタンスで上書きするために、上記例のようにシリアル化して値を解析する必要があります。
今回は、クラス内にそれらを投げてみます。

加えて、`Union`句を使用して、可能な入力型を組み合わせます。
`pendulum`はまだ型付けされていないため、`# type: ignore`を使用して`numpy`のエラーを黙らせる必要があります。

```python
import pendulum
from datetime import datetime


class DateTime:
    """
    このクラスはpendulum.DateTimeを文字列に変換して、また文字列からpendulum.DateTmeに戻すために使用されます。
    """

    @staticmethod
    def serialize(dt: Union[pendulum.DateTime, datetime]) -> str:  # type: ignore
        try:
            return dt.isoformat()
        except ValueError:
            return dt.to_iso8601_string() # type: ignore

    @staticmethod
    def parse_value(value: str) -> Union[pendulum.DateTime, datetime]:  # type: ignore
        return pendulum.parse(value)   # type: ignore


date_time = strawberry.scalar(
    Union[pendulum.DateTime, datetime],  # type: ignore
    serialize=DateTime.serialize,
    parse_value=DateTime.parse_value,
)
```

### BigInt

デフォルトでPythonは整数のサイズを2^64にすることができる。
しかし、GraphQLの仕様は2^32に制限されています。

これは必然的にエラーを引き起こす。
回避策としてクライアントで文字列を使用する代わりに、次のスカラーを使用できます。

```python
# GraphQLは64ビット整数をサポートしていないため、これが必要とされています。
BigInt = strawberry.scalar(
    Union[int, str],  # type: ignore
    serialize=lambda v: int(v),
    parse_value=lambda v: str(v),
    description="BigInt field",
)
```

`scalar_overrides`引数を使用することで、すべての整数について自動的にこのスカラーを使用するために、スキーマに結合できます。

---

用例

ほとんどの整数が64ビットであることが予想される場合のみ、このオーバーライドを使用してください。
ほとんどのGraphQLスキーマは標準的な設計パターンに従い、ほとんどのクライアントは文字列としてすべての数値を処理する追加的な努力を要求するため、32ビットの制限を実際に超える数値のためにBigIntを予約するほうが合理的です。
大きなPythonの数値を処理するリゾルバー内で`int`の代わりに`BigInt`で注釈することにより、これを達成できます。

---

```python
user_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    scalar_overrides={datetime: date_time, int: BigInt}
)
```

`inevitably`:【副詞】必然的に、必ず、予期した通り
`adapt`:【動詞】適応させる、合わせて変える、変更する、適合させる、順応する

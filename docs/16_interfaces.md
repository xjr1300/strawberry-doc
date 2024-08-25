# インターフェイス

インターフェイスは抽象型で、オブジェクト型によって実装されます。

インターフェイスはフィールドを持ちますが、それは決してインスタンス化されません。
代わりに、インターフェイスを実装したオブジェクトは、そのインターフェイスのメンバーにします。
また、フィールドはインターフェイス型を返すかもしれません。
これが発生したとき、返却されたオブジェクトはそのインターフェイスの任意のメンバーかもしれません。

例えば、`Customer`（インターフェイス）が`Individual`（オブジェクト）と`Company`（オブジェクト）のどちらかになることができるとします。
ここに、GraphQLスキーマ定義言語（SDL）でそれがどのように見えるか示します。

```graphql
interface Customer {
  name: String!
}

type Company implements Customer {
  employees: [Individual!]!
  name: String!
}

type Individual implements Customer {
  employed_by: Company
  name: String!
}

type Query {
  customers: [Customer!]!
}
```

`Customer`インターフェイスが`name: String!`フィールドを要求することに注意してください。
`Company`と`Individual`の両方は、`Customer`インターフェイスを満足するためにそのフィールドを実装しています。

問い合わせしたとき、インターフェイス上のフィールドを選択できます。

```graphql
query {
  customers {
    name
  }
}
```

オブジェクトが`Company`または`Individual`かどうかであっても、それは問題にならずそれらの名前を得ます。
もし、オブジェクト特有のフィールドが必要な場合、[インラインフラグメント](https://graphql.org/learn/queries/#inline-fragments)でそれらを問い合わせできます。

```graphql
query {
  customers {
    name
    ... on Individual {
      # company {
      employed_by {
        name
      }
    }
  }
}
```

互換性のあるオブジェクトの集合がある場合、インターフェイスは良い選択で、それらは一般的ないくつかのフィールドを持ちます。
一般的なフィールドを持たないとき、代わりに[Union](https://strawberry.rocks/docs/types/union)を使用します。

## インターフェイスの定義

`@strawberry.interface`デコレーターを使用してインターフェイスを定義できます。

```python
import strawberry


@strawberry.interface
class Customer:
    name: str
```

```graphql
interface Customer {
  name: String!
}
```

---

注意事項

インターフェイスクラスは直接インスタンス化されるべきではありません。

---

## インターフェイスの実装

インターフェイスを実装したオブジェクト型を定義するために、型はインターフェイスから派生されなければなりません。

```python
import strawberry


@strawberry.type
class Individual(Customer):
    # 追加のフィールド
    ...


@strawberry.type
class Company(Customer):
    # 追加のフィールド
    ...
```

---

用法

インターフェイスを実装するオブジェクト型を追加しますが、そのオブジェクト型がフィールドの戻り値の型またはユニオンのメンバーとしてスキーマ内に現れていない場合、直接スキーマ定義をそのオブジェクトに追加する必要があります。

```python
schema = strawberry.Schema(query=Query, types=[Individual, Company])
```

---

また、インターフェイスは、他のインターフェイスを実装できます。

```python
import strawberry


@strawberry.interface
class Error:
    message: str


@strawberry.interface
class FieldError(Error):
    message: str
    field: str


@strawberry.type
class PasswordTooShort(FieldError):
    message: str
    field: str
    min_Length: int
```

```graphql
interface Error {
  message: String!
}

interface FieldError implements Error {
  message: String!
  field: String!
}

type PasswordTooShort implements FieldError {
  message: String!
  field: String!
  minLength: Int!
}
```

## フィールドの実装

インターフェイスはフィールドの実装を十分に提供できます。

```python
import strawberry


@strawberry.interface
class Customer:
    @strawberry.field
    def name(self) -> str:
        return self.name.title()
```

このリゾルブメソッドは、インターフェイスを実装したオブジェクトによって呼び出されます。
オブジェクトクラスは、それら自身の`name`フィールドを定義することによって、実装をオーバーライドできます。

```python
import strawberry


@strawberry.type
class Company(Customer):
    @strawberry.field
    def name(self) -> str:
        return f"{self.name} Limited"
```

## インターフェイスの解決

フィールドの戻り値の型がインターフェイスのとき、GraphQLは戻り値の型に使用する具体的なオブジェクト型を知る必要があります。
上記例において、それぞれの顧客は`Individual`または`Company`として分類されなければなりません。
これを行うために、リゾルバーからオブジェクト型のインスタンスを常に返す必要があります。

```python
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def best_customer(self) -> Customer:
        return Individual(name="Patrick")
```

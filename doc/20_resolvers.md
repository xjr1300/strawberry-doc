# リゾルバー

GraphQLスキーマを定義するとき、通常APIのスキーマの定義で開始します。
例えば、このスキーマを確認しましょう。

```python
import strawberry


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    last_user: User
```

```graphql
type User {
  name: String!
}

type Query {
  lastUser: User!
}
```

`User`型と`Query`型を定義しました。
次に、サーバーからデータを返す方法を定義するために、フィールドにリゾルバーを付けます。

## リゾルバーの定義

リゾルバーを作成して`lastUser`フィールドにそれを付けましょう。
リゾルバーはPythonの関数で、それはデータを返します。
`Strawberry`において、リゾルバーを定義する2つの方法があります。
1つ目は、次の通りフィールド定義に関数を渡します。

```python
def get_last_user() -> User:
    return User(name="Marco")


@strawberry.type
class Query:
    last_user: User = strawberry.field(resolver=get_last_user)
```

これで、`Strawberry`が次のクエリを実行したとき、`Strawberry`は`lastUser`フィールドのデータを取得する`get_last_user`関数を呼び出します。

```graphql
{
  lastUser {
    name
  }
}
```

```json
{
  "data": {
    "lastUser": {
      "name": "Marco"
    }
  }
}
```

## メソッドとしてリゾルバーを定義

リゾルバーを定義する別の方法は、次のようにデコレーターとして`strawberry.field`を使用することです。

```python
@strawberry.type
class Query:
    @strawberry.field
    def last_user(self) -> User:
        return User(name="Marco")
```

これは、リゾルバーと型を一緒に配置したいとき、またはとても小さなリゾルバーがあるときに便利です。

---

注意事項

もしリゾルバーで`self`引数が機能する方法に興味があれば、[親データのアクセスガイド](https://strawberry.rocks/docs/guides/accessing-parent-data)を参照してください。

---

## 引数の定義

フィールドも引数を持てます。
`Strawberry`において、フィールドの引数はリゾルバーで定義されるため、Pythonの関数で通常行う通りです。
IDによってユーザーを返すクエリのフィールドを定義しましょう。

```python
import strawberry


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> User:
        # ここでデータベースからユーザーを取得するために`id`を使用します。
        return User(name="Marco")
```

```graphql
type User {
  name: String!
}

type Query {
  user(id: ID!): User!
}
```

## オプション引数

オプショナルまたはnull許可引数は、`Optional`を使用して表現されます。
もし、`null`（Pythonの`None`にマップ）と引数がないことを区別して渡す必要がある場合、`UNSET`を使用できます。

```python
from typing import Optional

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: Optional[str] = None) -> str:
        if name is None:
            return "Hello world!"
        return f"Hello {name}!"

    @strawberry.field
    def greet(self, name: Optional[str] = strawberry.UNSET) -> str:
        if name is strawberry.UNSET:
            return "Name was not set!"
        if name is None:
            return Name was null!"
        return f"Hello {name}!"
```

```graphql
type Query {
  hello(name: String = null): String!
  greet(name: String): String!
}
```

このようにすると、次のようなレスポンスを受け取ります。

```graphql
{
  unset: greet
  null: greet(name: null)
  name: greet(name: "Dominique")
}
```

```json
{
  "data": {
    "unset": "Name was not set!",
    "null": "Name was null!",
    "name": "Hello Dominique!"
  }
}
```

## 実行情報にアクセス

時々、現在実行中のコンテキストの情報にアクセスすることは便利です。
`Strawberry`は、自動的にリゾルバーに渡される`Info`型のパラメーターを宣言できるようにします。
この引数は、現在実行中のコンテキストを含んでいます。

```python
import strawberry
from strawberry.types import Info


def full_name(root: "User", info: strawberry.Info) -> str:
    return f"{root.first_name} {root.last_name} {info.field_name}"


@strawberry.type
class User:
    first_name: str
    last_name: str
    full_name: str = strawberry.field(resolver=full_name)
```

---

用法

このパラメーターを`info`と呼ぶ必要はなく、名前はどれでも構いません。
`Strawberry`はリゾルバーに正しい値を渡すために型を使用します。

---

## API

`Info`オブジェクトは現在実行中のコンテキストの情報を含んでいます。

```python
class Info(Generic[ContextType, RootValueType])
```

| 引数名 | 型 | 説明 |
| --- | --- | --- |
| field_name | `str` | 現在のフィールドの名前（一般的にキャメルケース） |
| python_name | `str` | フィールドの「Python名」（一般的にスネークケース） |
| context | `ContextType` | コンテキストの値 |
| root_value | `RootValueType` | ルート型の値 |
| variable_values | `Dict[str, Any]` | この操作の変数 |
| operation | `OperationDefinitionNode` | 現在の操作のAST（公開APIは将来変更するかもしれません） |
| path | `Path` | 現在のフィールドのパス |
| selected_fields | `List[SelectedField]` | 現在のフィールドに関連した追加情報 |
| schema | `Schema` | `Strawberry`のスキーマインスタンス |

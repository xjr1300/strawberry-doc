# オブジェクト型

オブジェクト型はGraphQLスキーマの基盤で、それらはスキーマ内に存在するオブジェクトの種類を定義するために使用されます。
オブジェクト型は名前とフィールドのリストを定義することによって作成されます。
GraphQLスキーマ言語を使用して定義されたオブジェクト型の例をここに示します。

```graphql
type Character {
  name: String!
  age: Int!
}
```

## クエリ、ミューテーションそしてサブスクリプションのメモ

GraphQLについて読んでいる間、`Query`、`Mutation`そして`Subscription`の3つの特別なオブジェクト型に遭遇したかもしれません。
それらは標準オブジェクト型として定義され、スキーマのエントリーポイントとして使用される点が異なります（ルート型として参照されます）。

1. `Query`はすべての問い合わせ操作のエントリーポイントです。
2. `Mutation`はすべての変更のエントリーポイントです。
3. `Subscription`はすべてのサブスクリプションのエントリーポイントです。

スキーマを定義する方法については、[スキーマの基本](https://strawberry.rocks/docs/general/schema-basics)を読んでください。

## オブジェクト型の定義

`Strawberry`において、次のように`@strawberry.type`デコレータを使用してオブジェクト型を定義できます。

```python
import strawberry


@strawberry.type
class Character:
    name: str
    age: int
```

```graphql
type Character {
  name: String!
  age: Int!
}
```

次のように他の型を参照できます。

```python
import strawberry


@strawberry.type
class Character:
    name: str
    age: int


@strawberry.type
class Book:
    title: str
    main_character: Character
```

```graphql
type Character {
  name: String!
  age: Int!
}

type Book {
  title: String!
  mainCharacter: Character!
}
```

## API

```python
@strawberry.type(name: str = None, description: str = None)
```

クラス定義からオブジェクト型を作成します。

`name`: 設定されている場合GraphQLの名前になり、そうでない場合は、GraphQLはクラスの名前をキャメルケースにすることで名前を生成します。

`description`: これはスキーマが内省されたとき、またはGraphiQLを使用してスキーマを案内するときに返されるGraphQLの説明です。

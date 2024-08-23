# ジェネリックス

`Strawberry`は再利用可能な型を動的に作成するために、Pythonの`Generic`タイピングをサポートします。

`Strawberry`はジェネリック型と型引数の組み合わせから正確なGraphQLスキーマを自動的に生成します。
ジェネリックスは、オブジェクト型、入力型、そしてクエリの引数、ミューテーションそしてスカラーでサポートされています。

例を確認しましょう。

## オブジェクト型

```python
from typing import Generic, List, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.type
class Page(Generic[T]):
    number: int
    items: List[T]
```

この例は、任意の型のページを表現するために使用できる`Page`ジェネリック型を定義します。
例えば、`User`オブジェクトのページを作成できます。

```python
import strawberry


@strawberry.type
class User:
    name: str


@strawberry.type
class Query:
    users: Page[User]
```

```graphql
type Query {
  users: UserPage!
}

type User {
  name: String!
}

type UserPage {
  number: Int!
  items: [User!]!
}
```

また、直接特別なジェネリック型を使用することもできます。
例えば、上の同じ例は次のように記述されます。

```python
import strawberry


@strawberry.type
class User:
    name: str


@strawberry.type
class UserPage(Page[User]):
    ...


@strawberry.type
class Query:
    users: UserPage
```

```graphql
type Query {
  users: UserPage!
}

type User {
  name: String!
}

type UserPage {
  number: Int!
  items: [User!]!
}
```

## 入力と引数型

クエリとミューテーションへの引数は、ジェネリックな入力型を作成することでジェネリックにできます。
ここに、何らかの集合として低ｋ票できる入力型を定義して、ミューテーションで引数を埋めることを使用して、特殊化を作成します。

```python

from typing import Generic, List, Optional, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.input
class CollectionInput(Generic[T]):
    values: List[T]


@strawberry.input
class PostInput:
    name: str


@strawberry.type
class Post:
    id: int
    name: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_posts(self, posts: CollectionInput[PostInput]) -> bool:
        return True


@strawberry.type
class Query:
    most_recent_post: Optional[Post] = None


schema = strawberry.Schema(query=Query, mutation=Mutation)
```

```graphql
input PostInputCollectionInput {
  values: [PostInput!]!
}

input PostInput {
  name: String!
}

type Post {
  id: Int!
  name: String!
}

type Query {
  mostRecentPost: Post
}

type Mutation {
  addPosts(posts: PostInputCollectionInput!): Boolean!
}
```

---

注意事項

`CollectionInput`と`PostInput`の両方が入力型である事実に注意を払ってください。
`posts: CollectionInput[Post]`を`add_posts`に提供することは、エラーになります（例えば、入力型でない`Post`型を使用すること）。

```text
PostCollectionInput fields cannot be resolved. Input field type must be aGraphQL input type
```

---

## 複数の特殊化

ジェネリック型の複数の特殊化を使用することは予期したように機能します。
ここに、`Point2D`型を定義して、`int`と`float`の両方に特殊化します。

```python
from typing import Generic, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.input
class Point2D(Generic[T]):
    x: T
    y: T


@strawberry.type
class Mutation:
    @strawberry.mutation
    def store_line_float(self, a: Point2D[float], b: Point2D[float]) -> bool:
        return True

    @strawberry.mutation
    def store_line_int(self, a: Point2D[int], b: Point2D[int]) -> bool:
        return True
```

```graphql
type Mutation {
  storeLineFloat(a: FloatPoint2D!, b: FloatPoint2D!): Boolean!
  storeLineInt(a: IntPoint2D!, b: IntPoint2D!): Boolean!
}

input FloatPoint2D {
  x: Float!
  y: Float!
}

input IntPoint2D {
  x: Int!
  y: Int!
}
```

## 可変数引数のジェネリック

[PEP-646](https://peps.python.org/pep-0646/)で導入された可変数引数のジェネリックは、現在サポートしていません。

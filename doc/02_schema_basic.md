# スキーマの基本

GraphQLサーバーはデータの形状を説明するためにスキーマを使用します。
スキーマはデータストアから生まれるフィールドを持つ型の階層を定義します。
また、スキーマはクライアントが実行できるクエリとミューテーションが存在することを性格に説明します。

このガイドはスキーマの基本的な構成要素と、`Strawberry`でそれを作成する方法を説明します。

## スキーマ定義言語（SDL）

GraphQLサーバーでスキーマを作成する方法が2つあります。
1つ目は「スキーマファースト」と呼ばれるもので、その他は「コードファースト」と呼ばれます。
`Strawberry`はコードファーストなスキーマのみをサポートします。
コードファーストに深入りする前に、スキーマ定義言語が何か説明します。

スキーマファーストは、GraphQLのスキーマ定義言語を使用して機能して、それはGraphQLの仕様に含まれています。

SDLを使用して定義されたスキーマの例を次に示します。

```graphql
type Book {
  title: String!
  author: Author!
}

type Author {
  name: String!
  books: [Book!]!
}
```

スキーマはすべての型とそれらの間の関連を定義します。
これを使用することで、クライアント側の開発者に、どのデータが利用できて、そのデータの具体的なサブセットをリクエストすることを正確に確認できるようにします。

---

注意事項

`!`記号はフィールドが非nullであることを示しています。

---

スキーマはデータを取得する方法を説明していないことに注意してください。
それは、後でリゾルバーを定義するときに説明します。

## コードファーストアプローチ

前に言及した通り、`Strawberry`はコードファーストアプローチを使用します。
前のスキーマは、`Strawberry`において次のように見えます。

```python
import typing
import strawberry


@strawberry.type
class Book:
    title: str
    author: "Author"


@strawberry.type
class Author:
    name: str
    books: typing.List[Book]
```

確認できるように、Pythonの型ヒント機能のおかげて、コードはスキーマとほぼ1対1でマッピングされています。

ここでもデータを取得する方法を指定していないことに注意してください。
それはリゾルバーのセクションで説明されます。

## サポートされている型

GraphQLはいくつかの型をサポートしています。

1. スカラー型
2. オブジェクト型
3. クエリ型
4. ミューテーション型
5. 入力型

## スカラー型

スカラー型はPythonの基本的な型に似ています。
GraphQLのデフォルトのスカラー型のリストを次に示します。

1. `Int`: 符号付き32ビット整数で、Pythonの`int`にマッピングします。
2. `Float`: 符号付き倍精度浮動小数点数の値で、Pythonの`float`にマッピングします。
3. `String`: Pythonの`str`にマッピングします。
4. `Boolean`: 真または偽で、Pythonの`bool`にマッピングします。
5. `ID`: 通常、オブジェクトを再取得、またはキャッシュのキーとして使用される一意な識別子です。
   文字列としてシリアライズされ、`strawberry.ID("value")`として利用します。
6. `UUID`: `UUID`値で文字列としてシリアライズされます。

---

注意事項

`Strawberry`は、`date`、`time`そして`datetime`のサポートを含み、それらは公式にGraphQL仕様に含まれていませんが、通常それらはほとんどのサーバーに必要とされています。
それらは`ISO-8601`としてシリアライズされます。

---

## オブジェクト型

GraphQLスキーマ内で定義するほとんどの型は、オブジェクト型です。
オブジェクト型は、フィールドのコレクションを含み、それらそれぞれはスカラー型か他のオブジェクト型です。

オブジェクト型は、前に定義したスキーマのように、互いに参照されます。

```python
import typing
import strawberry


@strawberry.type
class Book:
    title: str
    author: "Author"

@strawberry.type
class Author:
    name: str
    books: typing.List[Book]
```

## フィールドにデータを提供する

前のスキーマにおいて、`Book`は`author`フィールドを持ち、`Author`は`books`フィールドを持ちます。
しかし、約束されたスキーマの構造を満たすためにデータをマッピングする方法を理解していません。

これを成し遂げるために、関数を介してフィールドにデータを提供する**リゾルバー**の概念を導入します。

本と著者の例で続けると、リゾルバーはフィールドに値を提供するために定義されます。

```python
def get_author_for_book(root) -> "Author":
    return Author(name="Michael Crichton")


@strawberry.type
class Book:
    title: str
    author: "Author" = strawberry.field(resolver=get_author_for_book)


def get_books_for_author(root) -> typing.List[Book]:
    return [Book(title="Jurassic Park")]


@strawberry.type
class Author:
    name: str
    books: typing.List[Book] = strawberry.filed(resolver=get_books_for_author)


def get_authors(root) -> typing.List[Author]:
    return [Author(name="Michael Crichton")]


@strawberry.type
class Query:
    authors: typing.List[Author] = strawberry.field(resolver=get_authors)
    books: typing.List[Book] = strawberry.field(resolver=get_books_for_author)
```

これらの関数は、リクエストに応じてデータをGraphQLクエリにレンダリングする能力を持ち、すべてのGraphQL APIの中枢となる`strawberry.field`を提供します。

解決されたデータが完全に静的なため、この例は些細です。
しかし、より複雑なAPIを構築するとき、例えばSQLAlchemyとその他のAPI、例えばaiohttpを使用したHTTPリクエストを作成するなど、これらのリゾルバーは、データベースからデータをマッピングするように記述できます。

リゾルバーを記述するさまざまな方法の詳細については、リゾルバーのセクションを参照してください。

## クエリ型

`Query`型は、どのGraphQLクエリ（例えば、読み込み操作）をクライアントがデータに対して実行できるかを正確に定義します。
`Query`型は、オブジェクト型と似ていますが、その名前は常に`Query`です。

`Query`型のそれぞれのフィールドは、名前と様々なサポートされたクエリの戻り値を定義しています。
スキーマ例の`Query`型は、次に似ているかもしれません。

```python
@strawberry.type
class Query:
    books: typing.List[Book]
    authors: typing.List[Author]
```

この`Query`型は、`books`と`authors`の2つの利用できるクエリを定義しています。
それぞれのクエリは対応する型のリストを返します。

REST形式のAPIにおいて、多分`books`と`authors`は異なるエンドポイントによって返されます（例: `/api/books`と`/api/authors`）。
GraphQLの柔軟性は、クライアントが1つのリクエストで両方のリソースを問い合わせすることを可能にします。

`resemble`:【動詞】似ている

### クエリの構築

クライアントがデータグラフに対して実行するクエリを構築するとき、それらのクエリはスキーマで定義したオブジェクト型の形状と一致します。

これまでのスキーマ例に基づいて、クライアントはすべての本のタイトルのリストとすべての著者の名前のリストの両方をリクエストする次のクエリを実行できます。

```graphql
query {
  books {
    title
  }
  authors {
    name
  }
}
```

サーバーは、次の用にクエリの構造と一致した結果でクエリに応答します。

```json
{
  "data": {
    "books": [{ "title": "Jurassic Park" }],
    "authors": [{ "name": "Michael Crichton" } ]
  }
}
```

これら2つの分離したリストを取得するケースでは便利かもしれませんが、多分クライアントは本のリスト1つを取得することを好み、それぞれの本の著者はその結果内に含められます。

スキーマの`Book`型は`Author`型の`author`フィールドを持つため、クライアントは次のようなクエリを構築できます。

```graphql
query {
  books {
    title
    author {
      name
    }
  }
}
```

そしてもう一度、サーバーはクエリの構造に一致した結果で応答します。

```json
{
  "data": {
    "books": [
      { "title": "Jurassic Park", "author": { "name": "Michael Crichton" } }
    ]
  }
}
```

## ミューテーション型

`Mutation`型は構造と目的が`Query`型と似ています。
`Query`型はデータのサポートされた読み込み操作を定義する一方で、`Mutation`型はサポートされた書き込み操作を定義します。

`Mutation`型のそれぞれのフィールドはシグネチャーと様々な変更の戻り値を定義します。
スキーマ令の`Mutation`型は次に似ているかもしれません。

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title, str, author: str) -> Book:
        ...
```

この`Mutation`型は、`addBook`という単独の利用可能な変更を定義します。
その変更はタイトルと著者の2つの引数を受け付け、新しく作成された`Book`オブジェクトを返します。
予想した通り、この`Book`オブジェクトはスキーマ内で定義された構造と一致します。

`whereas`:【接続詞】〜であるのに対して、〜である一方で、〜という事実から見れば
`conform`:【動詞】一致する、同じである、〜を〜と一致させる（to, with）、従う、順応する、準拠する、適合する

---

注意事項

`Strawberry`は、デフォルトでフィールド名をスネークケースからキャメルケースに変換します。
これは、**スキーマで独自のStrawberryConfig`**を指定することで変更できます。

---

## ミューテーションの構築

クエリと同様に、ミューテーションはスキーマの型定義の構造と一致します。
次のミューテーションは新しい`Book`を作成して、戻り値として作成されたオブジェクトの特定のフィールドをリクエストします。

```graphql
mutation {
  addBook(title: "Fox in Socks", author: "Dr. Seuss") {
    title
    author {
      name
    }
  }
}
```

クエリのように、サーバーはこのミューテーションに対して、次のようなミューテーションの構造と一致した結果で応答します。

```json
{
  "data": {
    "addBook": {
      "title": "Fox in Socks",
      "author": {
        "name": "Dr. Seuss"
      }
    }
  }
}
```

## 入力型

入力型はクエリまたはミュテーションに引数としてオブジェクトを渡す特別なオブジェクト型です（スカラー型のみを渡すこととは対照的に）。
入力型は操作の署名を簡潔に維持することを支援します。

本を追加する前のミューテーションを考えます。

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        ...
```

2つの変数を受け取る代わりに、このミューテーションはこれらのフィールドをすべて含む1つの入力型を受け付けることができます。
これは、将来、発行日のような追加の引数を受け取ることを決定したとき、とても便利になります。

入力型の定義はオブジェクト型の定義と似ていますが、それは`input`キーワードを使用します。

```python
@strawberry.input
class AddBookInput:
    title: str
    author: str

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, book: AddBookInput) -> Book:
        ...
```

これはスキーマ内に`AddBookInput`型を渡すことを手助けするだけでなく、それはGraphQLに対応したツールによって自動的に公開される説明でフィールドを注釈する基盤を提供します。

```python
@strawberry.input
class AddBookInput:
    title: str = strawberry.field(description="The title of the book")
    author: str = strawberry.field(description="The name of the author")
```

複数の操作が正確に同じ情報の集合を要求するとき、入力型は時々便利になりますが、それらの再利用は控えめにするべきです。
最終的に、操作はそれらに要求された引数の集合に別れるかもしれません。

> クエリやミューテーションに入力型を利用する場合、それらが正確に同じ引数を要求しても、クエリやミューテーションそれぞれの入力型を定義することが推奨される。

`facilitate`:【動詞】容易にする、楽にする、手助けする
`sparingly`:【副詞】控えめに、節約して、わずかに、かろうじて
`diverge`:【動詞】別れる、分岐する、異なる、外れる、発散する

## さらに

確信できるスキーマ設計についてより学びたい場合、[Apolloによって提供されるドキュメント](https://www.apollographql.com/docs/apollo-server/schema/schema/#growing-with-a-schema)に従ってください。

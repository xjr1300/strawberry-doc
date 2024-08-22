# ミューテーション

クエリと対照的に、GraphQLのミューテーションはサーバー側のデータを変更して、さらに／または、サーバーで副作用を引き起こす操作を表現します。
例えば、アプリケーションに新しいインスタンスを作成するミューテーション、またはEメールを送信するミューテーションを持てます。
クエリと同様に、ミューテーションは引数を受け付け、新しい型や既存のオブジェクト型を含め、通常のフィールドで可能な何かを返します。
これは、更新した後のオブジェクトの新しい状態を取得するために便利です。

「チュートリアルを始める」からきた書籍プロジェクトを改善して、本を追加することを想定したミューテーションを実装します。

```python
import strawberry

# 読者の皆さん、この例のクエリを安全に無視できます。
# それはstrawberry.Schemaによって要求されるため、完全性のためにここに含まれています。
@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "world"


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        print(f"Adding {title} by {author}")

        return Book(title=title, author=author)


schema = strawberry.Schema(query=Query, mutation=Mutation)
```

> 上記コードで、クエリ型を無視して良いと記述しているのは、GraphQLのライブラリほとんどが
> クエリ型をデフォルトのエントリポイントとして扱うため、スキーマを定義するときにクエリを
> 必須とするためである。
> GraphQLの仕様には、クエリ型が必須であるという定めはなく、クエリ、ミューテーションまたは
> サブスクリプションのうち少なくとも1つのオペレーション型を持つことを定めている。
> 例えば、書き込み専用のアプリケーションであれば、ミューテーションだけでスキーマを定義しても良い。

クエリと同様に、ミューテーションは、後でスキーマ関数に渡されるクラス内に定義されます。
ここでは、タイトルと著者を受け付け、`Book`型を返す`addBook`ミューテーションを作成しました。

次のGraphQLドキュメントを、ミューテーションを実行するためにサーバーに送信します。

<!-- cspell: disable -->
```graphql
mutation {
  addBook(title: "The Little Prince", author: "Antoine de Saint-Exupéry") {
    title
  }
}
```
<!-- cspell: enable -->

`addBook`ミューテーションは単純化した例です。
実際のアプリケーションにおいて、ミューテーションはよくエラーを処理して、クライアントにそれらのエラーを伝える必要があります。
例えば、本がすでに存在した場合にエラーを返すことができます。

ミューテーションからユニオン型を返す方法を学ぶために、[エラーを扱う](https://strawberry.rocks/docs/guides/errors#expected-errors)を確認してください。

## 戻り値のないミューテーション

何も返さないミューテーションを記述できます。

これは、GraphQLのスカラーである`Void`にマッピングされ、常に`null`を返します。

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def restart() -> NOne:
        print("Restarting the server")
```

```graphql
mutation {
  restart: Void
}
```

---

注意事項

結果が`void`になるミューテーションは、[コミュニティーが作成したガイドラインであるGQLベストプラクティス](https://graphql-rules.com/rules/mutation-payload)に反します。

---

## 入力ミューテーションの拡張

`input`と呼ばれる[入力型](https://strawberry.rocks/docs/types/input-types)引数を1つ受け取るミューテーションを定義するパターンを使用することは便rにです。

`Strawberry`は、リゾルバーの引数と同じ属性を持つ入力型を自動的に作成するミューテーションを作成するためのヘルパーを提供します。

例えば、上記セクションで定義されたミューテーションを入力ミューテーションにすること想定します。
次のように`InputMutationExtension`をフィールドに追加できます。

```python
from strawberry.field_extensions import InputMutationExtension


@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    def update_fruit_weight(
        self,
        info: strawberry.Info,
        id: strawberry.ID,
        weight: Annotated[
            float,
            strawberry.argument(description="The fruit's new weight in grams"),
        ],
    ) -> Fruit:
        fruit = ...   # 与えられたIDでフルーツを取得する。
        fruit.weight = weight
        ... # おそらくデータベース内にフルーツを保存する。
        return fruit
```

上記は次のスキーマを生成します。

```graphql
input UpdateFruitWeightInput {
  id: ID!
  """
  フルーツの新しいグラム単位の重さ
  """
  weight: Float!
}

type Mutation {
  updateFruitWeight(input: UpdateFruitWeightInput!): Fruit!
}
```

## ネストしたミューテーション

グラフがあまりに大きくなることを避け、発見可能性を改善するために、[関心の分離によって名前空間を作成するApolloガイド](https://www.apollographql.com/docs/technotes/TN0012-namespacing-by-separation-of-concern/)によって説明された名前空間内にミューテーションをグループ化すると便利です。

> ここにおける名前空間は`FruitMutations`を示す。

```python
type Mutation {
  fruit: FruitMutations!
}

type FruitMutations {
  add(input: AddFruitInput): Fruit!
  updateWeight(input: UpdateFruitWeightInput!): Fruit!
}
```

すべてのGraphQLの操作はフィールドであるため、`FruitMutation`型を定義して、ルート`Mutation`型にミューテーションフィールドを追加するように、ミューテーションフィールドをそれに追加できます。

```python
import strawberry


@strawberry.type
class FruitMutations:
    @strawberry.mutation
    def add(self, info, input: AddFruitInput) -> Fruit:
        ...

    @strawberry.mutation
    def update_weight(self, info, input: UpdateFruitWeightInput) -> Fruit:
        ...


@strawberry.type
class Mutation:
    @strawberry.field
    def fruit(self) -> FruitMutations:
        return FruitMutations()
```

---

注意事項

ルート`Mutation`型のフィールドは連続的に解決されます。
データを変更するミューテーションフィールドはもはやルートレベルにないため、名前空間型はミューテーションが非同期かつ並行で解決される可能性があります。

名前空間型が使用されたときに連続実行を保証するために、クライアントは、それぞれのミューテーションに対応するルートミューテーションフィールドを選択するためにエイリアスを使用しなくてはなりません。
次の例において、一旦、`addFruit`実行が完了したら、`updateFruitWeight`が開始します。

> ここにおける名前空間のエイリアスとは、次の`addFruit`や`updateFruitWeight`を示す。

```graphql
mutation (
  $addFruitInput: AddFruitInput!
  $updateFruitWeightInput: UpdateFruitWeightInput!
) {
  addFruit: fruit {
    add(input: $addFruitInput) {
      id
    }
  }

  updateFruitWeight: fruit {
    updateWeight(input: $updateFruitWeightInput) {
      id
    }
  }
}
```

詳細については、[シリアルミューテーションの名前空間に関するApolloのガイドと、Rapid APIのGraphQLクエリの対話型ガイド: エイリアスと変数](https://www.apollographql.com/docs/technotes/TN0012-namespacing-by-separation-of-concern/#namespaces-for-serial-mutations)を参照してください。

---

`discoverability`:【名詞】発見可能性
`serially`:【副詞】連続して、連続的に

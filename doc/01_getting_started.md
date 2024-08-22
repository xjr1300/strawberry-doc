# Strawberryをはじめる

このチュートリアルは次を支援します。

1. GraphQLの原則の基本的な理解を得る。
2. `Strawberry`を使ってGraphQLスキーマを定義する。
3. スキーマに対してクエリを実行する`Strawberry`サーバーを起動する。

このチュートリアルは、コマンドラインとPythonに慣れている人と、最新バージョンのPython(3.8+)がインストールされていることを想定しています。

`Strawberry`は`Python`の`dataclasses`と`type hints`機能の上に構築されています。

## ステップ1: 新しいプロジェクトを作成と`Strawberry`のインストール

新しいフォルダーを作成します。

```sh
mkdir strawberry-demo
cd strawberry-demo
```

その後、新しい仮想環境が必要です。

```sh
python -m venv .venv
```

仮想環境をアクティブにした後、デバッグサーバー付きの`strawberry`をインストールします。

```sh
source .venv/bin/activate
pip install 'strawberry-graphql[debug-server]'
```

## ステップ2: スキーマの定義

すべてのGraphQLサーバーはクライアントが問い合わせできるデータ構造を定義するスキーマを使用します。
この例では、本のコレクションをタイトルと著者によって問い合わせするサーバーを作成します。

好みのエディター内で、次の内容を持つ`schema.py`と呼ばれるファイルを作成します。

```python
import typing

import strawberry  # type: ignore


@strawberry.type
class Book:
    title: str
    author: str


@strawberry.type
class Query:
    books: typing.List[Book]
```

これは、クライアントが、ゼロ以上の本のリストを返す`books`と名付けられたクエリを実行できるGraphQLスキーマを作成します。

## ステップ3: データセットの定義

これで、スキーマの構造ができたため、データを定義できます。
`Strawberry`は、例えばデータベース、REST API、ファイルなどの任意のデータソースと一緒に機能できます。
このチュートリアルでは、ハードコートされたデータを使用します。

いくつかの本を返す関数を作成します。

```python
def get_books():
    return [
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
        )
    ]
```

`Strawberry`は、スキーマを作成するためにPythonのクラスを使用するため、これはデータオブジェクトを作成するためにそれらを再利用できることを意味します。

## ステップ4: リゾルバーの定義

これで、いくつかの本を返す関数を持ちましたが、`Strawberry`はクエリを実行するときにそれを使用するべきであることを理解していません。
これを修正するために、本に対する**リゾルバー**を指定するためにクエリを更新する必要があります。
リゾルバーは、特定のフィールドに関係があるデータを取得する方法を`Strawberry`に伝えます。

クエリを更新します。

```python
@strawberry.type
class Query:
    books: typing.List[Book] = strawberry.field(resolver=get_books)
```

`strawberry.field`の使用は、特定のフィールドに対してリゾルバーを指定させます。

----

注意事項

Bookのフィールドに対してリゾルバーを指定する必要はありません。
それは、`Strawberry`がそれぞれのフィールドに対してデフォルトを追加して、そのフィールドの値を返すためです。

----

## ステップ5: スキーマを作成して実行

データとクエリを定義したため、GraphQLスキーマを作成してサーバーを開始する必要があります。

スキーマを追加するために次のコードを追加します。

```python
schema = strawberry.Schema(query=Query)
```

その後、次のコマンドを実行します。

```sh
strawberry server schema
```

これはデバッグ用サーバーを開始して、次の出力を確認できるはずです。

## ステップ6: 最初のクエリを実行

これで、GraphQLクエリを実行できます。
`Strawberry`は`GraphiQL`と呼ばれるツールと一緒に提供されます。
`GraphiQL`を開くために、`http://0.0.0.0:8000/graphql`にアクセスしてください。

次のようなものが確認できるはずです。

![GraphiQL](https://strawberry.rocks/_astro/index-server.vEXctPmd_ZYfLjO.webp)

GraphiQLは次を含んでいます。

1. クエリを記述するテキストエリア（左側）
2. クエリを実行する実行ボタン（中央の三角ボタン）
3. スキーマを内省するためにクエリ結果を確認するテキストエリア（右側）と、生成されたドキュメント（左側のタブを介して）

サーバーは`books`と名付けられた1つのクエリを想定しています。
それを実行します。

次の文字列を左側のエリアに貼り付けて、プレイボタンをクリックします。

```graphql
{
  books {
    title
    author
  }
}
```

右側に表示されたハードコートされたデータを確認できるはずです。

![result of books query](https://strawberry.rocks/_astro/index-query-example.apr0tLHb_2pxEMp.webp)

GraphQLはクライアントに対して、クライアントが必要とするフィールドのみを問い合わせさせるため、クエリから`author`を削除した後、それを再度実行してください。
レスポンスは、それぞれの本のタイトルのみを表示するはずです。

## 次のステップ

よくできました！
`Strawberry`を使用して最初のGraphQL APIを作成しました。
GraphQLと`Strawberry`についてより学ぶために、次のリソースを確認してください。

1. スキーマの基本
2. リゾルバー
3. デプロイメント

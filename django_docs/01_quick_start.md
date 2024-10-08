# クイックスタート

このクイックスタートでは、次を行います。

1. 関連を持った基本的なモデルのペアを準備します。
2. それらにGraphQLスキーマを追加して、GraphQL APIを提供します。
3. モデルコンテンツのためにGraphQL APIを問い合わせします。

ミューテーションと多くのクエリの集合を含んだ似たような準備をもつより高度な例については、[example app](https://github.com/strawberry-graphql/strawberry-django/tree/main/examples/django)を確認してください。

## インストール

```sh
mkdir strawberry-django-demo && cd strawberry-django-demo
poetry add strawberry-graphql-django
poetry add django-choices-field  # 必要ではありませんが推奨されます。
```

poetryを使用していない場合、`pip install strawberry-graphql-django`もきちんと機能します。

## アプリケーションのモデルの定義

フルーツとそれらの色のデータベースを構築します。

---

💡 Tip

`Fruit.category`のために、`TextFiled(choices=...)`の代わりに`TextChoicesField`を使用していくことに気づくでしょう。
これは、`strawberry-django`に、GraphQLスキーマで、`TextField`に対してデフォルトの振る舞いをする文字列に変わって、列挙型を自動的に使用させるようにします。

詳細は[選択フィールドの統合](https://strawberry.rocks/docs/django/integrations/choices-field)を参照してください。

---

```sh
poetry run django-admin startproject demo .
poetry run python manage.py startapp fruits
```

```python
# fruits/models.py
from django.db import models
from django_choices_field import TextChoicesField


class FruitCategory(models.TextChoices):
    CITRUS = "citrus", "柑橘類"
    BERRY = "berry", "ベリー類"


class Fruit(models.Model):
    """おいしい果物"""

    name = models.CharField(max_length=20, help_text="果物の品種名")
    category = TextChoicesField(choices_enum=FruitCategory, help_text="果物の分類")
    color = models.ForeignKey(
        "Color",
        on_delete=models.CASCADE,
        related_name="fruits",
        blank=True,
        null=True,
        help_text="この種類の果物の色",
    )


class Color(models.Model):
    """おいしい果物の色合い"""

    name = models.CharField(
        max_length=20,
        help_text="色の名前",
    )
```

マイグレーションを作成して、マイグレートする必要があります。

```python
 # demo/settings.py

 INSTALLED_APPS = [
     "django.contrib.admin",
     "django.contrib.auth",
     "django.contrib.contenttypes",
     "django.contrib.sessions",
     "django.contrib.messages",
     "django.contrib.staticfiles",
+    "fruits.apps.FruitsConfig",
 ]
```

```sh
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

これで、Djangoの`shell`、`admin`、`loaddata`コマンドまたはいくつかの果物と色をロードする好みのツールを使用できます。
赤いイチゴを積んでおいたので（予想通りですよね？！）、後で使えるように準備しました。

```json
// fruits/fixtures/colors.json
[
  { "model": "fruits.color", "pk": 1, "fields": { "name": "赤" } },
  { "model": "fruits.color", "pk": 2, "fields": { "name": "小紫" } }
]
```

```json
// fruits/fixtures/fruits.json
[
  {
    "model": "fruits.fruit",
    "pk": 1,
    "fields": { "name": "いちご", "category": "berry", "color": 1 }
  },
  {
    "model": "fruits.fruit",
    "pk": 2,
    "fields": { "name": "ラズベリー", "category": "berry", "color": 1 }
  },
  {
    "model": "fruits.fruit",
    "pk": 3,
    "fields": { "name": "ブルーベリー", "category": "berry", "color": 2 }
  }
]
```

```sh
poetry run python manage.py loaddata fruits/fixtures/colors.json
poetry run python manage.py loaddata fruits/fixtures/fruits.json
```

## 型の定義

クエリを作成する雨に、それぞれのモデルの`type`を定義する必要があります。
`type`はスキーマの基礎的なユニットであり、GraphQLサーバーから問い合わせされるデータの形状を説明します。
型はスカラー値（文字列、整数、論理値、浮動小数点そしてID）、列挙型、または多くのフィールドで構成される複雑なオブジェクトを表現します。

---

💡 Tip

`strawberry-graphql-django`の鍵となる機能は、モデルフィールドから型（そしてドキュメントも！！）を自動的に類推することにより、Djangoモデルから型を作成するヘルパーを提供します。

詳細は[フィールドガイド](https://strawberry.rocks/docs/django/guide/fields)を参照してください。

---

```python
# fruits/types.py
import strawberry_django
from strawberry import auto

from . import models


@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    category: auto
    color: "Color"  # Strawberryは、これが次に定義された"Color"型を参照することを理解します。


@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: list[
        Fruit
    ]  # これはFruitモデルへのForeignKeyであることと、その関連でFruitインスタンスを表現する方法をStrawberryに伝えます。
```

## クエリとスキーマの構築

次に、建築ブロックである型からスキーマを組み立てる必要があります。

---

⚠ 警告

見慣れた文`fruits: list[Fruit]`に気付くでしょう
前のステップの`types.py`内この文をすでに使用しました。
GraphQLと`Strawberry`を初めて理解するときに、それを2回見ることは混乱する可能性があります。

この目的は似ていますが、少し異なります。
以前の構文では、`Color`から`Fruit`のリストまで、グラフ内を横断するクエリを作成できると定義しました。
ここでは、その使用方法は、[ルートクエリ](https://strawberry.rocks/docs/general/queries)を定義します（グラフへのエントリーポイントに少し似ています）。

---

---

💡 Tip

ここで、`DjangoOptimizerExtension`を追加します。
現在のところ、理由を気にする必要はありませんが、それを必要とすることはほぼ確実です。

詳細は[最適化ガイド](https://strawberry.rocks/docs/django/guide/optimizer)を参照してください。

---

```python
import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from .types import Fruit


@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
)
```

`assemble`:【動詞】集める、集まる、会合する、まとめる、組み立てる

## APIの提供

これで、披露しています。
既存のDjangoアプリケーションはユーザー志向でないモデルのドキュメント文字列とヘルプテキストを持っている可能性があるため、これはデフォルトでは有効ではありません。
しかし、クリーンな状態で開始（または既存のドキュメント文字列とヘルプテキストを徹底的に見直す）した場合、次の準備はAPIのユーザーにとって非常に便利です。

もし、これらを行っていない場合、常にユーザー志向の説明を提供できます。

```python
# demo/settings.py
+STRAWBERRY_DJANGO = {
+    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
+    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
+}
```

```python
 # demo/settings.py
-WSGI_APPLICATION = "demo.wsgi.application"
+ASGI_APPLICATION = "demo.asgi.application"
```

```python
# demo/urls.py
from django.contrib import admin
from django.urls import path
from strawberry.django.views import AsyncGraphQLView

from fruits.schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", AsyncGraphQLView.as_view(schema=schema)),
]
```

これは次のスキーマを生成します。

```graphql
enum FruitCategory {
  CITRUS
  BERRY
}

"""
美味しい果物
"""
type Fruit {
  id: ID!
  name: String!
  category: FruitCategory!
  color: Color
}

type Color {
  id: ID!
  """
  field description
  """
  name: String!
  fruits: [Fruit!]
}

type Query {
    fruit: [Fruit!]!
}
```

`show off`:【動詞】披露する、見せびらかす、引き立てる、よく見せる
`overhaul`:【動詞】徹底的に点検する、徹底的に見直す、

## APIの使用

次でサーバーを起動します。

```sh
poetry run python manage.py runserver
```

そして、ブラウザーで<http://localhost:8000/graphql/>を訪問します。
Djangoによって提供されたGraphQLエクスプローラーを見るはずです。
対話型のクエリツールを使用して、前に追加した果物を問い合わせできます。

![GraphiQL](https://strawberry.rocks/_astro/graphiql-with-fruit.DTJ9EyOy_Z2pOmCT.webp)

```graphql
{
  fruits {
    id
    category
    name
    color {
      id
      name
    }
  }
}
```

## 次のステップ

1. より多くのDjangoの型を定義する
2. それらの型の内部にフィールドを定義する
3. ASGIまたはWSGIを使用してAPIを提供する
4. フィールドのフィルタを定義する
5. フィールドの順番を定義する
6. フィールドのページ分割を定義する
7. スキーマにクエリを定義する
8. スキーマにミューテーションを定義する
9. スキーマにサブスクリプションを定義する
10. 性能を改善するためにクエリオプティマイザーを有効にする
11. 高度なページ区切りとモデルの再取得のためにrelay統合を使用する
12. パーミッションエクステンションを使用してフィールドを保護する
13. スキーマのユニットテストを記述する

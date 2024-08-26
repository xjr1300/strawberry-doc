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


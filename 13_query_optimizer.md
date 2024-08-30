# クエリオプティマイザー

クエリオプティマイザーは、スキーマの性能を改善する必須のエクステンションです。
クエリオプティマイザーは、次をします。

1. 取得するために追加のクエリを要求することを避けるため、クエリによって選択されたすべての外部キー関連で[QuerySet.select_related()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-related)を呼び出します。
2. 取得するために追加のクエリを要求することを避けるため、クエリによって選択されたすべての多対1／多対多関連で[QuerySet.prefetch_related()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#prefetch-related)を呼び出します。
3. 実際に選択されたフィールドに対して、[QuerySet.only()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#only)を呼び出して、データベースのペイロードを削減して、実際に選択されているもののみを要求します。
4. [QuerySet.annotate()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#annotate)を呼び出して、渡された[クエリ式](https://docs.djangoproject.com/en/4.2/ref/models/expressions/)の註釈をサポートします。

これらは、有名な`N+1`問題のように、いくつかの一般的なGraphQLの落とし穴を避けるために、特に便利です。

## エクステンションの有効化

自動最適化は、`strawberry`のスキーマ設定に`DjangoOptimizerExtension`を追加することで有効化されます。

```python
import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension

schema = strawberry.Schema(
    query=Query,
    extensions=[
        ...
        DjangoOptimizerExtension,
        ...
    ]
)
```

## 使用方法

オプティマイザーは、自己内観することで自動的にすべての型の最適化を試みます。
次の例を考えてください。

```python
# models.py
class Artist(models.Model):
    name = models.CharField()


class Album(models.Model):
    name = models.CharField()
    release_date = models.DateTimeField()
    artist = models.ForeignKey("Artist", related_name="albums")


class Song(models.Model):
    name = models.CharField()
    duration = models.DecimalField()
    album = models.ForeignKey("Album", related_name="songs")
```

```python
# types.py
import strawberry_django
from strawberry import auto


@strawberry_django.type(Artist)
class ArtistType:
    name: auto
    albums: list["AlbumType"]
    albums_count: int = strawberry_django.field(annotate=Count("albums"))


@strawberry_django.type(Album)
class AlbumType:
    name: auto
    release_date: auto
    artist: ArtistType
    songs: list["SongType"]


@strawberry_django.type(Song)
class SongType:
    name: auto
    duration: auto
    album_type: AlbumType


@strawberry.type
class Query:
    artist: Artist = strawberry_django.field()
    songs: List[SongType] = strawberry_django.field()
```

`artist`と`songs`を次のようにクエリします。

```graphql
query {
  artist {
    id
    name
    albums {
      id
      name
      songs {
        id
        name
      }
    }
    albumsCount
  }
  song {
    id
    album {
      id
      name
      artist {
        id
        name
        albums {
          id
          name
          release_date
        }
      }
    }
  }
}
```

次のようなORMクエリを生成します。

```python
# "artist"のクエリ
Artist.objects.all().only("id", "name").prefetch_related(
    Prefetch(
        "albums",
        queryset=Album.objects.all().only("id", "name").prefetch_related(
            Prefetch(
                "songs",
                Song.objects.all().only("id", "name"),
            )
        )
    ),
).annotate(
    albums_count=Count("albums")
)

# "songs"のクエリ
Song.objects.all().only(
    "id",
    "album",
    "album__id",
    "album__name",
    "album__release_date",    # これに注意してください。
    "album__artist",
    "album__artist__id",
).select_related(
    "album",
    "album__artist",
).prefetch_related(
    Prefetch(
        "album__artist__albums",
        Album.objects.all().only("id", "name", "release_date"),
    )
)
```

---

ℹ️ ノート

ここで`album__release_date`フィールドは選択されていないにもかかわらず、それは後のクエリでプリフェッチされました。
Djangoのキャッシュはオブジェクトを理解しているため、ここでそれを選択しなければならないか、後で追加のクエリを発します。

---

## 最適化ヒント

ときどき、エクステンションによって自動的に最適化できないカスタムリゾルバーを持つかもしれません。
次の例を確認してください。

```python
# models.py
class OrderItem(models.Model):
    price = models.DecimalField()
    quantity = models.IntegerField()

    @property
    def total(self) -> decimal.Decimal:
        return self.price * self.quantity
```

```python
# types.py
import strawberry_django
from strawberry import auto


@strawberry_django.type(models.OrderItem)
class OrderItemType:
    price: auto
    quantity: auto
    total: auto
```

この場合において、もし`total`のみが要求された場合、`price`と`quantity`の両方の追加の問い合わせを発生させます。
それは、両方の値の取得が、オプティマイザーによって延期されているためです。

この場合の解決は、フィールドを最適化する方法を「オプティマイザーに伝える」ことです。

```python
# types.py
import strawberry_django
from strawberry import auto


@strawberry_django.type(models.OrderItem)
class OrderItemType:
    price: auto
    quantity: auto
    total: auto = strawberry_django.field(only=["price", "quantity"])
```

または、カスタムリゾルバーを使用します。

```python
# types.py
import decimal

import strawberry_django
from strawberry import auto


@strawberry_django.type(models.OrderItem)
class OrderItemType:
    price: auto
    quantity: auto

    @strawberry_django.field(only=["price", "quantity"])
    def total(self, root: models.OrderItem) -> decimal.Decimal:
        return root.price * root.quantity   # または直接root.total
```

次のオプションは、オプティマイザーのヒントとして受け付けられます。

1.`only`: [QuerySet.only()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#only)によってアクセスされる同じ形式のフィールドのリスト。
2. `select_related`: [QuerySet.select_related()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-related)を使用して結合する関連のリスト。
3. `prefetch_related`: [QuerySet.prefetch_related()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#prefetch-related)を使用してプリフェッチする関連のリスト。
   このオプションは、`Callable[[Info], Prefetch]`の形式の文字列または呼び出し可能オブジェクト（例えば、`prefetch_related=[lambda info: Prefetch(...)]`）。
4. `annotate`: [QuerySet.annotate()](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#annotate)を使用して注釈する式の辞書。
   この辞書のキーは文字列で、それぞれの値は[クエリ式](https://docs.djangoproject.com/en/4.2/ref/models/expressions/)または`Callable[[Info], BaseExpression]`の形式の呼び出し可能オブジェクト（例えば`annotate={"total": lambda info: Sum(...)}`）。

## モデルの最適化ヒント（モデル属性）

また、`auto`でかいけつされるようにするために、モデルの`@property`に直接型ヒントを含めることも可能で、GraphQLスキーマは内部のロジックについて気にかける必要はありません。

このために、この統合は市湯尾できる2つのデコレーターを提供しています。

1. `strawberry_django.model_property`: `@property`に似ていますが、最適化ヒントを受け付けます。
2. `strawberry_django.cached_model_property`: `@cached_property`に似ていますが、最適化ヒントを受け付けます。

前のセクションの例は、次のように`@model_property`で記述できます。

```python
# models.py
from strawberry_django import model_property


class OrderItem(models.Model):
    price = models.DecimalField()
    quantity = models.IntegerField()

    @model_property(only=["price", "quantity"])
    def total(self) -> decimal.Decimal:
        return self.price * self.quantity
```

```python
# types.py
import strawberry_django
from strawberry import auto


class OrderItemType:
    price: auto
    quantity: auto
    total: auto
```

これで`total`は、それがその最適化に必要となる情報を含んでいる`@model_property`でデコレーションされた属性を指し示すため、適切に最適化されます。

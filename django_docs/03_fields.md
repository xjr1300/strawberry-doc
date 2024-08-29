# フィールドの定義

---

💡 Tip

性能を改善して、いくつかの一般的な落とし穴に落ちること（例えば、`N+1`問題）を避けるために、[クエリ最適化エクステンション](https://strawberry.rocks/docs/django/guide/optimizer)を有効にすることを強く推奨します。

---

フィールドは、手動または自動型解決のために使用できる`auto`型で定義されます。
すべての基本的なフィールド型とリレーションフィールドは、組み込みでサポートされています。
もし、独自なフィールドを定義したライブラリを使用する場合、`str`、`float`、`bool`、`int`または`id`のような同等な型を定義する必要があります。

```python
# types.py
import strawberry_django
from strawberry import auto


@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto


# strawberryによって類推される同等な型
@strawberry_django.type(models.Fruit)
class Fruit:
    id: strawberry.ID
    name: str
```

---

💡 Tip

[DjangoのTextChoice/IntegerChoice](https://docs.djangoproject.com/en/4.2/ref/models/fields/#enumeration-types)を使用すた選択肢では、列挙型を処理する[django-choice-field](https://strawberry.rocks/docs/django/integrations/choices-field)統合を使用することを推奨します。

## リレーションシップ

1対1、1対多、多対1そして多対多すべてのリレーションシップ型はサポートされており、多対多関連は`typing.List`注釈を使用して記述されます。
`strawberry_django.fields()`のデフォルトの動作は、与えられた型情報を基にリレーションシップを解決します。

```python
from typing import List

@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color: "Color"


@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: List[Fruit]
```

すべてのリレーションシップは自然に`N+1`問題を引き起こす可能性があります。
これを避けるために、自動的にいくつかの一般的な問題を解決する[最適化エクステンション](https://strawberry.rocks/docs/django/guide/optimizer)、またはより複雑な状況で[データローダー](https://strawberry.rocks/docs/guides/dataloaders)を有効にできます。

## フィールドのカスタマイズ

すべてのDjangoの型は、デフォルトで`strawberry_django.fields()`フィールド型を使用して符号化されます。
フィールドはさまざまな引数でカスタマイズできます。

```python
# types.py
@strawberry_django.type(models.Color)
class Color:
    another_name: auto = strawberry_django.field(field_name="name")
    internal_name: auto = strawberry_django.field(
        name="fruits",
        field_name="fruit_set",
        filters=FruitFilter,
        order=FruitOrder,
        pagination=True,
        description="この色を持つ果物のリスト",
    )
```

## autoフィールドで型を定義する

フィールドの型を解決するために`strawberry.auto`を使用するとき、`strawberry_django`はDjangoフィールドのフィールド型とそれとの適切な方をマッピングする辞書を使用します。

```python
{
    models.CharField: str,
    models.IntegerField: int,
    ...
}
```

もしデフォルトライブラリの一部でない独自なDjangoフィールドを使用している、またはフィールドに異なる型を使用したい場合、マップ内でその値を上書きすることでできます。

```python
from typing import NewType

import strawberry
import strawberry_django
from django.db import models
from strawberry_django.fields.types import field_type_map


Slug = strawberry.scalar(
    NewType("Slug", str),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry_django.type
class MyCustomFileType:
    ...


field_type_map.update({
    models.SlugField: Slug,
    models.FileField: MyCustomFileType,
})
```

## 名前によってDjangoのモデルフィールドを含める／除外する

---

⚠ 警告

これらの新しいキーワードは、うっかり望んでいないデータの露出を招くかもしれないため、注意して使用されるべきです。
特に`fields="__all__"`または`exclude`の使用で、機密なモデルフィールドが含まれ、気づかないうちにスキーマ内に存在するように鳴るかもしれません。

---

`strawberry_django.type`は、Djangoモデルからフィールドを生成することを支援する`fields`と`exclude`の2つのオプションのキーワードフィールドを含みます。

`fields`の妥当な値は次のとおりです。

1. `__all__`は、すべてのモデルフィールドでフィールド型に`strawberry.auto`を割り当てます。
2. `[<List of field names>]`は、反復操作可能なフィールドのフィールド型に`strawberry.auto`を割り当てます。
   これらは必要に応じて手動の型注釈と組み合わされます。

```python
# すべてのフィールド
@strawberry_django.type(models.Fruit, fields="__all__")
class FruitType:
    pass


# 反復可能なフィールド
@strawberry_django.type(models.Fruit, fields=["name", "color"])
class FruitType:
    pass


# 上書きされるフィールド
@strawberry_django.type(models.Fruit, fields=["color"])
class FruitType:
    name: str
```

`exclude`の妥当な値は次のとおりです。

1. `[<List of field names>]`は、フィールドリストから女がいます。
   すべての他のDjangoモデルフィールドは含まれ、フィールド型として`strawberry.auto`を持ちます。
   もしほかのフィールド型が割り当てれている場合、これらは上書きされます。
   空のリストは無視されます。

```python
# 除外されるフィールド
@strawberry_django.type(models.Fruit, exclude=["name"])
class FruitType:
    pass


# 上書きされ、除外されるフィールド
@strawberry_django.type(models.Fruit, exclude=["name"])
class FruitType:
    color: int
```

`fields`は`exclude`よりも優先されるため、両方が提供された場合、`exclude`は無視されることに注意してください。

`inadvertently`:【副詞】不注意に、軽率に、うっかり
`exposure`:【名詞】さらす、受ける、身をさらす、露光、露出、暴露
`sensitive`:【形容詞】敏感な、感覚が鋭い、高感度な、神経質な、繊細な、機密の
`precedence`:【名詞】先行、優先、上位、優位、席次、序列

## フィールドクラスの上書き（応用）

プロジェクトにおいて、もし標準的な`strawberry_django.field()`の動作を変更／追加したい場合、`field_cls`引数で`strawberry_django.type`でデコレートすることで、独自のフィールドクラスを使用できます。

```python
class CustomStrawberryDjangoField(StrawberryDjangoField):
    """独自の動作をここに記述します。"""


@strawberry_django.type(User, field_cls=CustomStrawberryDjangoField)
class UserType:
    # これらフィールドはそれぞれ、`CustomStrawberryDjangoField`のインスタンスです。
    id: int
    name: auto


@strawberry.type
class UserQuery:
    # 素のstrawberry型に独自のフィールドクラスを直接作成できます。
    user: UserType = CustomStrawberryDjangoField()
```

この例において、`UserType`のそれぞれのフィールドは、`CustomStrawberryDjangoField`によって自動的に作成されます。
それは、リレーションシップの独自なページ区切りから、フィールド権限の変更まで、任意のものを実装できます。

`alter`:【動詞】変更する、変貌する

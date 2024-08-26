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

# 型の定義

## 出力型

---

ℹ 注意事項

性能を改善して、いくつかの一般的な落とし穴に落ちないように、[クエリ最適化エクステンション](https://strawberry.rocks/docs/django/guide/optimizer)を有効にすることを強く推奨します。

---

出力型はモデルから生成されます。
`auto`型はフィールド型を自動解決するために使用されます。
リレーションフィールドはDjangoモデルから生成された他の方を参照することによって記述されます。
多対多リレーションは`typing.List`型注釈で記述されます。
`strawberry_django`は、リレーショナルフィールドのリゾルバーを自動的に生成します。
詳細な情報については、[リゾルバー](https://strawberry.rocks/docs/django/guide/resolvers)ページを読んでください。

```python
# types.py
from typing import List

import strawberry_django
from strawberry import auto


@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color "Color"


@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: List[Fruit]
```

## 入力型

入力型は、`strawberry_django.input`デコレーターを使用してDjangoモデルから生成されます。
最初の引数はモデルで、（入力）型はそのモデルを継承しています。

```python
# types.py
@strawberry_django.input(models.Fruit)
class FruitInput:
    id: auto
    name: auto
    color: "ColorInput"


@strawberry_django.input(models.Color)
class ColorInput:
    id: auto
    name: auto
```

すべての`auto`フィールドがオプションである部分的な入力型は、`input`内の`partial`キーワード引数を`True`に設定することで生成されます。
部分的な入力型は、クラス継承を介して既存の入力型から生成されます。

明示的に`Optional[]`でマークされていない限り、非`auto`型の注釈は尊重され、それに従って必須になります。

```python
# types.py
@strawberry_django.input(models.Color, partial=True)
class FruitPartialInput(FruitInput):
    color: List["ColorPartialInput"]


# autoフィールドはオプションです。
@strawberry_django.input(models.Color, partial=True)
class ColorPartialInput:
    id: auto    # オプション
    name: auto  # オプション
    fruits: List[FruitPartialInput] # 必須


# 代わりの入力型で、nameフィールドは必須です。
@strawberry_django.input(models.Color, partial=True)
class ColorNameRequiredPartialInput:
    id: auto    # オプション
    name: str   # 必須
    fruits: List[FruitPartialInput] # 必須
```

`partial`:【形容詞】一部の、部分的な、不完全な、中途半端な、不公平な

## Djangoモデルからの型（の生成）

Djangoモデルは`strawberry_django.type`デコレーターで`strawberry`の型に変換できます。
独自の説明は、`description`キーワード引数を使用して追加できます。
詳細は、[`strawberry.type`デコレーターAPI](https://strawberry.rocks/docs/types/object-types#api)を参照してください。

```python
# types.py
import strawberry_django


@strawberry_django.type(models.Fruit, description="美味しいおやつ")
class Fruit:
    ...
```

## 型にフィールドを追加する

デフォルトで、新しい型にフィールドは実装されません。
そのため、ドキュメントの[フィールドを定義する方法](https://strawberry.rocks/docs/django/guide/fields)を確認してください。

## 返される`QuerySet`をカスタマイズする

---

⚠ 警告

これをすることによって、この型が返す任意のフィールドのすべての自動的な`QuerySet`の生成が変更されます。
理想的には、代わりに独自のリゾルバーを定義して、より細かく制御できるようにします。

---

デフォルトで、`strawberry_django`型はDjangoモデルのデフォルトマネージャーからデータを取得します。
クエリセットをさらにフィルタリングするような、デフォルトのクエリセットに何らかの追加処理をするために、型に独自の`get_queryset`クラスメソッドを実装できます。

```python
# types.py
@strawberry_django.type(models.Fruit)
class Berry:
    @classmethod
    def get_queryset(cls, queryset, info, **kwarg):
        return queryset.filter(name__contains="berry")
```

`get_queryset`クラスメソッドは、フィルターするために`QuerySet`を与えられ、`strawberry.Info`オブジェクトは結果についての詳細を含んでいます。

例えば、リクエストした現在のユーザーに基づいて、結果へのアクセスを制限するために、`info`引数を使用できます。

```python
# types.py
from strawberry_django.auth.utils import get_current_user


@strawberry_django.type(models.Fruit)
class Berry:
    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        user = get_current_user(info)
        if not user.is_staff:
            # もし、ユーザーがスタッフ・メンバー出ない場合、最も秘密なベリーへのアクセスを制限します。
            queryset = queryset.filter(is_top_secret=False)
        return queryset.filter(name__contains="berry")
```

---

ℹ ノート

[PermissionExtension](https://strawberry.rocks/docs/django/guide/permissions)を使用してこれを制限するほかの方法は、このライブラリによって提供されています。

---

`kwargs`辞書は、[フィルター](https://strawberry.rocks/docs/django/guide/filters)または[ページ区切り](https://strawberry.rocks/docs/django/guide/pagination)のような`@strawberry.django.type`定義内に追加された他の引数を含んでいます。

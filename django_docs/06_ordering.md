# 順序付け

```python
@strawberry_django.order(models.Color)
class ColorOrder:
    name: auto


@strawberry_django.order(models.Fruit)
class FruitOrder:
    name: auto
    color: ColorOrder | None
```

---

💡 Tip

ほとんどの場合、フィールドは`Optional`注釈とデフォルト値`strawberry.UNSET`を持つべきです。
上記`auto`注釈は自動的に`Optional`内にラップされます。
`UNSET`は自動的に、`field`のない、または`strawberry_django.order_field`を付けられたフィールド用に自動的に使用されます。

---

上記コードは、次のスキーマを生成します。

```graphql
enum Ordering {
  ASC
  ASC_NULLS_FIRST
  ASC_NULLS_LAST
  DESC
  DESC_NULLS_FIRST
  DESC_NULLS_LAST
}

input ColorOrder {
  name: Ordering
}

input FruitOrder {
  name: Ordering
  color: ColorOrder
}
```

## カスタム順序付けメソッド

リゾルバーに定義することで、カスタム順序付けメソッドを定義できます。

```python
@strawberry_django.order(models.Fruit)
class FruitOrder:
    name: auto

    @strawberry_django.order_field
    def discovered_by(self, value: bool, prefix: str) -> list[str]:
        if not value:
            return []
        return [f"{prefix}discover_by__name", f"{prefix}name"]

    @strawberry_django.order_field
    def order_number(
        self,
        info: Info,
        queryset: QuerySet,
        value: strawberry_django.Ordering,   # 代わりに`auto`を使用できます。
        prefix: str,
        sequence: dict[str, strawberry_django.Ordering] | None
    ) -> tuple[QuerySet, list[str]] | list[str]:
        queryset = queryset.alias(
            _ordered_num=Count(f"{prefix}orders__id")
        )
        ordering = value.resolve(f"{prefix}_ordered_num")
        return queryset, [ordering]
```

---

⚠ 警告

直接`queryset.order_by()`を使用しないでください。
`order_by`はチェーン可能な操作ではないため、この方法で適用された変更は後で上書きされます。

---

---

💡 Tip

`strawberry_django.Ordering`型は、フィールドの名前を`nulls_first`と`nulls_last`引数を持った`asc()`、`desc()`メソッドが正しく適用された適切な`F`オブジェクトに変更するために使用できる、便利な`resolve`メソッドを持っています。

---

上記コードは次のスキーマを生成します。

```graphql
enum Ordering {
  ASC
  ASC_NULLS_FIRST
  ASC_NULLS_LAST
  DESC
  DESC_NULLS_FIRST
  DESC_NULLS_LAST
}

input FruitOrder {
  name: Ordering
  discoveredBy: Boolean
  orderNumber: Ordering
}
```

## リゾルバーの引数

1. `prefix` - 現在のパスまたは位置を表現します。
    1. 必須です。
    2. ネストされた順序付けで重要です。
    3. 下のコードに置いて、カスタムな順序付けである`name`は、`prefix`を適用しないで`Color`の代わりに`Fruit`で順序付けする結果になります。
2. `value` - GraphQLフィールドの値を表現します。
    1. 必須ですが、デフォルトの`order`メソッド用に禁止されています。
    2. 注釈されなkレバなりません。
    3. フィールドの戻り値の型の代わりに使用されます。
    4. `auto`の仕様は`strawberry_django.Ordering`と同じです。
3. `queryset` - より複雑な順序付けのために使用されます。
    1. オプションですが、デフォルトの`order`メソッドのために必須です。
    2. 通常、`QuerySet`を注釈するために使用されます。
4. `sequence` - 同じレベルの値を順序付けするために使用されます。
    1. GraphQLオブジェクト内の要素は、ユーザーによって定義された順番を維持することを保証されていません。
 　　  その場合はこの引数を使用しなければなりません。
    2. 通常、カスタム順序付けフィールドメソッドのために使用されません。
    3. 高度な利用のために、`strawberry_django.process_order`を参照してください。

```python
@strawberry_django.order(models.Fruit)
class FruitOrder:
    name: auto
    color: ColorOrder | None


@strawberry_django.order(models.Color)
class ColorOrder:
    @strawberry_django.order_field
    def name(self, value: bool, prefix: str):
        # 未使用のルートオブジェクトが代わりに順序付けされている場合、接頭語は"fruit_set__"になります。
        if value:
            return ["name"]
        return []
```

```graphql
{
  fruits(
    order: {
      color: {
        name: ASC
      }
    }
  ){
    ...
  }
}
```

## リゾルバーの戻り値

カスタムフィールドメソッドのために、2つの戻り値がサポートされています。

1. `QuerySet.order_by -> Collection[F | str]`によって受け入れられる値のイテラブル
2. `QuerySet`と`QuerySet.order_by -> tuple[QuerySet, Collection[F | str]]`によって受け入れられる値のイテラブルのタプル

デフォルトの`order`メソッドは、2番目のバリアントのみがサポートされています。

## nullについてはどうか？

デフォルトで、`null`値は無視されます。
これは、`@strawberry_django.order_field(order_none=True)`のようにトグルされます。

## デフォルトのorderメソッドの上書き

フィールド順序付けメソッドと同様に機能しますが、次の点が異なります。

1. オブジェクト全体で順序付けの解決をする責任があります。
2. `order`と名付けなくてはなりません。
3. `queryset`引数は必須です。
4. `value`引数は禁止されています。
5. おそらく`sequence`を使用するはずです。

```python
@strawberry_django.order(models.Fruit)
class FruitOrder:
    name: auto

    @strawberry_django.order_field
    def ordered(
        self,
        info: Info,
        queryset: QuerySet,
        value: strawberry_django.Ordering,
        prefix: str
    ) -> tuple[QuerySet, list[str]] | list[str]:
        queryset = queryset.alias(
          _ordered_num=Count(f"{prefix}orders__id")
        )
        return queryset, [value.resolve(f"{prefix}_ordered_num") ]

    @strawberry_django.order_field
    def order(
        self,
        info: Info,
        queryset: QuerySet,
        prefix: str,
        sequence: dict[str, strawberry_django.Ordering] | None
    ) -> tuple[QuerySet, list[str]]:
        queryset = queryset.filter(
            ... # Do some query modification
        )

        return strawberry_django.process_order(
            self,
            info=info,
            queryset=queryset,
            sequence=sequence,
            prefix=prefix,
            skip_object_order_method=True
        )
```

---

💡 Tip

上記で見た通り、`strawberry_django.process_order`関数は公開され、カスタムメソッド内で再利用されます。
`order`メソッドの`skip_Object_order_method`は終わりのない再帰を避けるために使用されます。

---

## 型に順序付けを追加する

すべてのフィールドとミューテーションは、デフォルトで基づいた型から順序付けを継承します。
よって、次のようなフィールドがある場合・・・

```python
@strawberry_django.type(models.Fruit, order=FruitOrder)
class Fruit:
    ...
```

`fruits`フィールドは、それがフィールドに渡される同じ方法で型の`order`を継承します。

## フィールドに順序付けを直接追加する

フィールドに追加された順序付けは、デフォルトの順序付けを上書きします。

```python
@strawberry.type
class Query:
    fruits: Fruit = strawberry_django.field(order=FruitOrder)
```

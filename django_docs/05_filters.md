# フィルタリング

Django型にフィルターを定義することができ、それはORMで`.filter(...)`クエリに変換されます。

```python
import strawberry_django
from strawberry import auto


@strawberry_django.filter(models.Fruit)
class FruitFilter:
    id: auto
    name: auto


@strawberry_django.type(models.Fruit, filters=FruitFilter)
class Fruit:
    ...
```

---

💡 Tip

ほとんどの場合、フィルターフィールドは、`foo: Optional[SomeType] = strawberry.UNSET`のように`Optional註釈と`デフォルト値`strawberry.UNSET`であるべきです。
上記`auto`註釈は自動的に`Optional`でラップされます。
`UNSET`は、`field`のないフィールド、または`strawberry_django.filter_field`を含むフィールドで自動的に使用されます。

---

上記コードは、次のスキーマを生成します。

```graphql
input FruitFilter {
  id: ID
  name: String
  AND: FruitFilter
  OR: FruitFilter
  NOT: FruitFilter
  DISTINCT: Boolean
}
```

---

💡 Tip

もし[relay統合](https://strawberry.rocks/docs/django/guide/relay)を利用して、オブジェクトを識別するために`relay.Node`と`GlobalID`から継承した型と作業する場合、`auto`フィールドが型とフィルターの`GlobalID`とマッピングされることを確実にするために、[strawberry_django.settings](https://strawberry.rocks/docs/django/guide/settings)内の`MAP_AUTO_ID_AS_GLOBAL_ID = True`を設定することを勧めます。

---

## AND、OR、NOT、DISTINCT・・・

すべてのフィルターに`AND`、`OR`、`NOT`、`DISTINCT`フィールドが追加され、より複雑なフィルタリングを可能にします。

```graphql
{
  fruit (
    filters: {
      name: "kebab"
      OR: {
        name: "raspberry"
      }
    }
  ) {
    ...
  }
}
```

## ルックアップ

ルックアップは、`lookup=True`ですべてのフィールドに追加され、それはそれぞれの方を解決するために多くの選択肢を追加します。

```python
@strawberry_django.filter(models.Fruit, lookups=True)
class FruitFilter:
    id: auto
    name: auto
```

上記コードは、次のスキーマを生成します。

```graphql
input IDBaseFilterLookup {
  exact: ID
  isNull: Boolean
  inList: [String!]
}

input StrFilterLookup {
  exact: ID
  isNull: Boolean
  inList: [String!]
  iExact: String
  contains: String
  iContains: String
  startsWith: String
  iStartsWith: String
  endsWith: String
  iEndsWith: String
  regex: String
  iRegex: String
}

input FruitFilter {
  id: IDBaseFilterLookup
  name: StrFilterLookup
  AND: FruitFilter
  OR: FruitFilter
  NOT: FruitFilter
  DISTINCT: FruitFilter
}
```

単独のフィールドルックアップは、`FilterLookup`ジェネリック型で注釈されます。

```python
from strawberry_django import FilterLookup


@strawberry_django.filter(models.Fruit)
class FruitFilter:
    name: FilterLookup[str]
```

## リレーションシップを介してフィルタリングする

```python
# types.py
@strawberry_django.filter(models.Color)
class ColorFilter:
    id: auto
    name: auto


@strawberry_django.filter(models.Fruit)
class FruitFilter:
    id: auto
    name: auto
    color: ColorFilter | None
```

上記コードは、次のスキーマを生成します。

```graphql
input ColorFilter {
  id: ID
  name: String
  AND: ColorFilter
  OR: ColorFilter
  NOT: ColorFilter
}

input FruitFilter {
  id: ID
  name: String
  color: ColorFilter
  AND: ColorFilter
  OR: ColorFilter
  NOT: ColorFilter
}
```

## カスタムフィルターメソッド

リゾルバーに定義することで、カスタムフィルターのメソッドを定義できます。

```python
@strawberry_django.filter(models.Fruit)
class FruitFilter:
    name: auto
    last_name: auto

    @strawberry_django.filter_field
    def simple(self, value: str, prefix) -> Q:
        return Q(**{f"{prefix}name": value})

    @strawberry_django.filter_field
    def full_name(self, queryset: QuerySet, value: str, prefix: str) -> tuple[QuerySet, Q]:
        queryset = queryset.alias(
            _fullname=Concat(
                f"{prefix}name", Value(" "), f"{prefix}last_name"
            )
        )
        return queryset, Q(**{"_fullname": value})

    @strawberry_django.filter_field
    def full_name_lookups(
        self,
        info: Info,
        queryset: QuerySet,
        value: strawberry_django.FilterLookup[str],
        prefix: str
    ) -> tuple[QuerySet, Q]:
        queryset = queryset.alias(
            _fullname=Concat(
                f"{prefix}name", Value(" "), f"{prefix}last_name"
            )
        )
        return strawberry_django.process_filters(
            filters=value,
            queryset=queryset,
            info=info,
            prefix=f"{prefix}_fullname"
        )
```

---

⚠ 警告

直接、`queryset.filter()`を使用することは勧められません。
もし、`NOT`、`OR`そして`AND`を使用したより複雑なフィルタリングを使用するとき、望んでいない動作を導くかもしれません。

---

## process_filters

上記でみた`strawberry_django.process_filters`関数は公開され、カスタムメソッド内で使用されます。
上記のそれは、フィールドルックアップを解決するために使用されます。

## null値

デフォルトで`null`値はすべてのフィルターとルックアップで無視されます。
これは、カスタムフィルターメソッドも同様に適用されます。
これらは呼び出されることさえありません（`None`をチェックする必要はありません）。
これは、`strawberry_django.filter_field(filter_none=True)`を使用することで修正できます。
また、これは、組み込みの`exact`と`iExact`ルックアップは、`None`をフィルターするために使用できず、`isNull`を明示的に使用する必要があることを意味します。

## 値の解決

1. `relay.GlobalID`型の`value`引数は、その`node_id`属性に解決されます。
2. `Enum`型の`value`引数は、その値にに解決されます。
3. 上記型は`lists`に変換されます。

`strawberry_django.filter_field(resolve_value=...)`を介して解決が修正されます。

1. True - 常に解決されます。
2. False - 解決されません。
3. UNSET（デフォルト） - カスタムメソッドのみなしで、フィルターを解決します。

上記コードは、次のスキーマを生成します。

```graphql
input FruitFilter {
  name: String
  lastName: String
  simple: str
  fullName: str
  fullNameLookups: StrFilterLookup
}
```

## リゾルバーの引数

1. `prefix` - 現在のパスまたは位置を表現します。
   1. 必須です。
   2. ネストされたフィルターで重要です。
   3. 次のコードにおいて、`name`カスタムフィルターは、`prefix`を適用しないで`Color`の代わりに`Fruit`をフィルタリングする結果になります。

```python
@strawberry_django.filter(models.Fruit)
class FruitFilter:
    name: auto
    color: ColorFilter | None


@strawberry_django.filter(models.Color)
class ColorFilter:
    @strawberry_django.filter_field
    def name(self, value: str, prefix: str):
        # 未使用のルートオブジェクトがフィルタリングされる場合、接頭語は"fruit_set__"になります。
        if value:
            return Q(name=value)
        return Q()
```

```graphql
{
  fruits(
    filters: {
      color: {
        name: "blue"
      }
    }
  ) { ... }
}
```

1. `value` - GraphQLフィールド型を表現します。
   1. 必須ですが、デフォルト`filter`メソッドは禁止されています。
   2. 注釈されなくてはなりません。
   3. フィールドの戻り値の方の代わりに使用されます。
2. `queryset` - より複雑なフィルタリングで使用されます。
   1. オプションですが、デフォルトフィルターメソッドのために要求されます。
   2. 普通、`QuerySet`を註釈するために使用されます。

## リゾルバーの戻り値

カスタムメソッド用に、2つの戻り値がサポートされています。

1. Djangoの`Q`オブジェクト
2. `QuerySet`と`Q`オブジェクトのタプルである`tuple[QuerySet, Q]`

デフォルトフィルターメソッドように、2つのバリアントのみサポートされています。

## nullについてはどうか？

デフォルトで`null`値は無視されます。
これは、`@strawberry_django.filter_field(filter_none=True)`のようにトグルされます。

## デフォルトフィルターメソッドの上書き

機能はフィールドフィルターメソッドと似ていますが・・・

1. オブジェクト全体のフィルタリングを解決する責任があります。
2. `filter`と名付けなくてはなりません。
3. `queryset`引数は必須です。
4. `value`引数は禁止されています。

```python
@strawberry_django.filter(models.Fruit)
class FruitFilter:
    def ordered(
        self,
        value: int,
        prefix: str,
        queryset: QuerySet,
    ):
        queryset = queryset.alias(
          _ordered_num=Count(f"{prefix}orders__id")
        )
        return queryset, Q(**{f"{prefix}_ordered_num": value})

    @strawberry_django.order_field
    def filter(
        self,
        info: Info,
        queryset: QuerySet,
        prefix: str,
    ) -> tuple[QuerySet, list[Q]]:
        queryset = queryset.filter(
            ... # Do some query modification
        )

        return strawberry_django.process_filters(
            self,
            info=info,
            queryset=queryset,
            prefix=prefix,
            skip_object_order_method=True
        )
```

---

💡 Tip

上記で見た通り、`strawberry_django.process_filters`関数は、公開され、カスタムメソッド内で再利用されます。
フィルターメソッド用に、`skip_object_over_method`は終わりのない再起を避けるために使用されます。

---

## 型にフィルターを追加する

すべてのフィールドとCUDミューテーションは、デフォルトで基になる型からフィルターを継承します。
よって、次のようなフィールドがある場合・・・

```python
@strawberry_django.type(models.Fruit, filters=FruitFilter)
class Fruit:
    ...


@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field()
```

`fruits`フィールドは、フィルターがフィールドに渡される同じ方法で、型の`filters`を継承します。

## フィールドに直接フィルターを追加する

フィルターは型のデフォルトフィルターを上書きすることで、フィールドに追加されます。

```python
@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field(filters=FruitFilter)
```

## ジェネリックなルックアップのリファレンス

`strawberry_django`からインポート可能な、7つのジェネリックなルックアップである`strawberry.input`クラスをすでに定義されています。

### BaseFilterLookup

1. `exact`、`isNull`そして`inList`を含みます。
2. `ID`と`bool`フィールドで使用されます。

### RangeLookup

1. `range`または`BETWEEN`フィルタリングで使用されます。

### ComparisonFilterLookup

1. `BaseFilterLookup`を継承します。
2. 追加して`gt`、`gte`、`lt`、`lte`そして`range`を含みます。
3. 数値フィールドで使用されます。

### FilterLookup

1. `BaseFilterLookup`を継承します。
2. 追加して`iExact`、`contains`、`iContains`、`startsWith`、`iStartsWith`、`endsWith`、`iEndsWith`、`regex`そして`iRegex`を含みます。
3. デフォルトで文字列に基づいたフィールで使用されます。

### DateFilterLookup

1. `ComparisonFilterLookup`を継承します。
2. 追加して`year`、`month`、`day`、`weekDay`、`isoWeekDay`、`week`、`isoYear`そして`quarter`を含みます。
3. 日付に基づいたフィールドで使用されます。

### TimeFilterLookup

1. `ComparisonFilterLookup`を継承します。
2. 追加して`hour`、`minute`、`second`、`date`そして`time`を含みます。
3. 時間に基づいたフィールドで使用されます。

### DateTimeFilterLookup

1. `DataFilterLookup`と`TimeFilterLookup`を継承します。
2. 日時に基づいたフィールドで使用されます。

### 従来からのフィルタリング

[USE_DEPRECATED_FILTERS](https://strawberry.rocks/docs/django/guide/settings#strawberry_django)を介して、前のバージョンのフィルターは有効になります。

---

⚠ 警告

`USE_DEPRECATED_FILTERS`を`True`に設定しなかった場合、従来のカスタムフィルタリングメソッドは呼び出されません。

---

従来からのフィルターを使用する時は、従来の`strawberry_django.filters.FilterLookup`ルックアップも同様に使用することが重要です。
正しいバージョンは、`auto`で注釈されたフィルターフィールドに適用されます（`lookups=True`が設定されることで）。
新旧のルックアップの組み合わせは、`DuplicatedTypeName: Type StrFilterLookup is defined multiple times in the schema`エラーを引き起こすかもしれません。

従来のフィルタリングを有効な間、新しいフィルタリングのカスタムメソッドは、デフォルト`filter`メソッドを含み完全にに機能します。

移行プロセスは、これらのステップで構成されます。

1. `USE_DEPRECATED_FILTERS`を有効にします。
2. 徐々にカスタムフィルターフィールドメソッドを新しいバージョンに変換します（もし該当する場合、古い`FilterLookup`を使用することを忘れないでください）。
3. 徐々にデフォルトの`filter`メソッドを変換します。
4. `USE_DEPRECATED_FILTERS`を無効にして、これは破壊的な変更です。

`gradually`:【副詞】次第に、徐々に、だんだんと
`applicable`:【形容詞】〜に適用できる、適切な、該当する

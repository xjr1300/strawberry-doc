# 操作ディレクティブ

GraphQLはスキーマまたは操作内のアイテムの評価を修正するためにディレクティブを使用します。
操作ディレクティブは任意の操作（クエリ、サブスクリプション、ミューテーション）の内部に含まれ、操作の実行または操作によって返される値を修正するために使用されます。

ディレクティブは、追加フィールドの値を介して計算される値のリゾルバーを作成する手間を省きます。

すべてのディレクティブは`@`シンボルで始まります。

`directive`:【形容詞】指導（管理）的な、指示（命令）的な、指向性の【名詞】指示、命令

## デフォルトの操作ディレクティブ

`Strawberry`は2つのデフォルトの操作ディレクティブを提供しています。

1. `@skip(if: Boolean!)` - Booleanがtrueの場合、与えられたアイテムはGraphQLサーバーから解決されません。
2. `@include(if: Boolean!)` - Booleanがfalseの場合、与えられたアイテムはGraphQLサーバーから解決されません。

---

注意事項

`deprecated(reason: String)`は操作ディレクティブと互換性はありません。
`@deprecated`は[スキーマディレティブ](https://strawberry.rocks/docs/types/schema-directives)専用です。

---

デフォルトの操作ディレティブの例を次に示します。

```graphql
# @include
query getPerson($includePoints: Boolean!) {
  person {
    name
    points @include(if: $includePoints)
  }
}

# @skip
query getPerson($hideName: Boolean!) {
  person {
    name @skip(if: $hideName)
    points
  }
}
```

## 独自の操作ディレクティブ

独自のディレクティブは、クエリ内で使用するためにスキーマ内で定義される必要があり、スキーマの他の部分を装飾するために使用できます。

```python
# 定義
@strawberry.directive(
    locations=[DirectiveLocation.FIELD], description="Make string uppercase"
)
def turn_uppercase(value: str) -> str
    return value.upper()


@strawberry.directive(locations=[DirectiveLocation.FIELD])
def replace(value: str, old: str, new: str) -> str:
    return value.replace(old, new)
```

```python
# 使用
query People($identified: Boolean!) {
  person {
    name @turnUppercase
  }
  jess: person {
    name @replace(old: "Jess", new: "Jessica")
  }
  johnDoe: person {
    name @replace(old: "Jess", new: "John") @include(if: $identified)
  }
}
```

`exclusive`:【形容詞】排他的な、限定された、唯一の、独占的な

## 操作ディレクティブの場所

ディレクティブはクエリ内の特定な場所内にのみ現れます。
これらの場所はディレクティブの定義内に含まれる必要があります。
`Strawberry`において、その場所はディレクティブの関数の`locations`引数内で定義されます。

```python
@strawberry.directive(locations=[DirectiveLocation.FIELD])
```

### 操作ディレクティブの可能箇所

操作ディレクティブは操作の多くの異なる場所で適用されます。
次に許可された場所をリストします。

1. `QUERY`
2. `MUTATION`
3. `SUBSCRIPTION`
4. `FIELD`
5. `FRAGMENT_DEFINITION`
6. `FRAGMENT_SPREAD`
7. `INLINE_FRAGMENT`

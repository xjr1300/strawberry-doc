# ページ区切り

## デフォルトのページ区切り

限界／オフセットページ区切りのインターフェイスは、基本的なページ区切りに求められる機能を使用できます。

```python
@strawberry_django.type(models.Fruit, pagination=True)
class Fruit:
    name: auto
```

```graphql
query {
  fruits(pagination: {offset: 0, limit: 2}) {
    name
    color
  }
}
```

デフォルトの限界はありません。
もしページ区切りの限界が定義されていない場合、すべての要素が返されます。

## Relayのページ区切り

より複雑なシナリオにおいて、カーソルページ区切りの方が良いですよう。
このために、それらを定義するために[relay統合](https://strawberry.rocks/docs/django/guide/relay)を使用します。

# Relayサポート

次のようにDjango型に直接[公式のstrawberryのrelay統合](https://strawberry.rocks/docs/guides/relay)を使用できます。

```python
import strawberry
import strawberry_django
from strawberry_django.relay import ListConnectionWithTotalCount


class Fruit(models.Model):
    ...


@strawberry_django.type(Fruit)
class FruitType(relay.Node):
    ...


@strawberry.type
class Query:
    # オプション1: totalCountのないデフォルトのrelay
    # これはデフォルトのstrawberry relayの振る舞いです。
    # 注意事項: デフォルトのstrawberry.relay.connection()でゃなく、strawberry_django.connection()を使用する必要があります。
    fruits: strawberry.relay.ListConnection[FruitType] = strawberry_django.connection()

    # オプション2: strawberry_djangoはListConnectionWithTotalCountを付属しています。
    # これはクエリで合計数を取得できるようにします。
    fruits_with_total_count: ListConnectionWithTotalCount[
        FruitType
    ] = strawberry_django.connection()

    # オプション3: 手動のメソッドにより手動でリゾルバーを作成できまs樹。
    @strawberry_django.connection(ListConnectionWithTotalCount[FruitType])
    def fruits_with_custom_resolver(self) -> list[Fruit]:
        return Fruit.objects.all()
```

背後で、このエクステンションは次をしています。

1. [モデルの主キー](https://docs.djangoproject.com/en/4.2/ref/models/fields/#django.db.models.Field.primary_key)を使用して、自動的に`relay.NodeID`フィールドを解決します。
2. 定義されていないコネクションのリゾルバーを自動的に生成します。
   例えば、`some_model_conn`と`some_model_conn_with_total_count`は、`SomeModel.objects.all()`を返すカスタムリゾルバーを定義します。
3. コネクションの解決をこのライブラリで利用可能な他のすべての機能と統合します。
   例えば、[フィルター](https://strawberry.rocks/docs/django/guide/filters)、[順序付け](https://strawberry.rocks/docs/django/guide/ordering)そして[権限](https://strawberry.rocks/docs/django/guide/permissions)は、`strawberry_django`によって定義されたコネクションと一緒に使用されます。

`some_model_conn_with_resolver`がする同じ方法で、独自の`relay.NodeID`フィールドとリゾルバーを定義できます。
この場合、それらは上書きされません。

---

💡 Tip

`relay.Node`とオブジェクトを識別する`GlobalID`から継承した方のみを使用している場合、`auto`フィールドを型とフィルターの`GlobalID`にマッピングを得ることを保証するために、[strawberry_django設定](https://strawberry.rocks/docs/django/guide/settings)内で`MAP_AUTO_ID_AS_GLOBAL_ID=True`を設定できます。

---

また、このライブラリは、`strawberry.relay.ListConnection`がする同じ方法で機能しますが、`totalCount`属性を公開する`strawberry_django.relay.ListConnectionWithTotalCount`を公開します。

ページ区切りのアルゴリズムを変更する、`Connection`/`Edge`型にフィールドを追加するような、詳細なカスタマイズオプションは、適切に説明されている[公式のstrawberry relay統合]を確認してください。

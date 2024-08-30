# ミューテーション

## 始める

ミューテーションは、[strawberryのミューテーション](https://strawberry.rocks/docs/general/mutations)と同じ方法で定義できますが、`@strawberry.mutation`を使用する代わりに、`@strawberry_django.mutation`を使用します。

ここで、それらの間の違いを示します。

1. `strawberry`のDjangoのミューテーションは、ミューテーションが非同期で安全な環境で確実に実行されるようにします。
   それはASGIを実行して、`sync`なリゾルバーを定義した場合、それが自動的に`sync_to_async`呼び出しでラップされることを意味します。
2. [権限統合](https://strawberry.rocks/docs/django/guide/permissions)と適切に統合しています。
3. 一般的なDjangoエラーを自動処理して、標準化された方法でそれらを返す選択肢があります（詳細は次）。

## Djangoのエラー処理

ミューテーションを定義したとき、`ValidationError`、`PermissionDenied`そして`ObjectDoesNotExist`などの一般的なDjangoのエラーを処理するために、`handle_django_errors=True`を渡せます。

```python
@strawberry.type
class Mutation:
    @strawberry_django.mutation(handle_django_errors=True)
    def create_fruit(self, name: str, color:str) -> Fruit:
        if not is_valid_color(color):
            raise ValidationError("The color is not valid")

        # もし、例えば`name`が許可された`max_length`よりも長い場合、
        # 作成もValidationErrorを引き起こす可能性もあります。
        fruit = models.Fruit.objects.create(name=name)
        return cast(Fruit, fruit)
```

上記コードは、次のスキーマを生成します。

```graphql
enum OperationMessageKind {
  INFO
  WARNING
  ERROR
  PERMISSION
  VALIDATION
}

type OperationInfo {
  # 操作によって返されたメッセージのリスト
  messages: [OperationMessage!]!
}

type OperationMessage {
  # このメッセージの種類
  kind: OperationMessageKind!
  # エラーメッセージ
  message: String!
  # エラーを引き起こしたフィールド、または特定のフィールドに関連していない場合は`null`
  field: String
  # エラーコード、またはエラーコードが設定されていない場合は`null`
  code: String
}

type Fruit {
  name: String!
  color: String!
}

union CreateFruitPayload = Fruit | OperationInfo

mutation {
  createFruit(
    name: String!
    color: String!
  ): CreateFruitPayload!
}
```

---

💡 Tip

すべて、またはほとんどのミューテーションがこの振る舞いをする場合、[strawberry django設定](https://strawberry.rocks/docs/django/guide/settings)内で`MUTATIONS_DEFAULT_HANDLE_ERRORS=True`を設定することで、`handle_django_errors`のデフォルトの振る舞いを変更できます。

---

## 入力ミューテーション

これらは`@strawberry_django.input_mutation`を使用して定義され、`@strawberry_django.mutation`と同じ方法で動作します。
唯一の違いは、フィールドに[InputMutationExtension](https://strawberry.rocks/docs/general/mutations#the-input-mutation-extension)を注入することで、それはその引数を新しい型に変換します（詳細はそのエクステンションのドキュメントを確認してください）。

## CUDミューテーション

次のCUDミューテーションは、次のライブラリによって提供されます。

1. `strawberry_django.mutations.create`: 与えられた入力のデータを使用してモデルを作成します。
2. `strawberry_django.mutations.update`: 与えられた入力のデータを使用してモデルを更新します。
3. `strawberry_django.mutations.delete`: 与えられた入力のIDを使用してモデルを削除します。

基本的な例は次のとおりです。

```python
from strawberry import auto
from strawberry_django import mutations, NodeInput
from strawberry.relay import Node


@strawberry_django.type(SomeModel)
class SomeModelType(Node):
    name: auto


@strawberry_django.input(SomeModel)
class SomeModelInput:
    name: auto


@strawberry_django.partial(SomeModel)
class SomeModelInputPartial(NodeInput):
    name: auto


@strawberry.type
class Mutation:
    create_model: SomeModelType = mutations.create(SomeModelInput)
    update_model: SomeModelType = mutations.update(SomeModelInputPartial)
    delete_model: SomeModelType = mutations.delete(NodeInput)
```

ここで、注意すべき点がいくつかあります。

1. これらのCUDミューテーションは、`@strawberry_django.mutation`が受け付ける同じ引数を受け付けます。
   これは、例えばミューテーションに`handle_django_errors=True`を渡せるようにします。
2. ミューテーションは、デフォルトで`"data"`と名付けられた引数で型を受け取ります。
   例えばそれを`"info"`に変更するために、ミューテーションに`argument_name="info"`を渡すか、[strawberry django設定](https://strawberry.rocks/docs/django/guide/settings)で`MUTATION_DEFAULT_ARGUMENT_NAME="info"`を設定することで、指定されていない場合にこれをデフォルトにできます。
3. `partial`を使用した入力は、自動的に非`auto`フィールドをオプションにしないで、代わりに明示的な型註釈を尊重することに注意してください。
   例は[partial入力型](https://strawberry.rocks/docs/django/guide/types#input-types)を参照してください。
4. また、`key_attr`属性を提供することで、ID以外の唯一の識別子を使用してモデルを更新または削除できます。

```python
@strawberry_django.partial(SomeModel)
class SomeModelInputPartial:
    unique_field: strawberry.auto


@strawberry.type
class Mutation:
    update_model: SomeModelType = mutations.update(
        SomeModelInputPartial,
        key_attr="unique_field",
    )
    delete_model: SomeModelType = mutations.delete(
        SomeModelInputPartial,
        key_attr="unique_field",
    )
```

## フィルタリング

---

❗ 注意

これは、フィルターに問題があると、モデルコレクション全体が変更される可能性があるため、あまり勧められません。

---

フィルターは、更新と削除ミューテーションに追加でいます。
詳細な情報は[フィルタリング](https://strawberry.rocks/docs/django/guide/filters)を参照してください。

```python
import strawberry
from strawberry_django import mutations


@strawberry.type
class Mutation:
    updateFruits: List[Fruit] = mutations.update(FruitPartialInput, filters=FruitFilter)
    deleteFruits: List[Fruit] = mutations.delete(filters=FruitFilter)


schema = strawberry.Schema(mutation=Mutation)
```

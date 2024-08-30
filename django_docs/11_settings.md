# Django設定

このライブラリの特定の機能は、カスタム[Django設定](https://docs.djangoproject.com/en/4.2/topics/settings/)を使用して設定できます。

## STRAWBERRY_DJANGO

辞書は次のオプションのキーがあります。

これらの機能は、`settings.py`ファイルにこのコードを追加することで有効にできます。

```python
# <project>/settings.py
STRAWBERRY_DJANGO = {
    "FIELD_DESCRIPTION_FROM_HELP_TEXT": True,
    "TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING": True,
    "MUTATIONS_DEFAULT_ARGUMENT_NAME": "input",
    "MUTATIONS_DEFAULT_HANDLE_ERRORS": True,
    "GENERATE_ENUMS_FROM_CHOICES": False,
    "MAP_AUTO_ID_AS_GLOBAL_ID": True,
    "DEFAULT_PK_FIELD_NAME": "id",
}
```

### `FIELD_DESCRIPTION_FROM_HELP_TEXT`（デフォルトは`False`）

Trueの場合、[GraphQLのフィールドの説明](https://spec.graphql.org/draft/#sec-Descriptions)は、対応するDjangoのモデルフィールドの[`help_text`属性](https://docs.djangoproject.com/en/4.1/ref/models/fields/#help-text)から取得されます。
もし、説明が[fieldのカスタマイズ](fields.md#field-customization)を使用して提供されている場合、その説明が変わりに使用されます。

### `TYPE_DESCRIPTION_FROM_MODEL_DOCSTRING`（デフォルトは`False`）

Trueの場合、[GraphQLの型の説明](https://spec.graphql.org/draft/#sec-Descriptions)は、対応するモデルの[docstring](https://docs.python.org/3/glossary.html#term-docstring)から取得されます。
もし、説明が[`strawberry_django.type`デコレーター](types.md#types-from-django-models)を使用して提供されている場合、その説明が変わりに使用されます。

### `MUTATIONS_DEFAULT_ARGUMENT_NAME`（デフォルトは`"data"`）

オプションが渡されていない場合（例えば`"input"`）、[CUDミューテーション](mutations.md#cud-mutations)のデフォルおtの引数名を変更します。

### `MUTATIONS_DEFAULT_HANDLE_ERRORS`（デフォルトは`False`）

オプションが渡されていないとき、[Djangoのエラーハンドリング](mutations.md#django-errors-handling)のデフォルトの振る舞いを設定します。

### `GENERATE_ENUMS_FROM_CHOICES`（デフォルトは`False`）

Trueの場合、`choices`を持つフィールドは、`String`として公開される代わりに、選択肢をもつ列挙型を自動的に生成します。
[django-choices-field](../integrations/choices-field.md)統合の[Djangoの`TextChoices`/`IntegerChoices`/](https://docs.djangoproject.com/en/4.2/ref/models/fields/#enumeration-types)を使用することは良い選択です。

### `MAP_AUTO_ID_AS_GLOBAL_ID`（デフォルトは`False`）

Trueの場合、モデルのIDを参照する`auto`フィールドは、`strawberry.ID`の代わりに`relay.GlobalID`にマッピングされます。
これは、もしすべてのモデル方が`relay.Node`から継承してして、`GlobalID`で機能させたい場合にとても便利です。

### `DEFAULT_PK_FIELD_NAME`（デフォルトは`"pk"`）

[CUDミューテーション](mutations.md#cud-mutations)のデフォルトのプライマリーキーフィールドを変更します。

### `USE_DEPRECATED_FILTERS`（デフォルトは`False`）

Trueの場合、[従来からのフィルター](filters.md#legacy-filtering)が有効になります。
これは前のバージョンから移行するために便利です。

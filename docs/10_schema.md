# スキーマ

すべてのGraphQL APIはスキーマを持ち、それはAPIのすべての機能を定義するために使用されます。
スキーマは、`Query`、`Mutation`そして`Subscription`の3つの[オブジェクト型](https://strawberry.rocks/docs/types/object-types)を渡すことで定義されます。

`Mutation`と`Subscription`はオプションである一方で、`Query`は常に必要です。

`Strawberry`を使用してスキーマを定義する例を次に示します。

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


schema = strawberry.Schema(query=Query)
```

`meanwhile`:【副詞】間に、そうしているうちに、それまでには、同時に、一方では

## 実行エラーの処理

デフォルトで`Strawberry`はクエリを実行中に遭遇したエラーを`strawberry.execution`ロガーにログを出力します。
この動作は、`strawberry.Schema`クラスで`process_errors`関数を上書きすることで変更されます。

デフォルトの機能を次のようになります。

```python
# strawberry/schema/base.py
from strawberry.types import ExecutionContext

logger = logging.getLogger("strawberry.execution")


class BaseSchema:
    ...
    def process_errors(
        self,
        errors: List[GraphQLError],
        execution_context: Optional[ExecutionContext] = None,
    ) -> None:
        for error in errors:
            StrawberryLogger.error(error, execution_context)
```

```python
# strawberry/utils/logging.py
from strawberry.types import ExecutionContext


class StrawberryLogger:
    logger: Final[logging.Logger] = logging.getLogger("strawberry.execution")

    @classmethod
    def error(
        cls,
        error: GraphQLError,
        execution_context: Option[ExecutionContext] = None,
        # https://www.python.org/dev/peps/pep-0484/#arbitrary-argument-lists-and-default-argument-values
        **logger_kwargs: Any,
    ) -> None:
        # "stack_info" is a boolean; check for None explicitly
        if logger_kwargs.get("stack_info") is None:
            logger_kwargs["stack_info"] = True

        logger_kwargs["stacklevel"] = 3

        cls.logger.error(error, exc_info=error.original_error, **logger_kwargs)
```

## フィールドのフィルタリング／カスタマイズ

`Schema`クラスをサブクラス化して、`get_fields`メソッドを上書きすることで、スキーマで公開されるフィールドをカスタ水できます。
例えば、公開そして内部APIのように、異なるGraphQL APIを作成するために、これを使用できます。

```python
@strawberry.type
class User:
    name: str
    email: str = strawberry.field(metadata={"tags": ["internal"]})


@strawberry.type
class Query:
    user: User


def public_field_filter(field: StrawberryField) -> bool:
    return "internal" not in field.metadata.get("tags", [])


class PublicSchema(strawberry.Schema):
    def get_fields(
        self, type_definition: StrawberryObjectDefinition
    ) -> List[StrawberryField]:
        return list(filter(public_field_filter, type_definition.fields))


schema = PublicSchema(query=Query)
```

---

注意事項

`get_fields`メソッドは、スキーマを作成するときに一度だけ呼び出されます。
これはスキーマを動的にカスタマイズするために使用されることを意図していません。

---

## フィールドの廃止

`deprecation_reason`引数を使用して、フィールドを廃止することができます。

---

注意事項

これはフィールドの使用を妨げず、ドキュメントのために使用されます。
[GraphQLフィールドの廃止](https://spec.graphql.org/June2018/#sec-Field-Deprecation)を参照してください。

---

```python
import datetime
from typing import Optional

import strawberry


@strawberry.type
class User:
    name: str
    dob: datetime.date
    age: Optional[int] = strawberry.field(deprecation_reason="Age is deprecated")
```

```graphql
type User {
  name: String!
  dob: Date!
  age: Int @deprecated(reason: "Age is deprecated")
}
```

# 例外

`Strawberry`は、`strawberry.exceptions`内のライブラリ特有の例外を定義しています。

## Strawberryスキーマ例外

### FieldWithResolverAndDefaultFactoryError

この例外は、`strawberry.field`が`resolver`と`default_factory`の両方で使用されているときに発生します。

```python
@strawberry.type
class Query:
    @strawberry.field(default_factory=lambda: "Example C")
    def c(self) -> str:
        return "I'm a resolver"


# '"Query"型の"c"フィールドはdefault_factoryとリゾルバーを定義できません'をスローします。
```

### FieldWithResolverAndDefaultValueError

この例外は、`strawberry.field`が`resolver`と`default`引数の両方で使用されているときに発生します。

```python
def test_resolver() -> str:
    return "I'm a resolver"


@strawberry.type
class Query:
    c: str = strawberry.field(default="Example C", resolver=test_resolver)


# '"Query"型の"c"フィールドはデフォルト値とリゾルバーを定義できません'をスローします。
```

### MissingTypesForGenericError

この例外は、`Generic`型がそれを具体的にする任意の型を渡すことなしで`Strawberry`スキーマに追加されたときに発生します。

### MultiStrawberryArgumentsError

この例外は、`strawberry.argument`が型注釈内で複数回使用されたときに発生します。

```python
from typing_extensions import Annotated

import strawberry


@strawberry.field
def name(
    argument: Annotated[
        str,
        strawberry.argument(description="This is a description"),
        strawberry.argument(description="Another description"),
    ]
) -> str:
    return "Name"


# フィールド名の`argument`引数の注釈は、複数の`strawberry.argument`を持つことができません。
```

### UnsupportedTypeError

この例外は、使用された型注釈が`strawberry.field`によってサポートされていないときに発生します。
記述している時点で、この例外は`pydantic`のみで使用されます。

```python
class Model(pydantic.BaseModel):
    field: pydantic.Json


@strawberry.experimental.pydantic.type(Model, fields=["field"])
class Type:
    pass
```

### WrongNumberOfResultsReturned

この例外は、データローダーがリクエストされたよりも異なる数の結果を返したときに発生します。

```python
async def idx(keys):
    return [1, 2, 3]


loader = DataLoader(load_fn=idx)

await loader.load(1)

# 'データローダー内で誤った数の結果を受け取りました。期待値: 1、受け取った数: 2'をスローします。
```

## 実行時例外

また、いくつかのエラーはクエリ（ミュテーションまたはサブスクリプション）の実行を試みているときにスローされます。

### MissingQueryError

この例外は、`request`に`query`引数がないときに発生します。

```python
client.post("/graphql", data={})

# 'リクエストデータが"query"値がありません'をスローします。
```

### UnallowedReturnTypeForUnion

このエラーは、`Union`の戻り値の型が、ユニオン型のリストにないときに発生します。

```python
@strawberry.type
class Outside:
    c: int


@strawberry.type
class A:
    a: int


@strawberry.type
class B:
    b: int


@strawberry.type
class Mutation:
    @strawberry.mutation
    def hello(self) -> Union[A, B]:
        return Outside(c=5)


query = """
    mutation {
        hello {
            __typename

            ... on A {
                a
            }

            ... on B {
                b
            }
        }
    }
"""

result = schema.execute_sync(query)
# result will look like:
# ExecutionResult(
#     data=None,
#     errors=[
#         GraphQLError(
#             "The type \"<class 'schema.Outside'>\" of the field \"hello\" is not in the list of the types of the union: \"['A', 'B']\"",
#             locations=[SourceLocation(line=3, column=9)],
#             path=["hello"],
#         )
#     ],
#     extensions={},
# )
```

### WrongReturnTypeForUnion

この例外は、ユニオン型が`strawberry.field`でないために、解決できないときに発生します。

```python
@strawberry.type
class A:
    a: int


@strawberry.type
class B:
    b: int


@strawberry.type
class Query:
    ab: Union[A, B] = "ciao"  # missing `strawberry.field` !


query = """{
    ab {
        __typename,

        ... on A {
            a
        }
    }
}"""

result = schema.execute_sync(query, root_value=Query())

# result will look like:
# ExecutionResult(
#     data=None,
#     errors=[
#         GraphQLError(
#             'The type "<class \'str\'>" cannot be resolved for the field "ab" , are you using a strawberry.field?',
#             locations=[SourceLocation(line=2, column=9)],
#             path=["ab"],
#         )
#     ],
#     extensions={},
# )
```

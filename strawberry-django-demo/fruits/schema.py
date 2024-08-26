import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from .types import Fruit


@strawberry.type
class Query:
    fruits: list[Fruit] = strawberry_django.field()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        DjangoOptimizerExtension,
    ],
)

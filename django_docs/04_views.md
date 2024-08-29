# APIの提供

`strawberry`は、ASGI（非同期）とWSGI（同期）の両方で機能します。
この統合は、Djangoを提供する両方の方法をサポートしています。

ASGIは、`strawberry`を楽しむ最善な方法であり、何らかの理由で利用できない場合を除き、強く推奨します。
WSGIを使用することで、[データローダー](https://strawberry.rocks/docs/guides/dataloaders)のような、いくつかの興味深い機能のサポートがなくなります。

## ASGI（非同期）で提供する

`urls.py`を設定して、ASGIで`strawberry`のAPIを次の通り公開します。

```python
# urls.py
from django.urls import path
from strawberry.django.views import AsyncGraphQLView

from .schema import schema

urlpatterns = [
    path("graphql", AsyncGraphWLView.as_view(schema=schema)),
]
```

## WSGI（同期）で提供する

`urls.py`を設定して、WSGIで`strawberry`のAPIを次の通り公開します。

```python
from django.urls import path
from strawberry.django.views import GraphQLView

from .schema import schema

urlpatterns = [
    path("graphql", GraphQLView.as_view(schema=schema)),
]
```

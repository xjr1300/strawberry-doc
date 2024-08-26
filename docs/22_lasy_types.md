# Lazy型

`Strawberry`は遅延型をサポートしており、それは型間で循環依存を持つときに便利です。

例えば、`Post`型のリストを持つ`User`型があり、それぞれの`Post`型が`User`フィールドを持つとします。
この場合、`Post`型の前に`User`型を定義できず、また逆も同様です。

これを解決するために、遅延型を使用できます。

```python
# posts.py
from typing import TYPE_CHECKING, Annotated

import strawberry

if TYPE_CHECKING:
    from .users import User


@strawberry.type
class Post:
    title: str
    author: Annotated["User", strawberry.lazy(".users")]
```

```python
# users.py
from typing import TYPE_CHECKING, Annotated

import strawberry

if TYPE_CHECKING:
    from .posts import Post


@strawberry.type
class User:
    name: str
    posts: List[Annotated["Post", strawberry.lazy(".posts")]]
```

`strawberry.lazy`と`Annotated`の組み合わせは、使用したい型のモジュールのパスを定義して、Pythonの型ヒントを利用できるようにする一方で、循環インポートを回避して、`TYPE_CHECKING`を使用して型チェッカーに型を検索する場所を指示することで型の安全性を維持します。

---

注意事項

`Annotated`はPython 3.9+でのみ利用可能です。
もし古いバージョンのPythonで使用する場合、代わりに`typing_extensions.Annotated`を使用できます。

```python
# users.py
from typing import TYPE_CHECKING, List
from typing_extensions import Annotated

import strawberry

if TYPE_CHECKING:
    from .posts import Post


@strawberry.type
class User:
    name: str
    posts: List[Annotated["Post", strawberry.lazy(".posts")]]
```

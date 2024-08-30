# よく尋ねられる質問（FAQ）

## リゾルバーでDjangoリクエストオブジェクトにアクセスする方法

リクエストオブジェクトは`get_request`メソッドを介してアクセスできます。

```python
from strawberry_django.auth.utils import get_request


def resolver(root, info: Info):
    request = get_request(info)
```

## リゾルバーで現在のユーザーオブジェクトにアクセスする方法

現在のユーザーオブジェクトは、`get_current_user`メソッドを介してアクセスできます。

```python
from strawberry_django.auto.queries import get_current_user


def resolver(root, info: Info):
    user = get_current_user(info)
```

## エディターの自動補完

VSCodeのようないくつかのエディターは、明示的な`strawberry.django`インポートなしで、シンボルと型を解決でないかもしれません。
この問題を修正するためにコードに次の行を追加してください。

```python
import strawberry_django
```

## プロジェクト例

完全なDjangoプロジェクトは、GitHubリポジトリの[examples/django](https://github.com/strawberry-graphql/strawberry-django/tree/main/examples/django)フォルダーを参照してください。

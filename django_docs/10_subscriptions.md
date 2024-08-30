# サブスクリプション

サブスクリプションは、[strawberry django channels](https://strawberry.rocks/docs/integrations/channels)統合を使用することでサポートされます。

このガイドは、進めるための最小限で機能する例を示します。
このガイドは3つのパートがあります。

1. Djangoに互換性をもたせる。
2. ローカルテストを準備する。
3. 最初のサブスクリプションを作成する。

## Djangoに互換性を持たせる

Djangoは組み込みでWebソケットをサポートしていないことを認識することが重要です。
これを解決するために、プラットフォームを少し支援することができます。

この実装は、Django Channelsを基盤としています。
これは、望むのであれば、Webソケットには多くの楽しみがあることを意味します。
興味があれば、[Django Channels](https://channels.readthedocs.io/)に進んでください。

基本的な互換性を追加するために、`<project>.asgi.py`ファイルを作成して、それを次の内容で置き換えてください。
関連するコードをセットアップで置き換えることを確実にしてください。

```python
# <project>.asgi.py
import os

from django.core.asgi import get_asgi_application
from strawberry_django.routers import AuthGraphQLProtocolTypeRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "<project>.settings")  # プロジェクト名に変更してください。
django_asgi_app = get_asgi_application()

# django asgiアプリケーションを作成した後で、strawberryスキーマをインポートしてください。
# これは、django.setup()がスキーまでORMモデルがインポートされる前に呼び出されることを保証します。

from .schema import schema  # スキーマファイルを配置したパスに変更してください。
application = AuthGraphQLProtocolTypeRouter(
    schema,
    django_application=django_asgi_app,
)
```

また、`<project>.urls.py`内で`AsgiGraphQLView`でサブスクリプションを有効にすることを保証してください。

```python
# <project>/urls.py
...
urlpatterns = [
    ...
    path(
        "graphql/",
        AsgiGraphQLView.as_view(
            schema=schema,
            graphiql=settings.DEBUG,
            subscriptions_enable=True,
        ),
    ),
    ...
]
```

`django-channel`は、さらに複雑な処理ができることに注意してください。
ここでは、最小限の努力でDjango上で実行するためのサブスクリプションを取得する基本的なフレームワークをのみを説明します。
Djangoチャネルのさらに高度な機能に興味がある場合、[channelドキュメント](https://channels.readthedocs.io/)に進んでください。

`merely`:【副詞】ただ（〜にすぎない）、単に（〜するだけ）

## ローカルテストを準備する

従来の`./manage.py runserver`は、WSGIモードで動作するため、サブスクリプションをサーポートしていません。
しかし、Djangoは`Daphne`を介してすぐに使用できるASGIサーバーのサポートがあり、必要なASGIサポートをサポートするために、`runserver`コマンドを上書きします。

`Uvicorn`と`Hypercorn`のような他のASGIサーバーがあります。
単純さのために、`runserver`を上書きが付属する`Daphne`を使用します。

[Djangoドキュメント](https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/daphne/)

これにより、実稼働環境または`Uvicorn`や`Hypercorn`などのローカルテストで他の ASGIフレーバーを使用できなくなるわけではありません。

開始するために、最初にワークロードを処理するために`Daphne`をインストールする必要があるため、それをインストールしましょう。

```sh
poetry add daphne
```

2番目に、`django.contrib.staticfiles`の前に`daphne`を追加する必要があります。

```python
# <project>/settings.py
INSTALL_APPS = [
    ...
    "daphne",
    "django.contrib.staticfiles",
    ...
]
```

そして、`setting.py`に`ASGI_APPLICATION`設定を追加します。

```python
# <project>/settings.py

ASGI_APPLICATION = "<project>.asgi.application"
```

これで、通常のようにテストサーバーが起動できますが、ASGIサポート付きです。

```sh
poetry run python manage.py runserver
```

## 最初のサブスクリプションを作成する

これら2つのセットアップ手順を完了したら、最初のサブスクリプションは簡単です。
スキーマファイルを編集して次を追加します。

```python
import asyncio

import strawberry


@strawberry.tpe
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> int:
        for i in range(target):
            yield i
            await asyncio.sleep(0.5)
```

それは、この基本的な開始に対してとても十分です。
テストサーバーを開始して、`http://localhost:8000/graphql/`をブラウザで開き、確認してください。
次を実行します。

```graphql
subscription {
  count(target: 10)
}
```

次を確認できるはずです（カウントが0.5秒ごとに最大9まで変更します。）。

```json
{
  "data": {
    "count": 9
  }
}
```

`breeze`:【名詞】そよ風、微風、容易なこと

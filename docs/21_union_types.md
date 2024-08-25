# ユニオン型

ユニオン型はインターフェイスと似ていますが、インターフェイスはすべての実装で共通でなくてはならないフィールドを指示する一方で、ユニオンをしません。
ユニオンは許可された型の選択肢を表現して、それらの型に要求をしません。
ここに、GraphQLスキーマ定義言語で表現されたユニオンを示します。

```graphql
union MediaItem = Audio | Video | Image
```

スキーマから`MediaItem`を返すときはいつでも、`Audio`、`Video`または`Image`を得るかもしれません。
ユニオン型のメンバーは具体的なオブジェクト型である必要があることに注意してください。
インターフェイス、他のユニオンまたはスカラーからユニオン型を作成できません。

ユニオンの良いユースケースは検索フィールドです。

```graphql
searchMedia(term: "strawberry") {
  ... on Autio {
    duration
  }
  ... on Video {
    thumbnailUrl
  }
  ... on Image {
    src
  }
}
```

ここで、`searchMedia`フィールドは`[mediaItem!]!`を返し、リストのメンバーはそれぞれ`MediaItem`ユニオンの部分です。
よって、それぞれのメンバーについて、どの種類のオブジェクトかによって、異なるフィールドを選択しなければなりません。
それを[インラインフラグメント](https://graphql.org/learn/queries/#inline-fragments)を使用して行っています。

`dictate`:【動詞】口述する、書き取らせる、指示する、命令する、〜に影響する

## ユニオンの定義

`Strawberry`に置いて、ユニオンを定義する2つの方法があります。

ユニオンメンバーの名前から型の名前を自動的に生成する`typing`モジュールの`Union`型を使用できます。

```python
from typing import Union

import strawberry


@strawberry.type
class Audio:
    duration: int


@strawberry.type
class Video:
    thumbnail_url: str


@strawberry.type
class Image:
    src: str


@strawberry.type
class Query:
    latest_media: Union[Audio, Video, Image]
```

```graphql
union AudioVideoImage = Audio | Video | Image

type Query {
  latestMedia: AudioVideoImage!
}

type Audio {
  duration: Int!
}

type Video {
  thumbnailUrl: String!
}

type Image {
  src: String!
}
```

または、もしユニオンの名前と説明を指定する必要がある場合、`strawberry.union`関数をもつ`Annotated`を使用できます。

```python
from typing import Union, Annotated

import strawberry


@strawberry.type
class Query:
    latest_media: Annotated[Union[Audio, Video, Image], strawberry.union("MediaItem")]
```

```graphql
union MediaItem = Audio | Video | Image

type Query {
  latestMedia: MediaItem!
}

type Audio {
  duration: Int!
}

type Video {
  thumbnailUrl: String!
}

type Image {
  src: String!
}
```

## ユニオンの解決

フィールドの戻り値の型がユニオンのとき、GraphQLは戻り値に使用する具体的なオブジェクト型を知る必要があります。
上の例で、それぞれの`MediaItem`は`Audio`、`Image`または`Video`型として分類されなければなりません。
これを行うために、リゾルバーからオブジェクト型のインスタンスを常に返す必要があります。

```python
from typing import Union

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def latest_media(self) -> Union[Audio, Video, Image]:
        return Video(
          thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/hq720.jpg",
        )
```

## 1つのメンバーのユニオン

時々、たった1つのメンバを持つユニオンを定義しなければならないかもしれません。
これは、将来さらに多くの型をユニオンに追加する場合など、スキーマの将来を保証することに役立ちます。

実は、Pythonの`typing.Union`は、このユースケースをサポートしていませんが、`Annotated`と`strawberry.union`を使用することで、たった1つのメンバーでユニオンを定義することを`Strawberry`に伝えることができます。

```python
from typing import Annotated

import strawberry


@strawberry.type
class Audio:
    duration: int


@strawberry.type
class Query:
    latest_media: Annotated[Audio, strawberry.union("MediaItem")]
```

```graphql
union MediaItem = Audio

type Query {
  latestMedia: MediaItem!
}
```

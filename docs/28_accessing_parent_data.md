# リゾルバーで親のデータにアクセスする

リゾルバーでフィールドの親からのデータにアクセスすることは、とても一般的です。
例えば、`User`に`fullName`フィールドを定義したいとします。
次がコードです。

```python
import strawberry


@strawberry.type
class User:
    first_name: str
    last_name: str
    full_name: str
```

```graphql
type User {
  firstName: String!
  lastName: String!
  fullName: String!
}
```

この場合、`full_name`は`first_name`と`last_name`フィールドにアクセスする必要があり、関数またはメソッドしてリゾルバーが定義されているかどうかに依存して、いくつかの選択肢があります。
関数としてリゾルバーを定義することから始めましょう。

## 関数リゾルバーで親のデータにアクセスする

```python
import strawberry


def get_full_name() -> str:
    ...


@strawberry.type
class User:
    first_name: str
    last_name: str
    full_name: str = strawberry.field(resolver=get_full_name)
```

リゾルバーは引数のない関数であるため、`Strawberry`にフィールドの親を渡すことを伝えるために、次のように`strawberry.Parent[ParentType]`型で引数を追加する必要があります。

```python
def get_full_name(parent: strawberry.Parent[User]) -> str:
    return f"{parent.first_name} {parent.last_name}"
```

`strawberry.Parent`は、`Strawberry`にフィールドの親の値を渡すことを伝えて、この場合は`User`です。

---

注意事項

`strawberry.Parent`は型引数を受け付け、それはコードを検証するために型チェッカーによって使用されます。

---

## ルートの使用

歴史的に、`Strawberry`は`root`と呼ばれる引数を追加することで、親の値を渡すことのみをサポートしていました。

```python
def get_full_name(root: User) -> str:
    return f"{root.first_name} {root.last_name}"
```

これままだサポートされていますが、`strawberry.Parent`は型注釈を使用する`Strawberry`の哲学に従うため、`strawberry.Parent`を使用することを推奨しています。
また、`strawberry.Parent`を持つ引数は、任意の名前を持ち、例えば次は動作します。

```python
def get_full_name(user: strawberry.Parent[User]) -> str:
    return f"{user.first_name} {user.last_name}"
```

## メソッドリゾルバーから親のデータにアクセスする

メソッドリゾルバーを定義したときも両方の選択肢が機能するため、メソッドして定義されたリゾルバーで`strawberry.Parent`を使用できます。

```python
import strawberry


@strawberry.type
class User:
    first_name: str
    last_name: str

    @strawberry.field
    def full_name(self, parent: strawberry.Parent[User]) -> str;
        return f"{parent.first_name} {parent.last_name}"
```

しかし、ここで、ことはより興味深いものになります。
これが純粋なPythonのクラスの場合、`self`を直接使用しますよね？
`Strawberry`は、これもサポートしていることがわかりました！

リゾルバーを更新しましょう。

```python
import strawberry


@strawberry.type
class User:
    first_name: str
    last_name: str

    @strawberry.field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

はるかに良いですよね？
リゾルバーメッソッドの`self`はとても便利で、それはPythonでの動作と同様に機能しますが、Pythonの意味論に正しく従わない場合があります。
これは、リゾルバーが実際には`Strawberry`によって性的メソッドであるかのように呼び出されるからです。

`full_name`フィールドがリクエストされたときに、何が発生するかを簡単なバージョンで確認しますよう。
それをするために、ユーザーを取得するフィールドも必要です。

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(first_name="Albert", last_name="Heijn")
```

次のようなクエリを実行したとき・・・

```graphql
{
  user {
    fullName
  }
}
```

次のコードのように、`Query`クラスの`user`関数を呼び指してから、`User`クラスで`full_name`関数を呼び出すように要求しています。

```python
user = Query().user()
full_name = user.full_name()
```

この場合これは機能する一方で、異なる型を返す場合は機能しません。
例えば、データベースからユーザーを取得するとき・・・

```python
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        # UserModelがデータベースからデータを取得して、
        # それが`first_name`と`last_name`を持つと仮定します。
        user = UserModel.objects.first()
        return user
```

この場合、`UserModel`は`full_name`関数を持っていないため、疑似コードは壊れています！
しかし、`Strawberry`を使用したとき、それは機能します（`UserModel`が`first_name`と`last_name`フィールドの両方を持つことを提供する場合）。

前述した通り、これは、`Strawberry`が次のようにリゾルバーを、クラスに拘束されていない簡単な関数であるかのようにクラス化しているためです。

```python
# まったくQueryには興味がないことに注意してください。
user = Query.user()   # これは`UserModel`です。

full_name = User.full_name(user)
```

多分、`staticmethod`のことを考えていると思いますが、それが現在扱っていることすべてです。
もし、クラスのメソッドしてリゾルバーを維持したいけれど、`self`まわりの魔法を除きたい場合、`strawberry.Parent`と`@staticmethod`デコレーターの組を使用できます。

```python
import strawberry


@strawberry.type
class User:
    first_name: str
    last_name: str

    @strawberry.field
    @staticmethod
    def full_name(parent: strawberry.Parent[User]) -> str:
        return f"{parent.first_name} {parent.last_name}"
```

`@staticmethod`と`strawberry.Parent`の組み合わせは、コードを明確にして、内部で何が発生しているかを気づかせる良い方法で、それはリンターと型チェッカーを幸せにし続けます。

`properly`:【副詞】適切に、妥当に、正当に、礼儀正しく、上品に、正確に、厳密に

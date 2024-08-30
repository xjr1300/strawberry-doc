# 権限

この統合は、権限を確認するために[Djangoの権限システム](https://docs.djangoproject.com/en/4.2/topics/auth/default/)に使用されるフィールドを拡張するために、フィールドの拡張を公開します。

それは、次のような場面で任意のフィールドを保護することをサポートします。

1. ユーザーが認証されている。
2. ユーザーがすーぱーゆーざーである。
3. ユーザーまたは所属するグループが権限を持っている。
4. ユーザーまたは所属するグループが値を解決する権限を持っている。
5. ユーザーまたは所属するグループがフィールドの親の権限を持っている。
6. など

## 機能させる方法

```text
graph TD
  A[Extension Check for Permissions] --> B;
  B[User Passes Checks] -->|Yes| BF[Return Resolved Value];
  B -->|No| C;
  C[Can return 'OperationInfo'?] -->|Yes| CF[Return 'OperationInfo'];
  C -->|No| D;
  D[Field is Optional] -->|Yes| DF[Return 'None'];
  D -->|No| E;
  E[Field is a 'List'] -->|Yes| EF[Return an empty 'List'];
  E -->|No| F;
  F[Field is a relay `Connection`] -->|Yes| FF[Return an empty relay 'Connection'];
  F -->|No| GF[Raises 'PermissionDenied' error];
```

## 例

```python
import strawberry_django
from strawberry_django.permissions import (
    IsAuthenticated,
    HasPerm,
    HasRetvalPerm,
)


@strawberry_django.type
class SomeType:
    login_required_field: RetType = strawberry_django.field(
        # will check if the user is authenticated
        extensions=[IsAuthenticated()],
    )
    perm_required_field: OtherType = strawberry_django.field(
        # will check if the user has `"some_app.some_perm"` permission
        extensions=[HasPerm("some_app.some_perm")],
    )
    obj_perm_required_field: OtherType = strawberry_django.field(
        # will check the permission for the resolved value
        extensions=[HasRetvalPerm("some_app.some_perm")],
    )
```

## 利用可能なオプション

利用可能なオプションは次のとおりです。

1. `IsAuthenticated`: ユーザーが認証されているか確認します（例えば、`user.is_authenticated`）。
2. `IsStaff`: ユーザーがスタッフメンバーか確認します（例えば、`user.is_staff`）。
3. `IsSuperuser`: ユーザーがスーパーユーザーか確認します（例えば、`user.is_superuser`）。
4. `HasPerm(perms: str | list[str], any_perm: bool = True)`: ユーザーが与えられた権限の一部またはすべてを持っているか確認します（例えば、`user.has_perm(perm)`）。
5. `HasSourcePerm(perms: str | list[str], any: bool = True)`: ユーザーがフィールドのルートに対して与えられた権限の一部またはすべてを持っているか確認します（例えば、`user.has_perm(perm)`）。
6. `HasRetvalPerm(perms: str | list[str], any: bool = True)`: 結果を解決して、ユーザーがどの具体的な値に対する与えられた権限の一部またはすべてを持っているか確認します（例えば、`user.has_perm(perm, retval)`）。もし戻り値がリストの場合、このエクステンションは、戻り値をフィルターして、検査に失敗したオブジェクトを削除します（他の可能性に関する詳細な情報は、次を確認してください）。

---

ℹ ノート

`HasSourcePerm`と`HasRetvalPerm`は、オブジェクトの権限を解決することをサポートする[認証バックエンド](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/)を必要とします。
このライブラリは、そのままで[django-guardian](https://django-guardian.readthedocs.io/en/stable/)と機能するため、これを使用している場合、他に何もするひつようはありません。

---

## 権限がないときの処理

条件が失敗したとき、次がフィールドに返されます（次の優先順序に従って）。

1. 戻り値の型として許されている場合は、`OperationInfo`/`OperationMessage`
2. フィールドが必須でない場合は`null`（例えば、`String`または`[String]`）
3. フィールドがリストの場合は空のリスト（例えば、`[String]!`）
4. 戻り値の方がrelayコネクションの場合は空の`Connection`
5. そうでない場合は、エラーが発生

## カスタム権限確認

`DjangoPermissionExtension`をサブクラス化して、`resolve_for_user`メソッドを実装することで、独自の権限確認拡張を作成できます。

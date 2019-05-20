import uuid

from tds import AliasStatement

parent_alias = 'parent_' + uuid.uuid4().__str__().replace('-', '')

p = AliasStatement(parent_alias)
ref = AliasStatement

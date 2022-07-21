from apiflask import Schema
from apiflask.fields import Boolean
from apiflask.fields import Integer
from apiflask.fields import List
from apiflask.fields import Nested
from apiflask.fields import String

from ..user.schemas import PublicUserOutSchema


class GroupInSchema(Schema):
    name = String(required=True)
    members = List(Integer())
    private = Boolean()


class GroupOutSchema(Schema):
    name = String()
    members = List(Nested(PublicUserOutSchema))
    manager = Nested(PublicUserOutSchema)
    private = Boolean()

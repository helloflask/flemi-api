from apiflask import Schema
from apiflask.fields import Boolean
from apiflask.fields import Integer
from apiflask.fields import List
from apiflask.fields import Nested
from apiflask.fields import String
from marshmallow.fields import Url

from ...extensions import ma
from ..user.schemas import PublicUserOutSchema


class CommentInSchema(Schema):
    body = String(required=True)
    post_id = Integer(required=True)
    reply_id = Integer()


class CommentOutSchema(Schema):
    id = Integer()
    body = String()
    author = Nested(PublicUserOutSchema)
    post = Nested(
        lambda: PostOutSchema(
            only=(
                "id",
                "title",
                "self",
            )
        )
    )
    replying = Nested(lambda: CommentOutSchema(exclude=("replying",)))
    self = ma.URLFor(".comment", values=dict(comment_id="<id>"))


class ColumnInSchema(Schema):
    name = String()
    post_ids = List(Integer())


class ColumnOutSchema(Schema):
    id = Integer()
    name = String()
    author = Nested(PublicUserOutSchema)
    posts = List(Nested(lambda: PostOutSchema(only=("id", "title", "self"))))
    self = ma.URLFor(".column", values=dict(column_id="<id>"))


class PostInSchema(Schema):
    title = String(required=True)
    content = String(required=True)
    private = Boolean(default=False)
    column_ids = List(Integer())


class PostOutSchema(Schema):
    id = Integer()
    title = String()
    content = String()
    coins = Integer()
    private = Boolean()
    author = Nested(PublicUserOutSchema)
    comments = List(Nested(CommentOutSchema, exclude=("post",)))
    columns = List(Nested(ColumnOutSchema, exclude=("posts", "author")))
    self = ma.URLFor("post.post", values=dict(post_id="<id>"))


class PostsSchema(Schema):
    posts = Nested(PostOutSchema(many=True))
    prev = Url()
    next = Url()
    total = Integer()


class CommentOutSchema(Schema):
    id = Integer()
    body = String()
    author = Nested(PublicUserOutSchema)
    post = Nested(
        lambda: PostOutSchema(
            only=(
                "id",
                "title",
                "self",
            )
        )
    )
    replying = Nested(lambda: CommentOutSchema(exclude=("replying",)))
    self = ma.URLFor(".comment", values=dict(comment_id="<id>"))

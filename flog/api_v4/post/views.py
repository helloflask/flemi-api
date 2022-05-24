from unicodedata import name
from flask.views import MethodView
from flask import request
from apiflask import APIBlueprint, abort

from .schemas import (
    ColumnInSchema,
    ColumnOutSchema,
    PostInSchema,
    PostOutSchema,
    PostsSchema,
    CommentInSchema,
    CommentOutSchema,
)
from ..auth.views import auth
from ...models import Post, Column, Comment
from ...extensions import db
from ...utils import clean_html
from ..decorators import permission_required, can_edit

post_bp = APIBlueprint("post", __name__)


@post_bp.route("/posts")
@post_bp.output(PostsSchema)
def all_posts():
    try:
        limit = request.args.get("limit", type=int)
        offset = request.args.get("offset", type=int)
    except ValueError:
        abort(400)
        return
    posts = Post.query.filter(~Post.private).all()
    posts_count = len(posts)
    start = offset
    end = min(start + limit, posts_count)
    prev = ""
    next = ""
    if start != 0:
        prev = f"/posts?limit={limit}&offset={offset-limit}"
    if end < posts_count - limit:
        next = f"/posts?limit={limit}&offset={offset+limit}"
    return {"posts": posts[start:end], "prev": prev, "next": next, "total": posts_count}


@post_bp.route("/post/<int:post_id>", endpoint="post")
class PostAPI(MethodView):
    @post_bp.output(PostOutSchema)
    def get(self, post_id: int):
        post = Post.query.get_or_404(post_id)

        if post.private:
            user = auth.current_user
            if user and post in user.posts:
                return post
            abort(403, "the post is private")
        return post

    @permission_required
    @can_edit("post")
    @post_bp.input(PostInSchema(partial=True))
    @post_bp.output(PostOutSchema)
    def put(self, post_id, data):
        post = Post.query.get(post_id)
        for attr, value in data.items():
            if attr == "content":
                post.content = clean_html(value)
            elif attr == "column_ids":
                for column_id in data[attr]:
                    column = Column.query.get_or_404(column_id)
                    post.columns.append(column)
            else:
                post.__setattr__(attr, value)
        db.session.commit()
        return post

    @permission_required
    @can_edit("post")
    @post_bp.output({}, 204)
    def delete(self, post_id: int):
        post = Post.query.get(post_id)
        post.delete()


@post_bp.post("/post")
@permission_required
@post_bp.input(PostInSchema)
@post_bp.output({}, 201)
def create_post(data):
    post = Post(author=auth.current_user)
    for attr, value in data.items():
        if attr == "content":
            post.content = clean_html(value)
        elif attr == "column_ids":
            for column_id in data[attr]:
                column = Column.query.get_or_404(column_id)
                post.columns.append(column)
        else:
            post.__setattr__(attr, value)
    db.session.add(post)
    db.session.commit()
    return {}, 201


@post_bp.route("/column/<int:column_id>", endpoint="column")
class ColumnAPI(MethodView):
    @post_bp.output(ColumnOutSchema)
    def get(self, column_id):
        column = Column.query.get_or_404(column_id)
        return column

    @permission_required
    @can_edit("column")
    @post_bp.input(ColumnInSchema(partial=True))
    @post_bp.output(ColumnOutSchema)
    def put(self, column_id, data):
        column = Column.query.get(column_id)
        if data.get("name"):
            column.name = name
        if data.get("post_ids"):
            column.posts = []
            for post_id in data["post_ids"]:
                post = Post.query.get(post_id)
                if post is None:
                    abort(404, f"post {post_id} not found")
                column.posts.append(post)
        db.session.commit()
        return column

    @permission_required
    @can_edit("column")
    @post_bp.output({}, 204)
    def delete(self, column_id):
        column = Column.query.get(column_id)
        db.session.delete(column)
        db.session.commit()


@post_bp.post("/column")
@permission_required
@post_bp.input(ColumnInSchema)
@post_bp.output({}, 201)
def create_column(data):
    column = Column(author=auth.current_user, name=data["name"])
    for post_id in data["post_ids"]:
        post = Post.query.get(post_id)
        if post is None:
            abort(404, f"post {post_id} not found")
        column.posts.append(post)
    db.session.add(column)
    db.session.commit()
    return {}, 201


@post_bp.route("/comment/<int:comment_id>", endpoint="comment")
class CommentAPI(MethodView):
    @post_bp.output(CommentOutSchema)
    def get(self, comment_id: int):
        return Comment.query.get_or_404(comment_id)

    @permission_required
    @can_edit("comment")
    @post_bp.input(CommentInSchema(partial=True))
    @post_bp.output(CommentOutSchema)
    def put(self, comment_id: int, data):
        comment = Comment.query.get(comment_id)
        for attr, value in data.items():
            if attr == "reply_id":
                comment.replied = Comment.query.get_or_404(value)
            elif attr == "post_id":
                post = Post.query.get_or_404(value)
                if post.private:
                    abort(400, "the post is private")
                comment.post = post
            elif attr == "body":
                comment.body = clean_html(value)
        db.session.commit()
        return comment

    @permission_required
    @can_edit("comment")
    @post_bp.output({}, 204)
    def delete(self, comment_id: int):
        comment = Comment.query.get(comment_id)
        comment.delete()


@post_bp.post("/comment")
@permission_required
@post_bp.input(CommentInSchema)
@post_bp.output({}, 201)
def create_comment(data):
    comment = Comment(
        author=auth.current_user,
        body=clean_html(data["body"]),
    )
    post = Post.query.get_or_404(data["post_id"])
    if post.private:
        abort(400, "the post is private")
    comment.post = post
    if data.get("reply_id"):
        comment.replied = Comment.query.get_or_404(data["reply_id"])
        if comment.replied not in comment.post.comments:
            abort(
                400,
                "the comment you reply does not belong to the post",
            )
    db.session.add(comment)
    db.session.commit()
    return {}, 201

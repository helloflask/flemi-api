"""
MIT License
Copyright (c) 2020 Andy Zhou
"""

import hashlib
import os
from datetime import datetime
from datetime import timedelta
from time import time

from authlib.jose import jwt
from authlib.jose.errors import JoseError
from flask import current_app
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .extensions import db
from .shop_items import items


group_user_table = db.Table(
    "group_user",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("group_id", db.Integer, db.ForeignKey("group.id")),
    extend_existing=True,
)

column_post_table = db.Table(
    "column_post",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("column_id", db.Integer, db.ForeignKey("column.id")),
    extend_existing=True,
)

coin_table = db.Table(
    "coin_table",
    db.Column("owner_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    extend_existing=True,
)

Collect = db.Table(
    "collect",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Belong(db.Model):
    """
    A model describing the relationship of user and shop items.
    """

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(
        db.Integer(),
        db.ForeignKey("user.id"),
    )
    goods_id = db.Column(
        db.Integer(),
    )
    expires = db.Column(db.DateTime)
    owner = db.relationship("User", back_populates="belongings")

    def __str__(self):
        return f"<Belong relationship {self.goods_id} -> User {self.owner_id}>"

    def load_expiration_delta(self):
        delta = self.expires - datetime.utcnow()
        return delta


class Post(db.Model):
    """
    A model for posts.
    """

    # Post id
    id = db.Column(db.Integer, primary_key=True)

    # Initial information
    title = db.Column(db.String(128), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="posts")
    content = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    private = db.Column(db.Boolean, default=False)

    # Others
    comments = db.relationship("Comment", back_populates="post")
    columns = db.relationship(
        "Column", secondary=column_post_table, back_populates="posts"
    )
    coins = db.Column(db.Integer, default=0)
    coiners = db.relationship(
        "User", secondary=coin_table, back_populates="coined_posts"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    @property
    def picked(self):
        """
        Decide whether a post is picked.
        """
        # key HOT_POST_COIN must be included in config.
        return self.coins >= current_app.config["HOT_POST_COIN"]

    def delete(self):
        """
        Delete a post.
        """
        db.session.delete(self)
        db.session.commit()

    def add_coin(self, coin_num: int, current_user):
        """
        Give a certain number of coins to a post.
        """
        if coin_num not in (
            1,
            2,
        ):  # Used when a user put an invalid number of coins.
            return "Invalid coin!"
        if self in current_user.coined_posts:  # A post cannot be recoined.
            return "Invalid coin!"
        if self.author == current_user:  # Used for flemio, so that flemio CLI users
            return "You can't coin yourself."  # cannot give coins to their own posts.

        amount = coin_num
        if current_user.coins < amount:  # A user must have enough coin to give.
            return "Not enough coins."

        current_user.coined_posts.append(self)
        current_user.coins -= amount
        current_user.experience += amount * 10
        self.coins += amount

        if self.author:  # The author will be given 1/4
            self.author.coins += amount / 4  # of the number of coins given.
            self.author.experience += amount * 10

        db.session.commit()


class Column(db.Model):
    """
    A column of posts.
    """

    # Initial information
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), unique=True)
    posts = db.relationship(
        "Post", secondary=column_post_table, back_populates="columns"
    )
    author = db.relationship("User", back_populates="columns")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def coins(self):
        """
        The total coins of the column.
        """
        return sum(post.coins for post in self.posts)

    @property
    def topped(self):
        """
        Working like picking posts.
        """
        return self.coins() >= current_app.config["HOT_COLUMN_COIN"]

    def delete(self):
        """
        Delete a column. (Posts inside will be okay)
        """
        db.session.delete(self)
        db.session.commit()


class Comment(db.Model):
    """
    A Comment Model.
    """

    # Initial information
    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
    flag = db.Column(db.Integer, default=0)

    # comment reply
    replied_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    replies = db.relationship("Comment", back_populates="replied", cascade="all")
    replied = db.relationship("Comment", back_populates="replies", remote_side=[id])

    def delete(self):
        """
        Delete a comment.
        """
        db.session.delete(self)
        db.session.commit()


class Notification(db.Model):
    """
    The model of Notification.
    """

    # Initial information
    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver = db.relationship("User", back_populates="notifications")

    def push(self):
        """
        Push a notification to the user.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete a notification.
        """
        db.session.delete(self)
        db.session.commit()


class Image(db.Model):
    """
    A Image file uploaded to server.
    """

    # Initial information
    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(512), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="images")
    private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def url(self) -> str:
        return url_for("image.uploaded_files", filename=self.filename, _external=True)

    def path(self) -> str:
        return os.path.join(current_app.config["UPLOAD_DIRECTORY"], self.filename)

    def toggle_visibility(self) -> None:
        """
        Change the visibility of the image uploaded.
        """
        self.private = not self.private
        db.session.commit()

    def delete(self) -> None:
        """
        Delete an image (from the server).
        """
        try:
            os.remove(self.path())
        except FileNotFoundError:
            pass
        db.session.delete(self)
        db.session.commit()


class Group(db.Model):
    """
    A Group model used for chat.
    """

    # Initial information
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), unique=True)
    members = db.relationship(
        "User", secondary=group_user_table, back_populates="groups"
    )
    manager = db.relationship("User", back_populates="managed_groups")
    manager_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    messages = db.relationship("Message", back_populates="group")
    private = db.Column(db.Boolean, default=False)

    def delete(self):
        """
        Delete a group.
        """
        db.session.delete(self)
        db.session.commit()


class Message(db.Model):
    """
    Message Model in the group.
    """

    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="messages")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="sent_messages")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class User(db.Model):
    """
    User model.
    """

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256))
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship("Post", back_populates="author")
    avatar_hash = db.Column(db.String(32))

    locked = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())

    collections = db.relationship(
        "Post", secondary=Collect, backref=db.backref("collectors")
    )

    locale = db.Column(db.String(16))

    columns = db.relationship("Column", back_populates="author")

    comments = db.relationship("Comment", back_populates="author", cascade="all")
    notifications = db.relationship(
        "Notification", back_populates="receiver", cascade="all"
    )
    images = db.relationship("Image", back_populates="author", cascade="all")
    groups = db.relationship(
        "Group", secondary=group_user_table, back_populates="members"
    )
    managed_groups = db.relationship("Group", back_populates="manager")
    custom_avatar_url = db.Column(db.String(128), default="")
    sent_messages = db.relationship("Message", back_populates="author")
    coins = db.Column(db.Float, default=3)
    experience = db.Column(db.Integer, default=0)
    coined_posts = db.relationship(
        "Post", secondary=coin_table, back_populates="coiners"
    )

    belongings = db.relationship("Belong", back_populates="owner")

    avatar_style_id = db.Column(db.Integer(), default=0)

    clicks = db.Column(db.Integer(), default=0)
    clicks_today = db.Column(db.Integer(), default=0)

    default_status = db.Column(db.String(64), default="online")
    # online, idle, focus, offline

    remote_addr = db.Column(db.String(), default="")

    password_update = db.Column(db.Float(), default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return f"<User '{self.username}'>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_administrator(self):
        return self.is_admin

    def verify_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def can(self, perm) -> bool:
        return not self.locked

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode("utf-8")).hexdigest()

    def avatar_url(self, size=30):
        if self.custom_avatar_url:
            return self.custom_avatar_url
        url = "https://rice0208.pythonanywhere.com/silicon/v1"  # use silicon generator
        hash = self.avatar_hash or self.gravatar_hash()
        return f"{url}/{hash}?s={size}"

    def ping(self, force_time=None):
        now = datetime.utcnow() if force_time is None else force_time
        last_seen_day = datetime(
            self.last_seen.year, self.last_seen.month, self.last_seen.day
        )
        self.coins = self.coins or 3.0  # maybe this account is processed
        if now - last_seen_day >= timedelta(days=1):
            self.coins += 1
            self.clicks_today = 0
        self.last_seen = now
        db.session.commit()

    def auth_token(self):
        header = {"alg": "HS256"}
        payload = {"uid": self.id, "time": time()}
        return jwt.encode(header, payload, current_app.config["SECRET_KEY"]).decode()

    def gen_email_verify_token(self):
        header = {"alg": "HS256"}
        payload = {"uid": self.id, "email": self.email, "time": time()}
        token = jwt.encode(header, payload, current_app.config["SECRET_KEY"]).decode()
        return token

    @staticmethod
    def verify_email_token(self, token: str):
        try:
            data = jwt.decode(token.encode("ascii"), current_app.config["SECRET_KEY"])
            if data.get("time") + 900 > time():
                self.confirmed = True
                return True
            raise JoseError("Token expired")
        except JoseError:
            self.confirmed = False
            return False

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def collect(self, post):
        if not self.is_collecting(post):
            self.collections.append(post)
            db.session.commit()

    def uncollect(self, post):
        if post in self.collections:
            self.collections.remove(post)
            db.session.commit()

    def is_collecting(self, post):
        return post in self.collections

    def join_group(self, group) -> None:
        self.groups.append(group)
        db.session.add(self)
        db.session.add(group)
        db.session.commit()

    def in_group(self, group) -> bool:
        return self in group.members

    def lock(self):
        self.locked = True
        db.session.commit()

    def unlock(self):
        self.locked = False
        db.session.commit()

    def level(self) -> int:
        if self.experience < 100:
            return 1
        elif self.experience < 200:
            return 2
        elif self.experience < 350:
            return 3
        elif self.experience < 550:
            return 4
        elif self.experience < 800:
            return 5
        elif self.experience < 1100:
            return 6
        elif self.experience < 1500:
            return 7
        elif self.experience < 2500:
            return 8
        else:
            lv = 9
            while (lv - 8) * (lv - 7) * 100 + 2500 <= self.experience:
                lv += 1
            return lv

    def level_badge_link(self) -> str:
        """
        The link of a level badge
        """
        lv = self.level()
        prefix = "https://img.shields.io/badge/Lv" + str(min(lv, 9)) + "%20"
        if lv <= 8:
            color = ""
            if lv == 1:
                color = "eee"
            elif lv == 2:
                color = "ff9"
            elif lv == 3:
                color = "afa"
            elif lv == 4:
                color = "5d5"
            elif lv == 5:
                color = "0dd"
            elif lv == 6:
                color = "00f"
            elif lv == 7:
                color = "da3"
            elif lv == 8:
                color = "f00"
            return prefix + "-" + color
        else:
            plus = lv - 9
            return prefix + "%2B" + str(plus) + "-808"

    def load_belongings(self):
        belongings = [
            item for item in self.belongings if item.expires > datetime.utcnow()
        ]
        return belongings

    def load_belongings_id(self):
        return [item.goods_id for item in self.load_belongings()]

    def load_avatar_style(self, size=36):
        if self.avatar_style_id is None:
            self.avatar_style_id = 0
            db.session.commit()
        style = items(self.avatar_style_id).style
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style.format(size / 160)
        return ""

    def load_username_style(self):
        if self.avatar_style_id is None:
            self.avatar_style_id = 0
            db.session.commit()
        style = items(self.avatar_style_id).text_style
        if self.avatar_style_id in [item.goods_id for item in self.load_belongings()]:
            return style
        return ""

    def word_count(self):
        """
        The length of content.
        """
        return sum(len(post.content) for post in self.posts)

    def get_alpha(self):
        """
        Get the Alpha Index describing how a user is in the site.
        """

        def _get_recent_posts(user):
            return [
                post
                for post in user.posts
                if (datetime.utcnow() - post.timestamp < timedelta(days=21))
            ]

        def _get_recent_comments(user):
            return [
                comment
                for comment in user.comments
                if (datetime.utcnow() - comment.timestamp < timedelta(days=21))
            ]

        v5 = (
            (True if self.name else False)
            + (True if self.location else False)
            + (len(self.about_me or "hello world") >= 20)
        ) / 3

        def _get_total_post_content(user):
            return sum(len(p.content) for p in _get_recent_posts(user))

        def _get_total_comment(user):
            return sum(len(c.body) for c in _get_recent_comments(user))

        def _get_total_coins_in_posts(user):
            return sum(p.coins for p in _get_recent_posts(user))

        def _get_recent_coined_posts(user):
            return [
                post
                for post in user.coined_posts
                if (datetime.utcnow() - post.timestamp < timedelta(40))
            ]

        def _get_total_coins_given(user):
            return sum(p.coins for p in _get_recent_coined_posts(user))

        pc, cc, tc, tc_ = (
            _get_total_post_content(self),
            _get_total_comment(self),
            _get_total_coins_in_posts(self),
            _get_total_coins_given(self),
        )

        def _get_preportion(self_count, func):
            max_count = max(func(user) for user in User.query.all())
            return 0 if max_count == 0 else self_count / max_count

        v1 = _get_preportion(pc, _get_total_post_content)
        v2 = _get_preportion(cc, _get_total_comment)
        v3 = _get_preportion(tc, _get_total_coins_in_posts)
        v4 = _get_preportion(tc_, _get_total_coins_given)

        pi = 3.141592653589793
        s2 = 1.4142135623730951
        return (
            (v1 * pi / 2 + v2 * pi / 2 + v3 * pi / 2 + v4 * pi / 4 + v5 * pi / 4)
            * 100
            / (4 * s2)
        ).__round__(2)

    def ping_update_ai(self):
        now = datetime.utcnow()
        sl = datetime.utcfromtimestamp(self.last_update) or datetime(
            2000, 1, 1, 0, 0, 0, 0
        )
        if now >= datetime(
            year=sl.year, month=sl.month, day=sl.day, hour=(sl.hour // 12 + 1) * 12
        ):
            self.alpha_index = self.get_alpha()
            self.last_update = now

    def post_count(self):
        return len(self.posts)

    def post_coins(self):
        return sum(post.coins for post in self.posts)

    def post_collects(self):
        return sum(len(post.collectors) for post in self.posts)

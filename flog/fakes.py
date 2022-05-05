from random import randint
from faker import Faker
from rich import print
from rich.progress import track
from .utils import lower_username
from .models import (
    db,
    Post,
    User,
    Comment,
    Notification,
    Group,
    Column,
    Message,
)

fake = Faker()


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#           WARNING:   DO NOT USE FAKE DATA IN PRODUCTION ENVIRONMENT!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def users(count: int = 10) -> None:
    """Generates fake users"""

    print(f"\ngenerating users: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        name = fake.name()
        username = lower_username(name)
        # Ensure the username is unique.
        if User.query.filter_by(username=username).first() is not None:
            continue
        user = User(
            username=username,
            name=name,
            email=fake.email(),
            confirmed=True,
        )
        user.set_password("123456")
        db.session.add(user)
    db.session.commit()


def posts(count: int = 10) -> None:
    """Generates fake posts"""
    print(f"\ngenerating posts: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        post = Post(
            title=fake.word() + " " + fake.word(),
            content=fake.text(randint(100, 300)),
            timestamp=fake.date_time_this_year(),
            author=User.query.get(randint(1, User.query.count())),
            private=bool(randint(0, 1)),
        )
        db.session.add(post)
    db.session.commit()


def comments(count: int = 10) -> None:
    """Generates fake comments for posts."""
    print(f"\ngenerating comments: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        filt = Post.query.filter(~Post.private)
        comment = Comment(
            author=User.query.get(randint(1, User.query.count())),
            post=filt.all()[randint(1, filt.count() - 1)],
            body=fake.text(),
        )
        db.session.add(comment)
    db.session.commit()


def notifications(count: int, receiver: User = None) -> None:
    """Generates fake notifications"""
    print(f"\ngenerating notifications: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        if receiver is None:
            admin = User.query.filter_by(is_admin=True).first()
            receiver = admin
        notification = Notification(
            message=fake.sentence(),
            receiver=receiver,
        )
        db.session.add(notification)
    db.session.commit()


def groups(count: int) -> None:
    """Generates fake user groups"""
    print(f"\ngenerating groups: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        manager = User.query.get(randint(1, User.query.count()))
        group = Group(name=fake.sentence(), manager=manager)
        if manager:
            manager.join_group(group)
            db.session.add(group)
    db.session.commit()


def columns(count: int) -> None:
    print(f"\ngenerating columns: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        posts = list(
            set(Post.query.get(randint(1, Post.query.count())) for _ in range(5))
        )
        author = User.query.get(randint(1, User.query.count()))
        column = Column(name=fake.sentence(), author=author, posts=posts)
        db.session.add(column)
    db.session.commit()
    top = Column.query.get(randint(1, Column.query.count()))
    while top is None:
        top = Column.query.get(randint(1, Column.query.count()))
    db.session.commit()


def messages(count: int) -> None:
    print(f"\ngenerating messages: [magenta]{count}[/magenta]")
    for _ in track(range(count), description="progress"):
        group = Group.query.get(randint(1, Group.query.count()))
        message = Message(group=group, body=fake.sentence())
        db.session.add(message)
    db.session.commit()

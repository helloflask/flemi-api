import os
import click
from flask import Flask
from rich import print
from .auth import register_auth_group
from .cli import confirm


def register_commands(app: Flask, db):  # noqa: C901
    @app.cli.command()
    def test() -> None:
        """Run the unittests."""
        os.system("pytest -v")

    @app.cli.command()
    def create_admin():
        """Create administrator account"""
        from ..models import User

        username = app.config["FLOG_ADMIN"]
        email = app.config["FLOG_ADMIN_EMAIL"]
        password = app.config["FLOG_ADMIN_PASSWORD"]

        print("\ncreating administrator account ...")
        print("[yellow]username[/yellow]: [green]%s[/green]" % username)
        print("[yellow]email[/yellow]: [green]%s[/green]" % email)

        if (
            User.query.filter_by(email=email).count()
            + User.query.filter_by(username=username).count()
            == 0
        ):
            admin = User(username=username, email=email, name=username, confirmed=True)
            admin.set_password(password)
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            print("[green]Success![/green]\n")
        else:
            print(
                f"\n[red]Fatal[/red]: user matching email ([green]{email}[/green]) "
                f"or username ([green]{username}[/green]) excceeded "
                "(limit: [magenta]1[/magenta])\n"
            )

    @app.cli.command()
    @click.option("--users", default=20, help="Generates fake users")
    @click.option("--posts", default=200, help="Generates fake posts")
    @click.option("--comments", default=100, help="Generates fake comments")
    @click.option("--notifications", default=10, help="Generates fake notifications")
    @click.option("--groups", default=20, help="Generates fake groups")
    @click.option("--columns", default=20, help="Generate fake columns")
    @click.option("--messages", default=300, help="Generate fake messages")
    def forge(
        users,
        posts,
        comments,
        notifications,
        groups,
        columns,
        messages,
    ):
        """Generates fake data"""
        print(
            "\n[yellow]WARNING[/yellow]: the forge command is for development use. "
            + "it will generate fake data which may mess up your database with a lot of "
            + "[red]bullshit[/red], and deleting them from your database is pretty hard."
        )
        confirm("would you like to continue?", otherwise=exit)

        print("\ngenerating fake data ...")
        from .. import fakes as fake

        fake.users(users)
        fake.posts(posts)
        fake.comments(comments)
        fake.notifications(notifications)
        fake.groups(groups)
        fake.columns(columns)
        fake.messages(messages)

        print("\n[green]Success![/green]\n")

    @app.cli.command()
    @click.option("--drop/--no-drop", help="Drop database or not")
    def init_db(drop: bool = False) -> None:
        """Initialize database on a new machine."""
        print(
            "\n[yellow]WARNING[/yellow]: the init-db command will initialize "
            + "your database, which may be destructive to your data."
        )
        confirm("would you like to continue?", otherwise=exit)
        print("\n")
        if drop:
            print("dropping the database ...")
            db.drop_all(app=app)
        print("initializing the database ...\n")
        db.create_all(app=app)

    @app.cli.command()
    def deploy():
        """Run deployment tasks"""

        print("\ndeployment tasks start.")
        from flask_migrate import upgrade, stamp

        try:
            # upgrade the database.
            print("upgrading from [yellow]flask-migrate[/yellow]")
            upgrade()
            print("[green]Success![/green]")
        except:
            # I forgot to run `flask db migrate` at the beginning of the project,
            # so I have to init the database like this.
            print("upgrade fails, initializing ...")
            db.create_all()
            print("stamping ...")
            stamp()
            print("[green]Success![/green]")
        print("\n")

    register_auth_group(app=app, db=db)

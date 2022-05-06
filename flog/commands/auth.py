from flask import Flask
from getpass import getpass
from halo import Halo
from rich import print
from .cli import confirm, check, int_input
from ..models import User
import re


def register_auth_group(app: Flask, db):
    @app.cli.group()
    def auth():
        """
        Authentication commands.
        """
        pass

    @auth.command()
    def register():
        """
        Create a new account.
        """
        print("\n[yellow]username[/yellow]: ", end="")
        username = input("")

        spinner_username = Halo(text="verifying username ...", spinner="dots")
        spinner_username.start()
        if User.query.filter_by(username=username).count() != 0:
            spinner_username.fail(text="verify username failed")
            print(
                f"[red]Fatal[/red]: username [green]{username}[/green] already exists.\n"
            )
            exit(0)
        if not re.match("^[A-Za-z]([A-Za-z0-9_\-.]){5,11}$", username):
            spinner_username.fail(text="verify username failed")
            print(
                "[red]Fatal[/red]: match pattern fails: "
                "[cyan]^[A-Za-z]([A-Za-z0-9_-.]){5,11}$[/cyan] "
                f"(invalid username [green]{username}[/green])\n"
            )
            exit(0)
        spinner_username.succeed(text="verify username success")

        print("[yellow]email[/yellow]: ", end="")
        email = input("")

        spinner_email = Halo(text="verifying email ...", spinner="dots")
        spinner_email.start()
        if User.query.filter_by(email=email).count() != 0:
            spinner_email.fail(text="verify email failed")
            print(f"[red]Fatal[/red]: email [green]{email}[/green] already exists.\n")
            exit(0)
        if not re.match("^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", email):
            spinner_email.fail(text="verify email failed")
            print(
                f"[red]Fatal[/red]: match pattern fails (invalid email [green]{email}[/green])\n"
            )
            exit(0)
        spinner_email.succeed(text="verify email success")

        print("[yellow]name[/yellow]: ", end="")
        name = input("")

        spinner_name = Halo(text="verifying name ...", spinner="dots")
        spinner_name.start()
        if not 1 < len(name) <= 64:
            spinner_name.fail(text="verify name failed")
            print(
                f"[red]Fatal[/red]: max length of content is 64 (currently {len(name)})\n"
            )
            exit(0)
        spinner_name.succeed(text="verify name success")

        print("[yellow]about[/yellow] [green]\[Optional][/green]: ", end="")
        about = input("")

        print("[yellow]location[/yellow] [green]\[Optional][/green]: ", end="")
        location = input("")

        print("[yellow]password[/yellow]: ", end="")
        passwd = getpass("")

        print("[yellow]password again[/yellow]: ", end="")
        passwd_again = getpass("")

        spinner_pwd = Halo(text="verifying password ...", spinner="dots")
        spinner_pwd.start()
        if passwd != passwd_again:
            spinner_pwd.fail(text="verify password failed")
            print("[red]Fatal[/red]: password not match\n")
            exit(0)

        spinner_pwd.succeed(text="verify password success")

        u = User(
            username=username, email=email, name=name, about_me=about, location=location
        )

        u.set_password(passwd)

        def register_exit():
            db.session.add(u)
            db.session.commit()
            print("\ncreate user [green]success[/green]!\n")
            exit(0)

        print("\n[green]Nice![/green] the basic information is now ready.")

        confirm(prompt="want to make advanced configuration?", otherwise=register_exit)

        print("")
        if check(f"is [green]{username}[/green] an [yellow]administrator[/yellow]?"):
            u.is_admin = True

        if check(f"is [green]{username}[/green] [yellow]locked[/yellow]?"):
            u.locked = True

        u.coins = int_input(
            f"set initial [yellow]coins[/yellow] for [green]{username}[/green] (default to 3): ",
            default=3,
        )

        u.experience = int_input(
            f"set initial [yellow]EXP[/yellow] for [green]{username}[/green] (default to 0): ",
            default=0,
        )

        register_exit()

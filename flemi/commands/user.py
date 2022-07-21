import click
from flask import Flask


def register_user_group(app: Flask, db):
    @app.cli.group()
    def user():
        """
        User commands
        """
        pass

    @user.command()
    @click.option("--username", default=None, help="query from username")
    @click.option("--email", default=None, help="query from email")
    @click.option("--name", default=None, help="query from name")
    @click.option("--location", default=None, help="query from location")
    def query():
        """
        user query to id (returns list)
        """

from random import randint
from rich import print
from ..extensions import db


def confirm(prompt, otherwise):
    while True:
        print(prompt, end="")
        answer = input(" [Y/n] ")
        if answer in "YyNn" and len(answer) == 1:
            if answer in "Nn":
                print("[yellow]WARNING[/yellow]: operation cancelled by user.\n")
                otherwise()
            else:
                break
        else:
            print(
                "[red]Fatal[/red]: please choose [green]Y[/green] or [green]n[/green]"
            )
            continue


def check(prompt):
    while True:
        print(prompt, end="")
        answer = input(" [Y/n] ")
        if answer in "YyNn" and len(answer) == 1:
            return answer in "Yy"
        print("[red]Fatal[/red]: please choose [green]Y[/green] or [green]n[/green]")


def int_input(prompt: str, default=None, auto_default: bool = False):
    while True:
        print(prompt, end="")
        answer = input("")
        try:
            return int(answer)
        except:
            if (default is not None) and (auto_default or answer == ""):
                return default
            print(f"[red]Fatal[/red]: integer is required (e.g. {randint(3, 99)})")

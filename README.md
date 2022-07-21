# Flemi API

> **Tips:** This repository is still under construction.

This project is the new version of z-t-y/Flog.

This written is written to be the back-end of this website project, there's also a front-end
project of Flemi (using React.js).

## How to install

Flemi API uses [PDM](https://github.com/pdm-project/pdm) to manage its dependencies,
so you should install PDM first:

```powershell
pip install pipx
pipx install pdm
```

then install with PDM:

```powershell
pdm install
```

To initialize Flemi API, you must make the database and administrator ready with command:

```powershell
flask deploy
flask create-admin
```

If you want to generate fake data for testing, you should use command `flask forge` after
running the command above.

Then you can run our Flemi API. In most cases just use `flask run`, but if you use servers
like PythonAnywhere, Heroku, etc. Read its docs and go on.

## Credits

Flemi project is created by [@z-t-y](https://github.com/z-t-y). Now maintained by [helloflask/floggers](https://github.com/orgs/helloflask/teams/floggers). See contributors for more information.

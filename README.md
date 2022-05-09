# Flog API v4

> **Tips:** This repository is still under construction.

This project is actually a side project of z-t-y/Flog, working as Flog's new web API.
There's currently 3 API versions in Flog repository, and, because of this, this project
is version 4.

API v4 is written to be the back-end of this website project, there's also a front-end
project of Flog (using React.js).

## How to install

Flog API v4 uses [PDM](https://github.com/pdm-project/pdm) to manage its dependencies,
so you should install PDM first:

```powershell
pip install pipx
pipx install pdm
```

then install with PDM:

```powershell
pdm install
```

To initialize Flog API, you must make the database and administrator ready with command:

```powershell
flask deploy
flask create-admin
```

If you want to generate fake data for testing, you should use command `flask forge` after
running the command above.

Then you can run our Flog API. In most cases just use `flask run`, but if you use servers
like PythonAnywhere, Heroku, etc. Read its docs and go on.

## Credits

The code is written by @rice0208 and @z-t-y.

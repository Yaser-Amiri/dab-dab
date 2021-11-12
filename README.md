# Dab-Dab

This software simply creates a bridge between your browser and your OS (everything outside of your browser's sandbox).
Dab-Dab is a simple HTTP web server written in pure Python (without extra dependencies) that works on Linux.
You call it from your browser (preferably with [Surfingkeys](https://github.com/brookhong/Surfingkeys)) and
send your payload to it and it runs your scripts which you put in your `HOME` directory.

## How does it work?

It runs as a `systemd` service with `root` permissions.  
At startup, it checks the existence of a group named `dab-dab` on your system and creates it if there isn't one.  
Then it creates a directory named `dab-dab` for members of `dab-dab` group in this path: `~/.config/dab-dab`
and a python virtual environment inside it (`.venv`).

You can put your scripts inside your `dab-dab` dir (`~/.config/dab-dab`) this way:  
- Create a directory per script (like `~/.config/dab-dab/bookmarker`)
- Put your python script inside it and rename your python file to `main.py`
- If there is a dependency for your script, install it on `~/.config/dab-dab/.venv`

It will look like:
```
yaser:~/.config/dab-dab$ tree . -aL 2
.
├── bookmarker
│   └── main.py
└── .venv
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    └── pyvenv.cfg
```

Then All you have to do is call it. The request must be *POST* and URL is `/scripts/{your-script-dir-name}` for example:
`http://localhost:9669/scripts/bookmarker`.

When you call it, it tries to find the script and runs it with your user's permissions (demotes from `root` to the user who owns the client socket).  
It passes the payload to your script by an environment variable named `PARAMS`, you have to read it and decode it by a json parser and use it (or not).

Sample script:

```
import os, json

def run():
    payload = json.loads(os.environ.get("PARAMS", "{}"))
    print(payload)
    exit(0)

if __name__ == "__main__":
    run()
```
If you pass `interactive=true` as a query string, Dab-Dab will return the output of your script in response and you can print it in your browser.

## How can I install it?

Simple! Just clone this repo and run `sudo make install` (There is a `uninstall` too)  
This will start `dab-dab` service too, it creates a group named `dab-dab`, add your user too the group and restart the service.  
```
$ sudo usermod -aG dab-dab $(whoami)
$ sudo systemctl restart dab-dab.service
```

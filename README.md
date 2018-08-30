# CuBISM
## Curses Bash Install Scripts Manager

Graphical user interface in python with curses to manage installation, uninstallation and installations check from a command line.

![Status](https://img.shields.io/github/release/simchanu29/cubism/all.svg)
![Github license](https://img.shields.io/github/license/simchanu29/cubism.svg)

### Usage

To launch it :
```python
python cubism.py
```

### Configuration

To add new scripts :
 1. create a folder inside tasks and name it after the task you want the script to perform
 2. create 3 scripts inside this new folder : `do.sh`, `undo.sh`, `check.sh`
    - `do.sh` called at installations
    - `undo.sh` called at uninstallation
    - `check.sh` called when you want to know if the task has been properly done.

### Troubleshooting

If the script throw an error, the terminal window may be too small.

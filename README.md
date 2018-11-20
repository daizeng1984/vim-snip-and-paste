## Introduction
It's a breaking workflow when I need to take a picture of screen (to clipboard), save it into somewhere and link it before starting to write something in markdown. This plugin is to fix that for vim users. It can also do the same job for image file if you have its absolute path in clipboard!

## Screenshot
![snip-n-paste](./snip-n-paste.gif)
## Before PlugInstall
- Python working for neovim
- PyGObject and GTK:
    - For conda user on *nix, simply do `conda install -c pkgw-forge -c conda-forge gtk3 pygobject`
    - For non-conda user, go [here](https://pygobject.readthedocs.io/en/latest/getting_started.html#getting-started)

## Install
```
Plug 'daizeng1984/vim-snip-and-paste'
```
As all Python remote plugins, after you `PlugInstall`, you need to run `:UpdateRemotePlugins`.

## TODO
- [ ] Fix bug that when filename is empty
- [ ] Gifs
- [ ] Allow moving or renaming folder
- [ ] More configurables
- [ ] *Add runtime colorful markdown image preview in vim with PIL

## Introduction
It's a breaking workflow when I need to take a picture of screen (to clipboard), save it into somewhere and link it before starting to write something in markdown. This plugin is to fix that for vim users. It can also do the same job for image file if you have its absolute path in clipboard!

## Before PlugInstall
- Python 3
- For Mac OSX user, `brew install pngpaste`
- For Linux user, TODO

## Install
```
Plug 'daizeng1984/vim-snip-and-paste'
```
As all Python remote plugins, after you `PlugInstall`, you need to run `:UpdateRemotePlugins`.

## TODO
- [ ] Refactor the platform code
- [ ] Add linux clipboard logic (require xsel)
- [ ] Add windows clipboard logic (TBD)
- [ ] Allow moving or renaming folder
- [ ] More configurables
- [ ] *Add runtime colorful markdown image preview in vim with PIL

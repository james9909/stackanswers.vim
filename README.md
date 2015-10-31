stackanswers.vim
================

[Vim](http://www.vim.org/) plugin to get answers from [Stack Overflow](https://stackoverflow.com/). Inspired by [SO-Eclipse-Plugin](https://github.com/MarounMaroun/SO-Eclipse-Plugin).

`:StackAnswers`
---------------
Anything inputted after the command becomes the 'question' that will be answered from Stack Overflow, provided
that answers exist. Answers will be shown in a separate buffer.

![Gif](/screenshots/example.gif)

Installation
------------
StackAnswers should work with any modern plugin manager for Vim, such as [NeoBundle](https://github.com/Shougo/neobundle.vim), [Pathogen](https://github.com/tpope/vim-pathogen), [Vim-Plug](https://github.com/junegunn/vim-plug/), or [Vundle](https://github.com/VundleVim/Vundle.vim).

#### Requirements:
StackAnswers uses an external python module to parse data. You can install it via:
```
sudo apt-get install pip
sudo pip install requests
```
#### Options
It is possible to filter out the top answer, accepted answer, or not at all.
```Vim
let g:stack_filter = "top"  # The top answer is often the accepted one.
let g:stack_filter = "accepted"
```

Contributing
------------
If you have something you would like to contribute, feel free to open up a pull request with a short
summary of what exactly you are adding/fixing.

Thanks to all the people who [contributed](https://github.com/james9909/stackanswers.vim/graphs/contributors) to the project!.

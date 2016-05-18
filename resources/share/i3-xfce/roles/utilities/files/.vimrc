set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'
Plugin 'scrooloose/nerdtree'
Plugin 'Valloric/YouCompleteMe'
Plugin 'majutsushi/tagbar'
Plugin 'bling/vim-airline'
Plugin 'Lokaltog/powerline-fonts'
Plugin 'jistr/vim-nerdtree-tabs'
Plugin 'dschwen/switch-header-source'
Plugin 'tpope/vim-fugitive'
Plugin 'taglist.vim'

"Plugin 'FuzzyFinder'
"Plugin 'L9'
"Plugin 'c.vim'
"Plugin 'amiorin/vim-project'
"Plugin 'airblade/vim-rooter
"Plugin'
"Plugin 'xieyu/vim-assist'
"Plugin 'cmdalias.vim'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

" Common flags
syn  on
set  syntax =on
filetype  indent plugin on
set  nocp
set  nu
set  showmatch
set  tabstop =4
set  shiftwidth =4
set  softtabstop =4
set  expandtab 
set  incsearch
set  ignorecase
set  smartcase
set  wildmenu    "affiche le menu
set  wildmode =list:longest,list:full    "affiche toutes les possibilités
set  wildignore =*.o,*.r,*.so,*.sl,*.tar,*.tgz    "ignorer certains types de fichiers pour la complétion des includes
set  cursorline
set  columns=200
set  textwidth=200
set  mouse=a
" Airline stuff
set laststatus=2
set t_Co=256
let g:airline_powerline_fonts = 1
let g:airline_theme = 'badwolf'
set encoding=utf-8
let g:bufferline_echo = 0
set noshowmode
let g:airline_detect_whitespace=0
let g:airline#extensions#tabline#enabled = 0

" Split navigation
nmap <silent> <A-Up> :wincmd k<CR>
nmap <silent> <A-Down> :wincmd j<CR>
nmap <silent> <A-Left> :wincmd h<CR>
nmap <silent> <A-Right> :wincmd l<CR>
set splitbelow
set splitright

" NERDTree stuff
map <C-n> :NERDTreeTabsToggle<CR>
"autocmd vimenter * NERDTree

let g:ycm_server_keep_logfiles = 1
let g:ycm_server_log_level = 'debug'
let g:ycm_path_to_python_interpreter = '/usr/bin/python2'

let g:nerdtree_tabs_open_on_console_startup=1
let g:nerdtree_tabs_open_on_gui_startup=1
let g:nerdtree_tabs_open_on_new_tab=1

set statusline=%<%f\ [%{Tlist_Get_Tagname_By_Line()}]\ %h%m%r%=%-14.(%l,%c%V%)\ %P
colorscheme industry
set guifont=Monospace\ 9

map <A-S-Up> <c-w>+
map <A-S-Down> <c-w>-
map <A-S-Right> <c-w>>
map <A-S-Left> <c-w><

autocmd BufEnter * silent! if bufname('%') !~# 'NERD_tree_' | cd %:p:h | NERDTreeCWD | wincmd p | endif

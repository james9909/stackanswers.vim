if !exists('g:stack_width') "{{{
    let g:stack_width = 60
endif "}}}
if !exists('g:stack_height') "{{{
    let g:stack_height = 15
endif "}}}
if !exists('g:stack_left') "{{{
    let g:stack_left = 0
endif "}}}
if !exists('g:stack_bottom') "{{{
    let g:stack_bottom = 0
endif "}}}
if !exists('g:stack_right') "{{{
    let g:stack_right = 0
endif "}}}

" Slightly modified from Gundo
let s:plugin_path = escape(expand('<sfile>:p:h'), '\')
function! s:StackAnswersSettings() "{{{
    setlocal buftype=nofile
    setlocal bufhidden=hide
    setlocal noswapfile
    setlocal nobuflisted
    setlocal nomodifiable
    setlocal nolist
    setlocal nonumber
    setlocal norelativenumber
endfunction "}}}

function! s:StackAnswersOpen() "{{{
    let existing_answer_buffer = bufnr('__Answers__')

    if existing_answer_buffer == -1
        if g:stack_bottom
            exe 'botright new __Answers__'
        else
            if g:stack_right
                exe 'botright vnew __Answers__'
            elseif g:stack_left
                exe 'topleft vnew __Answers__'
            else " Default is top
                exe 'split __Answers__'
            endif
        endif
        call s:StackResizeBuffers(winnr())
    else
        let existing_preview_window = bufwinnr(existing_answer_buffer)

        if existing_preview_window != -1
            if winnr() != existing_preview_window
                exe existing_preview_window . 'wincmd w'
            endif
        else
            if g:stack_bottom
                exe 'botright split +buffer' . existing_answer_buffer
            else
                if g:stack_right
                    exe 'botright vsplit +buffer' . existing_answer_buffer
                elseif g:stack_left
                    exe 'topleft vsplit +buffer' . existing_answer_buffer
                else
                    exe 'split +buffer' . existing_answer_buffer
                endif
            endif
            call s:StackResizeBuffers(winnr())
        endif
    endif
endfunction "}}}

function! s:GoToWindowForBufferName(name) "{{{
    if bufwinnr(bufnr(a:name)) != -1
        exe bufwinnr(bufnr(a:name)) . "wincmd w"
        return 1
    else
        return 0
    endif
endfunction "}}}

function! s:StackResizeBuffers(backto) "{{{
    call s:GoToWindowForBufferName('__Answers__')
    exe "vertical resize " . g:stack_width
    exe "resize " . g:stack_height

    exe a:backto . "wincmd w"
endfunction "}}}

function! s:ClearBuffer(name) "{{{
    if bufwinnr(bufnr(a:name)) != -1
        exe bufwinnr(bufnr(a:name)) . "wincmd w"
        setlocal modifiable
        exe '%d'
        setlocal nomodifiable
        return 1
    else
        return 0
    endif
endfunction "}}}

function s:JobHandler(job_id, data, event) "{{{
    if a:event ==? 'stdout'
        let s:data = a:data
    elseif a:event ==? 'stderr'
        let s:data = 'Something went wrong!'
        let s:data = a:data
    endif

    " Open buffer and make it modifiable
    call s:StackAnswersOpen()
    setlocal modifiable

    " Append output
    call append(line('$'), s:data)

    " Go to top of file
    exe 'normal gg'

    " Remove first line if it is empty
    if (getline(1) ==# '')
        exe 'normal dd'
    endif
    setlocal nomodifiable
endfunction "}}}

if has('nvim') "{{{
    let s:callbacks = {
        \ 'on_stdout': function('s:JobHandler'),
        \ 'on_stderr': function('s:JobHandler'),
    \ }
endif "}}}

function! stackanswers#StackAnswers(...) "{{{
    if has('nvim')
        call jobstart(['python', s:plugin_path . '/stackanswers.py', '--cli', a:2], extend({'shell': 'shell'}, s:callbacks))
        call s:ClearBuffer("__Answers__")
    else
        call s:StackAnswersOpen()
        if has("python")
            exe 'pyfile ' . s:plugin_path . '/stackanswers.py'
        elseif has("python3")
            exe 'py3file ' . s:plugin_path . '/stackanswers.py'
        else
            return
        endif

        python stackAnswersVim("a:2")
        " Go to top of file
        exe 'normal gg'
    endif
endfunction "}}}

augroup StackAug
    autocmd!
    autocmd BufNewFile __Answers__ call s:StackAnswersSettings()
augroup END

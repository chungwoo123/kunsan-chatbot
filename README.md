파일을 읽는 도중 오류가 발생했습니다: C:\Users\CIE02_18\Desktop\대화데이터\KAKAO_1648_13.json
Traceback (most recent call last):

  File ~\anaconda3\Lib\site-packages\spyder_kernels\py3compat.py:356 in compat_exec
    exec(code, globals, locals)

  File c:\users\cie02_18\desktop\머신\chat.py:71
    y_sequences = [[tokenizer.word_index[start_token]] + seq + [tokenizer.word_index[end_token]] for seq in y_sequences]

  File c:\users\cie02_18\desktop\머신\chat.py:71 in <listcomp>
    y_sequences = [[tokenizer.word_index[start_token]] + seq + [tokenizer.word_index[end_token]] for seq in y_sequences]

KeyError: '<start>'

파일을 읽는 도중 오류가 발생했습니다: C:\Users\CIE02_18\Desktop\대화데이터\KAKAO_1648_13.json
4944/4944 ━━━━━━━━━━━━━━━━━━━━ 246s 49ms/step - accuracy: 0.8840 - loss: 1.2358 - val_accuracy: 0.8884 - val_loss: 0.8365
안녕하세요! 진로 상담 챗봇입니다. '종료'라고 입력하면 대화를 종료합니다.
사용자: 안녕
1/1 ━━━━━━━━━━━━━━━━━━━━ 0s 104ms/step
Traceback (most recent call last):

  File ~\anaconda3\Lib\site-packages\spyder_kernels\py3compat.py:356 in compat_exec
    exec(code, globals, locals)

  File c:\users\cie02_18\desktop\머신\chat.py:167
    chat_with_bot()

  File c:\users\cie02_18\desktop\머신\chat.py:160 in chat_with_bot
    response = decode_sequence(input_seq)

  File c:\users\cie02_18\desktop\머신\chat.py:116 in decode_sequence
    target_seq[0, 0] = tokenizer.word_index['<start>']

KeyError: '<start>'


2024-06-05 09:10:22.701255: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.

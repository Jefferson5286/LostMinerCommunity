from re import compile as re_compile


EMAIL_PATTERN = re_compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

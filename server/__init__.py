import argparse
import json
import MySQLdb
import string


class MyException(BaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def __str__(self):
        return self.msg


class ParserException(MyException):
    def __init__(self, msg):
        super().__init__(msg)


class IllegalArgsException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)


class ExecuteException(BaseException):
    def __init__(self, msg):
        super().__init__(msg)

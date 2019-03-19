import json
from sys import stdin, stdout
from server import ParserException, IllegalArgsException, ExecuteException
from server.server_core import MyParser, DatabaseController

try:
    print(json.dumps(DatabaseController.execute(MyParser.parse(stdin.readline()))))
except (ParserException, IllegalArgsException, ExecuteException) as e:
    print(json.dumps(str(e)))
finally:
    stdout.flush()

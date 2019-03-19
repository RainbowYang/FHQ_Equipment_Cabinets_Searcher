from sys import stdin, stdout
from server.server_core import run

print(run(stdin.readline()))
stdout.flush()

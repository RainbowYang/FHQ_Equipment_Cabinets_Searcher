import socket

'''
使用UDP方式与服务器进行连接
'''
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.sendto(b"INSERT TEST 123", ('118.25.49.70', 6666))
# print(s.recvfrom(1024))

'''
使用TCP方式与服务器进行连接
'''
s = socket.socket()  # socket 默认为TCP
# s.connect(('118.25.49.70', 6666))
s.connect(('127.0.0.1', 6666))
s.send(b"select_all")
print(s.recv(1024))
s.send(b'EXIT')
s.close()

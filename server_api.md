## 服务器说明 

### 服务器IP及端口
> for单片机: 118.25.49.70:6666
>
> for网页:   118.25.49.70:8080

### 协议

单片机可以使用TCP协议或UDP协议

网页使用websocket

### 返回值

单片机会接受到字符串

网页会接受到json格式的字符串（可能是数组，可能是带”的字符串）

### 命令

#### 查找

##### 通过Name，查找Location

```
SELECT [-n NAME]
```

for单片机：

正常情况下，会返回所对应的Location

如不存在，将会返回“0”

for网页：

正常情况下，会返回所对应的[Location，name]

如不存在，将会返回"ExecuteException("The Name(%s) is Not Found" % name)"

------

##### 通过Location，查找Name

```
SELECT [-l LOCATION]
```

for单片机：

正常情况下，会返回所对应的Name

如不存在，会返回“Empty”

for网页：

正常情况下，会返回所对应的[[Location，name]]

如不存在，会返回“ExecuteException("The Location(%s) is Empty" % location)”

##### 查找所有

```
SELECT_ALL
```

just for 网页：

格式如下

[[Location1，name1],[Location2，name2],...]

#### 删除

```
DELETE [-n NAME]
```

```
DELETE [-l LOCATION]
```
正常情况下会返回`"Successful Deleted"`
如不存在，会返回`"Not Found"`

#### 添加

```
INSERT [-n NAME] [-l LOCATION]
```
正常情况会返回`"Successful Inserted"`
如已存在，会返回`"Name is Existed"` 或者 `"Location is Existed"`

#### 更换

```
UPDATE [-n NAME] [-l LOCATION]
```

等同于执行`DELETE [-n NAME] [-l LOCATION]`和`INSERT [-n NAME] [-l LOCATION]`



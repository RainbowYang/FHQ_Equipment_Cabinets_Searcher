from server import *

"""
用于从接受外部的命令并进行解析，到进入数据库执行对应命令，最后返回结果
"""

methods = {"SELECT", "DELETE", "INSERT", "UPDATE"}


class MyParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument('operator', type=str.upper, choices=methods)
        self.add_argument('-n', '--name', type=str)
        self.add_argument('-l', '--location', type=int)
        self.add_argument('-all', type=bool, default=False)

    @staticmethod
    def parse(cmd: str) -> argparse.Namespace:
        """
        用于解析命令，并生成对应的NameSpace
        :param cmd: 需要解析的命令
        :return: 对应的NameSpace
        """
        return MyParser().parse_args(cmd.split())

    def error(self, message):
        raise ParserException(str(message))


ip, user, password, database, table = "118.25.49.70", "Rainbow", "Rainbow", "mydb", "mytb"


class DatabaseController(object):
    def __init__(self):
        self.ip, self.user, self.password, self.database, self.table = ip, user, password, database, table
        self.connection = MySQLdb.connect(self.ip, self.user, self.password, self.database)
        self.cursor = self.connection.cursor()
        self.methods = {"SELECT": self.select, "DELETE": self.delete, "INSERT": self.insert, "UPDATE": self.update}

    def connect(self):
        self.connection = MySQLdb.connect(self.ip, self.user, self.password, self.database)
        self.cursor = self.connection.cursor()

    @staticmethod
    def execute(args):
        return DatabaseController().methods.get(args.operator)(args.name, args.location)

    def select(self, name=None, location=None):
        self.check_name_and_location(name, location, 1)

        if location is not None:
            result = self.run_sql("SELECT location,name FROM %s WHERE location= '%s'" % (self.table, location))
            if len(result) == 0:
                raise ExecuteException("The Location(%s) is Empty" % location)
            return result
        elif name is not None:
            result = self.run_sql("SELECT location,name FROM %s WHERE name = '%s'" % (self.table, name))
            if len(result) == 0:
                raise ExecuteException("The Name(%s) is Not Found" % name)
            return result

    def delete(self, name=None, location=None):
        self.check_name_and_location(name, location, 1)

        if location is not None:
            try:
                item = self.select(location=location)
            except ExecuteException as e:
                raise e
            else:
                self.run_sql("DELETE FROM %s WHERE location = '%s'" % (self.table, location))
                return item
        elif name is not None:
            try:
                item = self.select(name=name)
            except ExecuteException as e:
                raise e
            else:
                self.run_sql("DELETE FROM %s WHERE name = '%s'" % (self.table, name))
                return item

    def insert(self, name=None, location=None):
        self.check_name_and_location(name, location, 2)

        try:
            self.select(name=name)
        except ExecuteException:
            try:
                self.select(location=location)
            except ExecuteException:
                self.run_sql("INSERT into %s values('%s', %s)" % (self.table, name, location))
                return self.select(name=name)
            else:
                raise ExecuteException("The Location(%s) is Not Empty" % location)
        else:
            raise ExecuteException("The Name(%s) is Existed" % name)

    def update(self, name=None, location=None):
        """
        update means move sth to sp
        :param name: the thing that existed
        :param location: the new place
        :return: result
        """
        self.check_name_and_location(name, location, 2)

        try:
            self.select(name=name)
        except ExecuteException as e:
            raise e
        else:
            try:
                self.select(location=location)
            except ExecuteException:
                self.delete(name=name)
                self.insert(name, location)
                return self.select(name=name)
            else:
                raise ExecuteException("The Location(%s) is Not Empty" % location)

    def run_sql(self, sql: str) -> str:
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            result = self.cursor.fetchall()
            return result
        except MySQLdb.OperationalError:
            self.connect()
            return self.run_sql(sql)

    def is_empty(self, location):
        try:
            self.select(location=location)
        except ExecuteException:
            return True
        else:
            return False

    def is_existed(self, name):
        try:
            self.select(name=name)
        except ExecuteException:
            return False
        else:
            return True

    @staticmethod
    def check_name(name):
        if name is None or len(name) == 0 or name[0] not in string.ascii_letters + '_':
            raise IllegalArgsException("The Name(%s) is not Allowed" % name)
        for c in name:
            if c not in string.ascii_letters + string.digits + '_':
                raise IllegalArgsException("The Name(%s) is not Allowed" % name)
        return True

    def check_name_and_location(self, name, location, needed: int):
        """
        check the name and the location is fitted to the method or not
        :param name: name
        :param location: location
        :param needed: the count of the var that the method need
        :return: return True if right or raise a Exception
        """
        if needed == 1:
            if name is None and location is not None or name is not None and location is None:
                if name is not None:
                    self.check_name(name)
                return True
            else:
                raise IllegalArgsException("name and location only need one")
        elif needed == 2:
            if name is not None and location is not None:
                self.check_name(name)
                return True
            else:
                raise IllegalArgsException("name and location are all needed")


def run(cmd: str) -> str:
    try:
        args = MyParser.parse(cmd)
        print(args)
        result = DatabaseController.execute(args)
        return json.dumps((args.operator, result))
    except (ParserException, IllegalArgsException, ExecuteException) as e:
        return json.dumps(str(e.__class__.__name__ + '(' + e.__str__()) + ')')


if __name__ == '__main__':
    print(run("insert -all yes"))
    print(run("update -n test -l 123"))
    # print(run("delete -l 1234"))
    print(run("select -n test"))

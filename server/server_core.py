import argparse
import string
import MySQLdb

from server import ParserException, IllegalArgsException, ExecuteException

methods = {"SELECT", "SELECT_ALL", "DELETE", "DELETE_ALL", "INSERT", "UPDATE", "RESTORE"}


class MyParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument('operator', type=str.upper, choices=methods)
        self.add_argument('-n', '--name', type=str)
        self.add_argument('-l', '--location', type=int)

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


ip, user, password, database, table = "127.0.0.1", "Rainbow", "Rainbow", "mydb", "mytb"


class DatabaseController(object):
    def __init__(self):
        self.ip, self.user, self.password, self.database, self.table = ip, user, password, database, table
        self.connection = MySQLdb.connect(self.ip, self.user, self.password, self.database)
        self.cursor = self.connection.cursor()
        self.methods = {"SELECT": self.select, "SELECT_ALL": self.select_all,
                        "DELETE": self.delete, "DELETE_ALL": self.delete_all,
                        "INSERT": self.insert, "UPDATE": self.update, "RESTORE": self.restore}

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

    def select_all(self, name=None, location=None):
        return self.run_sql("SELECT location,name FROM %s" % self.table)

    def delete(self, name=None, location=None) -> str:
        self.check_name_and_location(name, location, 1)

        if location is not None:
            try:
                item = self.select(location=location)
            except ExecuteException as e:
                raise e
            else:
                self.run_sql("DELETE FROM %s WHERE location = '%s'" % (self.table, location))
                return str(item[0]) + "is Successfully Deleted"
        elif name is not None:
            try:
                item = self.select(name=name)
            except ExecuteException as e:
                raise e
            else:
                self.run_sql("DELETE FROM %s WHERE name = '%s'" % (self.table, name))
                return str(item[0]) + "is Successfully Deleted"

    def delete_all(self, name=None, location=None) -> str:
        self.run_sql("DELETE FROM %s" % self.table)
        return "All items are Successfully Deleted"

    def insert(self, name=None, location=None) -> str:
        self.check_name_and_location(name, location, 2)

        try:
            self.select(name=name)
        except ExecuteException:
            try:
                self.select(location=location)
            except ExecuteException:
                self.run_sql("INSERT into %s values('%s', %s)" % (self.table, name, location))
                return str(self.select(name=name)[0]) + " is Successfully Inserted"
            else:
                raise ExecuteException("The Location(%s) is Not Empty" % location)
        else:
            raise ExecuteException("The Name(%s) is Existed" % name)

    def restore(self, name=None, location=None):
        self.delete_all()
        for item in [[1, 'Switch'], [2, 'Resistor'], [3, 'Capacitor'], [4, 'Inductor'],
                     [5, 'Battery'], [6, 'Diode'], [7, 'Triode']]:
            self.insert(item[1], item[0])
        return "All items are Deleted and Restored"

    def update(self, name=None, location=None):
        """
        update means move sth to sp
        :param name: the thing that existed
        :param location: the new place
        :return: result
        """
        self.check_name_and_location(name, location, 2)

        try:
            item = self.select(name=name)
        except ExecuteException as e:
            raise e
        else:
            try:
                self.select(location=location)
            except ExecuteException:
                self.delete(name=name)
                self.insert(name, location)
                return str(item[0]) + " is Successfully Updated to " + str(self.select(name=name)[0])
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

    @staticmethod
    def check_name(name):
        if name[0] not in string.ascii_letters + '_':
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
        if needed == 0:
            if name is None and location is None:
                return True
            else:
                raise IllegalArgsException("name and location are not needed")
        elif needed == 1:
            if name is None and location is not None \
                    or name is not None and location is None:
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

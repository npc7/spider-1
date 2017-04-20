# coding=utf-8
'''
Created on 2013-11-21
@author: jzx
'''
import pymysql
import time
import threading

def msg_print(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S ") + msg)


class MysqlDB:
    conn = None
    cursor = None

    def __init__(self, ip, db, user, pswd):
        self.conn = pymysql.connect(host=ip, user=user, passwd=pswd, db=db, charset='utf8')
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def write_record(self, sql):
        """
        write data, such as insert, delete, update
        :param sql: string sql
        :return: affected rows number
        return 0 when errors
        """
        self.lock.acquire()
        try:
            self.conn.ping(True)
            res = self.cursor.execute(sql)
            self.conn.commit()
            return res
        except Exception as ex:
            print(sql)
            print(ex)
            return 0
        finally:
            self.lock.release()

    def read_record(self, sql):
        """
        read data, such as select
        :param sql: string sql
        :return: iter rows and iter cells in each row
        return None when errors
        """
        self.lock.acquire()
        try:
            self.conn.ping(True)
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.conn.commit()
            return res
        except Exception as ex:
            print(sql)
            print(ex)
            return None
        finally:
            self.lock.release()

    def safe_string(self, string):
        """
        remove special char from string to avoid sql syntax error
        :param string: string
        :return: 
        """
        return string.replace("'", "\\'").replace("\\", "\\\\")

    def insert_dict(self, table, data_dict, mode="his"):
        """
        insert data with column names and different mode
        :param data_dict: data dict,
        {
        "update":[column,...], //columns for update when data exists
        "column1": "value1",  // column and value to insert
        ...
        }
        :param table: string table name
        :param mode: 'his' or 'syn', default 'his'
        his: history mode, insert ignore into ...
        syn: sync mode, replace into ...
        :return: return affected rows number
        """
        columns, values = [], []
        flag = mode == "his" and "update" in data_dict
        supdate = flag and ",".join(["%s='%s'" % (k, data_dict[k]) for k in data_dict.pop("update")]) or ""
        for k in data_dict:
            v = self.safe_string(data_dict[k])
            columns.append(k)
            values.append("'%s'" % v)
        sfield = ",".join(columns)
        svalue = ",".join(values)
        if len(sfield) == 0 or len(svalue) == 0:
            msg_print("result dict has no key-value ! save canceled !")
            return
        # 默认为his模式（需要历史数据）
        # 存在则更新下update_time,表示数据还在，不存在则插入
        strsql = "insert ignore into  %s (%s)values (%s)" % (table, sfield, svalue)
        strsql += supdate and " ON DUPLICATE KEY UPDATE %s" % supdate or ""
        # 如果为syn（实时同步模式）
        if mode == "syn":
            strsql = "REPLACE INTO %s (%s) values (%s)" % (table, sfield, svalue)
        ires = self.write_record(strsql)
        msg_print(ires > 0 and "insert success !" or ("insert failed ! ", data_dict))
        return ires

    def update_dict(self, data_dict, table):
        """
        update data with column names
        :param data_dict:
        {
        "where":[column,...], // columns in where
        "column1": "value1",  // column and value to update
        ...
        }
        :param table: string table name
        :return: return affected rows number
        """
        setstr = ""
        if "where" not in data_dict:
            msg_print("update need where condition!")
            return -1
        # data_dict.pop() 避免 where 条件 column 出现在 set 语句后面
        wherestr = ",".join(["%s='%s'" % (wh, data_dict.pop(wh)) for wh in data_dict.pop("where")])
        for key in data_dict:
            setstr += "%s='%s'," % (key, self.safe_string(data_dict[key]))
        strsql = "update %s set %s where %s" % (table, setstr, wherestr)
        ires = self.write_record(strsql)
        msg_print(ires > 0 and "update info success !" or "update failed !")
        return ires


if __name__ == "__main__":
    msg_print("unit test")

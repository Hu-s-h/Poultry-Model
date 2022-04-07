import pymysql.cursors
class ConnDB():
    def __init__(self,host='localhost',port=3306,user='root',passwd='root',db='ji2020'):
        self.host=host
        self.port=port
        self.user=user
        self.passwd=passwd
        self.db=db
        self.charset='utf8'
        self.isShow=0 #是否输出：0否 1是
    def conn(self):
        connect = pymysql.Connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
            charset=self.charset
        )
        if connect:
            if self.isShow:
                print("连接成功!")
            self.connect=connect
            # 获取游标
            cursor = connect.cursor()
            self.cursor=cursor
            # return cursor
        else:
            if self.isShow:
                print("连接失败!") 
    # 事务处理
    # sql_1 = "UPDATE trade SET saving = saving + 1000 WHERE account = '18012345678' "
    # sql_2 = "UPDATE trade SET expend = expend + 1000 WHERE account = '18012345678' "
    # sql_3 = "UPDATE trade SET income = income + 2000 WHERE account = '18012345678' "

    # try:
    #     cursor.execute(sql_1)  # 储蓄增加1000
    #     cursor.execute(sql_2)  # 支出增加1000
    #     cursor.execute(sql_3)  # 收入增加2000
    # except Exception as e:
    #     connect.rollback()  # 事务回滚
    #     print('事务处理失败', e)
    # else:
    #     connect.commit()  # 事务提交
    #     print('事务处理成功', cursor.rowcount)
    """ 
        功能：插入数据 
        输入：sql,data
            sql = "INSERT INTO trade (name, account, saving) VALUES ( '%s', '%s', %.2f )"
            data = ('雷军', '13512345678', 10000)
        输出：
    """  
    def insert(self,sql,data):
        if self.connect:
            self.cursor.execute(sql % data)
            self.connect.commit()
            if self.isShow:
                print('成功插入', self.cursor.rowcount, '条数据')
    """ 
        功能：删除数据
        输入：sql,data
            sql = "DELETE FROM trade WHERE account = '%s' LIMIT %d"
            data = ('13512345678', 1)
        输出：
    """  
    def delete(self,sql,data):
        if self.connect:
            self.cursor.execute(sql % data)
            self.connect.commit()
            if self.isShow:
                print('成功删除', self.cursor.rowcount, '条数据')
    """ 
        功能：修改数据
        输入：sql,data
            sql = "UPDATE trade SET saving = %.2f WHERE account = '%s' "
            data = (8888, '13512345678')
        输出：
    """  
    def update(self,sql,data):
        if self.connect:
            self.cursor.execute(sql % data)
            self.connect.commit()
            if self.isShow:
                print('成功修改', self.cursor.rowcount, '条数据')
    """ 
        功能：查询数据
        输入：sql,data
            sql = "SELECT name,saving FROM trade WHERE account = '%s' "
            data = ('13512345678',)
        输出：
    """  
    def select(self,sql,data):
        results=[]
        if self.connect:
            self.cursor.execute(sql % data)
            # num=0
            for row in self.cursor.fetchall():
                results.append(row)
            if self.isShow:
                print('共查找出', self.cursor.rowcount, '条数据')   
        return results 
                # num=num+1
                # print('订单%02d:'%num,end='')
                # for i in range(len(row)):
                #     if row[i]!=None:
                #         if i>2:
                #             data = row[i].split(',')
                #             jnum = int(data[0])
                #             jdage = int(data[1])
                #             javgw = float(data[2])
                #             jgrade = int(data[3])
                #             print(nameList[i]+"-数量%d,天龄%d,均重%0.2f,品种%d;"%(jnum,jdage,javgw,jgrade),end='')
                #         else:
                #             print(nameList[i]+str(row[i])+';',end='')
                # print(end='\n')
        # sql = "SELECT name,saving FROM trade WHERE account = '%s' "
        # data = ('13512345678',)
        # cursor.execute(sql % data)
        # for row in cursor.fetchall():
        #     print("Name:%s\tSaving:%.2f" % row)
        # print('共查找出', cursor.rowcount, '条数据')

    def close(self):
        # 关闭连接
        if self.connect:
            self.cursor.close()
            self.connect.close()

#创建数据库连接pymysql.Connect()参数说明
# host(str):      MySQL服务器地址
# port(int):      MySQL服务器端口号
# user(str):      用户名
# passwd(str):    密码
# db(str):        数据库名称
# charset(str):   连接编码，存在中文的时候，连接需要添加charset='utf8'，否则中文显示乱码。

# connection对象支持的方法
# cursor()        使用该连接创建并返回游标
# commit()        提交当前事务，不然无法保存新建或者修改的数据
# rollback()      回滚当前事务
# close()         关闭连接

# cursor对象支持的方法
# execute(op)     执行SQL，并返回受影响行数
# fetchone()      取得结果集的下一行
# fetchmany(size) 获取结果集的下几行
# fetchall()      获取结果集中的所有行
# rowcount()      返回数据条数或影响行数
# close()         关闭游标对象




# nameList=["客户编号","客户名","预计提货时间","大土2公","大土2项","大土2阉鸡","优土2公","优土2项","黄鸡2号公",
# "黄鸡2号项","勒竹土鸡项","麻黄鸡3号项","青脚麻鸡2号公","青脚麻鸡2号母","清远麻鸡2号公","清远麻鸡2号项",
# "清远麻鸡2号阉鸡","山坑凤公","山坑凤项","天露草鸡项","天露草阉鸡","天露麻鸡4号公","天露麻鸡4号母","天露黑鸡5号母",
# "温氏土鸡2号公","新矮脚黄鸡A公","新矮脚黄鸡A项","瑶鸡项","新兴黄鸡3号项","玉香鸡公","玉香鸡项","玉香鸡阉鸡","文昌鸡项",
# "文昌阉鸡","育成母鸡","天露麻阉生鸡","土1阉生鸡","竹丝鸡6号公","竹丝鸡6号母"]
# # 查询数据
# sql = "SELECT * FROM order_info"
# cursor.execute(sql)
# num=0
# for row in cursor.fetchall():
#     num=num+1
#     print('订单%02d:'%num,end='')
#     for i in range(len(row)):
#         if row[i]!=None:
#             if i>2:
#                 data = row[i].split(',')
#                 jnum = int(data[0])
#                 jdage = int(data[1])
#                 javgw = float(data[2])
#                 jgrade = int(data[3])
#                 print(nameList[i]+"-数量%d,天龄%d,均重%0.2f,品种%d;"%(jnum,jdage,javgw,jgrade),end='')
#             else:
#                 print(nameList[i]+str(row[i])+';',end='')
#     print(end='\n')






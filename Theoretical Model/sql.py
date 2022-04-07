import pymysql

# 数据库连接
def sql_conn(sql):
    conn = pymysql.connect(host="localhost", user="root", password="root", database="ws_chicken_db",charset="utf8")
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql)
    ret = cursor.fetchall()
    cursor.close()
    conn.commit()
    conn.close()
    return ret

sql1 = 'DELETE FROM order_info'
sql2 = 'DELETE FROM bre_info'
sql3 = 'DELETE FROM gap_info'
r1 = sql_conn(sql1)
r2 = sql_conn(sql2)
r3 = sql_conn(sql3)
####################################
bre_num = 10 #养户数
cus_num = 5 #客户数
pz = 5 #品种数
bre_tn = [2000,4000]
cus_tn = [1500,2000]
####################################
bre_id = ['' for i in range(bre_num)]
for i in range(bre_num):
    if(i >= 1000):
        bre_id[i] = 'b'+str(i)
    elif (i >= 100):
        bre_id[i] = 'b0' + str(i)
    elif (i >= 10):
        bre_id[i] = 'b00' + str(i)
    else:
        bre_id[i] = 'b000' + str(i)
cus_id = ['' for i in range(cus_num)]
for i in range(cus_num):
    if(i >= 1000):
        cus_id[i] = 'c'+str(i)
    elif (i >= 100):
        cus_id[i] = 'c0' + str(i)
    elif (i >= 10):
        cus_id[i] = 'c00' + str(i)
    else:
        cus_id[i] = 'c000' + str(i)

bre_name = ['' for i in range(bre_num)]
name_id = ['' for i in range(bre_num)]
for i in range(bre_num):

    if (i >= 100):
        name_id[i] = str(i)
    elif (i >= 10):
        name_id[i] = '0' + str(i)
    else:
        name_id[i] = '00' + str(i)
    bre_name[i] = '养户' + name_id[i]

cus_name = ['' for i in range(cus_num)]
for i in range(cus_num):
    if (i >= 100):
        cus_name[i] = '客户' + str(i)
    elif (i >= 10):
        cus_name[i] = '客户0' + str(i)
    else:
        cus_name[i] = '客户00' + str(i)

import random
for i in range(bre_num):
    # sql = "insert into bre_info values ('" + bre_id[i] + "','" + bre_name[i] + "','" + '' + "','" + str(1) + "','" + str(1) + "');"
    # sql = "insert into bre_info (bre_id, bre_name,bre_address,bre_longitude,bre_latitude)\
    #       values (bre_id[i], bre_name[i],'','1','1')"
    resultList = random.sample(range(1, pz+1), 4)
    sql = "insert into bre_info (bre_id, bre_name,bre_address,bre_longitude,bre_latitude,\
    spc_"+str(resultList[0])+",spc_"+str(resultList[1])+",spc_"+str(resultList[2])+",spc_"+str(resultList[3])+")\
                    values ('" + bre_id[i] + "','" + bre_name[i] + "',\'\' ,\'1\',\'1\','"\
          + str(random.randint(bre_tn[0], bre_tn[1])) + ",50,4.6,1','"\
          + str(random.randint(bre_tn[0], bre_tn[1])) + ",50,4.6,1','"\
          + str(random.randint(bre_tn[0], bre_tn[1])) + ",50,4.6,1','"\
          + str(random.randint(bre_tn[0], bre_tn[1])) + ",50,4.6,1')"
    sql1 = "insert into gap_info (bre_id, bre_name, gap_1, gap_2, gap_3, gap_4)\
        values ('" + bre_id[i] + "','" + bre_name[i] + "',"+str(random.randint(6, 100))+\
            ","+str(random.randint(6, 100))+","+str(random.randint(6, 100))+","+str(random.randint(6, 100))+")"
    ret = sql_conn(sql)
    ret1 = sql_conn(sql1)

for i in range(cus_num):
    resultList = random.sample(range(1, pz+1), 3)
    sql = "insert into order_info (cus_id, cus_name,cus_address,cus_longitude,cus_latitude,pre_time,\
    spc_"+str(resultList[0])+",spc_"+str(resultList[1])+",spc_"+str(resultList[2])+")\
                    values ('" + cus_id[i] + "','" + cus_name[i] + "',\'\' ,\'1\',\'1\','2020-08-12 0"+str(random.randint(3, 9))+":00:00','"\
          + str(random.randint(cus_tn[0], cus_tn[1])) + ",50,4.6,1','"\
          + str(random.randint(cus_tn[0], cus_tn[1])) + ",50,4.6,1','"\
          + str(random.randint(cus_tn[0], cus_tn[1])) + ",50,4.6,1')"
    ret = sql_conn(sql)

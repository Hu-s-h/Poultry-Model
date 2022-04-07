import pandas as pd
import xlrd
import json
import pymysql
import random as rd
import requests
from math import radians, cos, sin, asin, sqrt
class readKhOrder():
    def __init__(self):
        pass
    
    def read_kh_xsls(self,xlsx_path):
        data_xsls = xlrd.open_workbook(xlsx_path)  # 打开此地址下的exl文档
        sheet_name = data_xsls.sheets()[0]  # 进入第1张表
        sheet_name1 = data_xsls.sheet_by_index(0)
        count_nrows = sheet_name.nrows  # 获取总行数
        count_nocls = sheet_name.ncols  # 获得总列数
        line_value = sheet_name.row_values(0)
        data_value = []
        data_keys = []
        data_2 = []
        data = [0 in range(count_nrows)]

        for j in range(0, count_nocls):
            data_2.append(sheet_name.cell_value(0, j))  # 根据行数来取对应列的值

        for i in range(1,count_nrows):
            data_1 = []
            data_1 = sheet_name.row_values(i)
            data_value.append(data_1)
        return data_value, data_2 #data_2是列名 data_value是数据

    def read_yh_xlsx(self,xlsx_path):
        data_xsls = xlrd.open_workbook(xlsx_path)  # 打开此地址下的exl文档
        sheet_name = data_xsls.sheets()[0]  # 进入第5张表
        sheet_name1 = data_xsls.sheet_by_index(0)
        count_nrows = sheet_name.nrows  # 获取总行数
        count_nocls = sheet_name.ncols  # 获得总列数
        line_value = sheet_name.row_values(0)
        data_value = []
        data_keys = []
        data_2 = []
        data = [0 in range(count_nrows)]

        for j in range(0, count_nocls):
            data_2.append(sheet_name.cell_value(0, j))  # 根据行数来取对应列的值

        for i in range(1,count_nrows):
            data_1 = []
            data_1 = sheet_name.row_values(i)
            data_value.append(data_1)
        return data_value, data_2 #data_2是列名 data_value是数据

    #计算两点间距离-m
    def geodistance(self,lng1,lat1,lng2,lat2):
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
        dlon=lng2-lng1
        dlat=lat2-lat1
        a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        dis=2*asin(sqrt(a))*6371*1000
        return dis

    def geocodeG(self,address):
        par = {'address': address, 'key': 'd01252e25c8ed19ea83cbaf98320d0fd'}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        response = requests.get(base, par)
        answer = response.json()
        GPS = answer['geocodes'][0]['location'].split(",")
        return GPS[0], GPS[1]


if __name__ == '__main__':

    db = pymysql.connect('localhost', 'root', 'root', 'ws_chicken_db')
    cursor = db.cursor()

    # 读订单数据的部分
    path2 = '../data/3.27调度系统客户导入格式.xls'
    data_kh, List_col = readKhOrder().read_kh_xsls(path2)
    new_list_col = []
    new_data_kh = [[] for i in range(len(data_kh))]
    for i in range(len(List_col)): #取出品种名
        if i not in (0, 1, 2, 3, 4):
            new_list_col.append(List_col[i])
    print(new_list_col)
#插入bre_name
    spc_name_save= [ [] for i in range(len(new_list_col))]
    spc_num_add = 1
    for i in range(len(new_list_col)):
        spc_name_save[i].append(spc_num_add)
        spc_name_save[i].append(new_list_col[i])
        spc_num_add += 1
        sql_apc_name_add = 'update bre_name set yh_name = %s where spec_num = %s'
        mid_index_spc = (spc_name_save[i][1],spc_name_save[i][0])
        cursor.execute(sql_apc_name_add,mid_index_spc)
    


    spc_list = ['spc_'+str(i) for i in range(1,len(new_list_col)+1)]
    spc_dict = dict(zip(new_list_col,spc_list))
    chinese_pz = []
    for i in range(len(new_list_col)):
        chinese_pz.append(new_list_col[i])

    #插入订单数据
    #删除订单数据

    sql2 = 'DELETE FROM order_info'
    cursor.execute(sql2)
    db.commit()
    table = "order_info"

    # 列的字段
    str_head = ['cus_name','cus_id', 'pre_time','content','phone']
    for i in range(len(str_head)):
        new_list_col.insert(i, str_head[i])
    for i in range(len(spc_list)):
        new_list_col[i+5] = spc_list[i]
    keys = ', '.join(new_list_col)
    # 行字段
    for i in range(len(data_kh)):

        values = ','.join(['%s'] * len(data_kh[i]))
        sql = 'insert into {table}({keys}) values ({values})'.format(table=table, keys=keys, values=values)
        cursor.execute(sql, data_kh[i])
        db.commit()


    #删除养户数据
    db = pymysql.connect('localhost', 'root', 'root', 'ws_chicken_db')
    cursor = db.cursor()
    sql3 = 'DELETE FROM bre_info'
    cursor.execute(sql3)
    db.commit()
    table_yh = "bre_info"

    #读养户信息
    # path3 = '../data/养户肉鸡上市信息表1.6簕竹.xlsx'
    path3 = '../data/3.27养户供应导入数据.xlsx'
    data_yh, List_yh_col = readKhOrder().read_yh_xlsx(path3)

    str_yh_head = ['bre_id','bre_name','bre_fwz','bre_phone','bre_address','bre_longitude_latitude']
    list_col_yh = []#存储养户列头数据
    flag_yh_need_yn = True
    list_col_yh_data = [[] for i in range(len(data_yh))]
    for i in range(len(data_yh)):
        # print(i)
        for j in range(len(str_yh_head)):
            list_col_yh.append(str_yh_head[j])
        str_spc= data_yh[i][6]
        # print(chinese_pz)
        if str_spc not in chinese_pz:
            flag_yh_need_yn = False
            list_col_yh = []
            continue
        list_col_yh.append(str(spc_dict[str_spc]))
        for j in range(len(data_yh[i])):
            if j in range(6):
                if j ==0:
                    list_col_yh_data[i].append(int(data_yh[i][j]))
                else:
                    list_col_yh_data[i].append(data_yh[i][j])
            elif j == 6:
                str_index = str(int(data_yh[i][9])) + ',' + str(int(data_yh[i][10])) + ',' + str(int(data_yh[i][12]))
                list_col_yh_data[i].append(str_index)

        # 插入养户数据
        keys_yh = ', '.join(list_col_yh)
        values_yh = ','.join(['%s'] * len(list_col_yh_data[i]))
        sql = 'insert into {table}({keys}) values ({values})'.format(table=table_yh, keys=keys_yh, values=values_yh)
        yh_id_cz_yn = list_col_yh_data[i][0]
        sql_select = 'select bre_id from bre_info '
        cursor.execute(sql_select)
        # print(cursor.fetchall())
        flag = False
        if (str(yh_id_cz_yn),) in cursor.fetchall():

            # print(yh_id_cz_yn)
            sql_select_spc = 'select * from bre_info where bre_id = %s '
            cursor.execute(sql_select_spc,yh_id_cz_yn)
            clone_data_yh = cursor.fetchall()[0]
            for c in range(len(clone_data_yh)-6):
                if clone_data_yh[c+6] != None:
                    pz_no = list_col_yh[6].split('_')[1]
                    if int(pz_no) == int(c+1):
                        pz_num = int(clone_data_yh[c+6].split(',')[0]) + int(data_yh[i][9])
                        pz_num_date_pj = str(pz_num)+','+str(int(data_yh[i][10])) + ',' + str(int(data_yh[i][12]))
                        print(pz_num_date_pj)
                        sql_update_same = "update bre_info  set  spc_%s = %s where bre_id = %s"
                        # sql_insert_same = 'insert into bre_info (%s) values (%s)'
                        index_data_clone = (c+1,str(pz_num_date_pj),yh_id_cz_yn)
                        cursor.execute(sql_update_same,index_data_clone)
                        flag = True
                        break
                    else:

                        sql_insert_dif = "update bre_info  set  spc_%s = %s  where bre_id = %s"

                        # sql_insert_dif = "update bre_info  set  spc_1 = '5200'  where  bre_id = '5333'"

                        # sql_insert_same = 'insert into bre_info (%s) values (%s)'
                        # print(c+1)
                        pz_num_date_pj = str(int(data_yh[i][9])) + ',' + str(int(data_yh[i][10])) + ',' + str(int(data_yh[i][12]))
                        # print(pz_no, pz_num_date_pj, yh_id_cz_yn)
                        # index_data_clone = (int(pz_no), str(pz_num_date_pj), yh_id_cz_yn)
                        # cursor.execute(sql_insert_dif, index_data_clone)
                        # print("****")
                        # # print(cursor.execute(sql_insert_dif))
                        # print("****")
                        # # print(cursor.fetchall())
                        # print("zhiixngchenggong")
                        # sql_select_id = "select * from bre_info  where bre_id = 5333"
                        # print(cursor.execute(sql_select_id))
                        # print(cursor.fetchall())
                        flag = True
                        break
            # print(clone_data_yh)
        if flag is True:
            list_col_yh = []
            continue
        sql_select_id = "select * from bre_info  where bre_id = 5333"
        # print(cursor.execute(sql_select_id))
        # print(cursor.fetchall())
        cursor.execute(sql, list_col_yh_data[i])
        db.commit()

        #令list_col_yh为空，重新存储下一次的列名
        list_col_yh = []
    sql_select_id = "select * from bre_info  where bre_id = 5333"
    # print(cursor.execute(sql_select_id))
    # print(cursor.fetchall())

    #插入订单数据
    #删除订单数据
    db = pymysql.connect('localhost', 'root', 'root', 'ws_chicken_db')
    cursor = db.cursor()
    sql2 = 'DELETE FROM order_info'
    cursor.execute(sql2)
    db.commit()
    table = "order_info"
    new_list_col_kh_no2 =[]

    str_head = ['cus_name','cus_id', 'pre_time','content','phone']
    for i in range(len(str_head)):
        new_list_col_kh_no2.insert(i, str_head[i])

    for i in range(len(spc_list)):
        new_list_col_kh_no2.append(spc_list[i])
    keys_kh = ', '.join(new_list_col_kh_no2)

    # 行字段
    for i in range(len(data_kh)):
        # print(data_kh[i])
        values = ','.join(['%s'] * len(data_kh[i]))
        sql = 'insert into {table}({keys}) values ({values})'.format(table=table, keys=keys_kh, values=values)
        cursor.execute(sql, data_kh[i])
        db.commit()

#生成距离数据
    list_fwz = ['广东省云浮市新兴县簕竹镇榄根村', '广东省云浮市新兴县簕竹镇榄根村', '广东省云浮市新兴县簕竹镇榄根村马屯垌脊',
                '广东省云浮市新兴县车岗镇工业开发区', '广东省云浮市新兴县车岗镇工业开发区',
                '广东省云浮市新兴县稔村镇白土开发区', '广东省云浮市新兴县稔村镇白土开发区',
                '云浮市新兴县东成镇东瑶十里坩秋']
    # path3 = '../data/养户肉鸡上市信息表1.6簕竹新大地 .xlsx'
    # path3 = '../data/test山坑1.xlsx'
    data_yh, List_yh_col = readKhOrder().read_yh_xlsx(path3)
    gap_data = [[] for i in range(len(data_yh))]

    for i in range(len(data_yh)):
        for j in range(len(data_yh[i])):
            if j in (0,1,2,4):
                #可以加地址信息   [23457.0, '王建新1', '勒竹服务部', '新兴县稔村镇白土村']
                gap_data[i].append(data_yh[i][j])

    list_fwz_ins = [[] for i in range(8)]
    for i in range(8):
        index1, index2 = readKhOrder().geocodeG(list_fwz[i])
        list_fwz_ins[i].append(index1)
        list_fwz_ins[i].append(index2)
    # print(list_fwz_ins)

    for i in range(len(gap_data)):
        # print(gap_data[i][3])
        index3, index4 = readKhOrder().geocodeG(gap_data[i][3])
        for j in range(len(list_fwz_ins)):
            num_mid = readKhOrder().geodistance(float(index3), float(index4), float(list_fwz_ins[j][0]), float(list_fwz_ins[j][1]))
            gap_data[i].append(round(num_mid / 1000, 3))

    gap_list_col = ['bre_id','bre_name','bre_fwz','bre_address','gap_1','gap_2','gap_3','gap_4','gap_5','gap_6','gap_7','gap_8']
    db = pymysql.connect('localhost', 'root', 'root', 'ws_chicken_db')
    cursor = db.cursor()
    sql4 = 'DELETE FROM gap_info'
    cursor.execute(sql4)
    db.commit()
    table_gap = "gap_info"
    keys_gap = ', '.join(gap_list_col)
    # print(gap_list_col)
    # print(keys_gap)
    for i in range(len(gap_data)):
        for j in range(len(gap_data[i])):
            if j ==0 :
                gap_data[i][j] = int(gap_data[i][j])
    for i in range(len(gap_data)):
        values_gap = ','.join(['%s'] * len(gap_data[i]))
        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table_gap, keys=keys_gap, values=values_gap)
        # 将字段的value转化为元祖存入
        # print(data_yh[i])
        cursor.execute(sql, gap_data[i])
        db.commit()

#实现客户并单
    #后面用的这三行代码
    a = new_list_col_kh_no2[0]
    new_list_col_kh_no2[0] = new_list_col_kh_no2[1]
    new_list_col_kh_no2[1] = a

    sql_select_bd = 'select cus_id,content from order_info '
    cursor.execute(sql_select_bd)
    list_cus_id_bd = []
    list_cus_id_bd_split = []
    for  i in cursor.fetchall():
        list_cus_id_bd.append(list(i))
    print(list_cus_id_bd)
    index_count_dh = 0
    len_list_cus_id_bd = len(list_cus_id_bd)
    while index_count_dh < len(list_cus_id_bd) :
        if ',' not in list_cus_id_bd[index_count_dh][1]:
            # print(list_cus_id_bd[index_count_dh][1])
            del list_cus_id_bd[index_count_dh]
            continue
        index_count_dh += 1
    # print(list_cus_id_bd)
    for i in range(len(list_cus_id_bd)):
        list_cus_id_bd_split.append(list((list_cus_id_bd[i][0],list_cus_id_bd[i][1].split(',')[0])))
    print(list_cus_id_bd_split)
    #解决问题['070174', '分单，装早鸡']



    flag_bd = ['']
    for i in range(len(list_cus_id_bd_split)):
        index_list_same_bd = []
        index_list_same_bd.append(list_cus_id_bd_split[i])
        for j in range(i+1,len(list_cus_id_bd_split)):
            if list_cus_id_bd_split[i][1] == list_cus_id_bd_split[j][1] and list_cus_id_bd_split[i][1] not in flag_bd:
                index_list_same_bd.append(list_cus_id_bd_split[j])
        if len(index_list_same_bd)>=2:
            list_sql_select_result = []
            for z in range(len(index_list_same_bd)):
                id = index_list_same_bd[z][0]
                sql_mid_same_select = "select * from order_info where cus_id = %s"%(id)
                cursor.execute(sql_mid_same_select)
                db.commit()
                for d in cursor.fetchall():
                    list_sql_select_result.append(list(d))
                sql_mid_delect_same = "delete from order_info where cus_id = %s"%(id)
                cursor.execute(sql_mid_delect_same)
                db.commit()

            print(list_sql_select_result) #输出需合并的客户
            index_kh_hd = []
            a_fuhao = ['',None]
            for f in range(len(list_sql_select_result)):
                for z in range(len(list_sql_select_result[0])):
                    if z == 0:
                        if len(index_kh_hd) == 0:
                            index_kh_hd.append(list_sql_select_result[0][0])
                    if z == 1:
                        if len(index_kh_hd) <= 1:
                            index_kh_hd.append(list_sql_select_result[0][1][:5])
                        else:
                            index_kh_hd[1] += '_' + list_sql_select_result[f][z][:5]
                    if z == 2:
                        if len(index_kh_hd) <= 2:
                            index_kh_hd.append(list_sql_select_result[0][2])
                    if z == 3:
                        if len(index_kh_hd) <= 3:
                            index_kh_hd.append(',')
                    if z == 4:
                        if len(index_kh_hd) <= 4:
                            index_kh_hd.append(list_sql_select_result[0][4])
                        else:
                            index_kh_hd[4] += '_' + list_sql_select_result[f][z]
                    if z > 4:
                        if len(index_kh_hd) <= z:
                            index_kh_hd.append(list_sql_select_result[f][z])
                        else:
                            if (list_sql_select_result[f][z] not in a_fuhao) and (index_kh_hd[z] not in a_fuhao):
                                # print("aaaaaaaaa")
                                # print(index_kh_hd[z])
                                # print("aaaa")
                                # print(list_sql_select_result[f][z])
                                # print("aaaaa")
                                index_kh_hd[z] = str(int(index_kh_hd[z].split(',')[0])+int(list_sql_select_result[f][z].split(',')[0]))
                                index_kh_hd[z] +=',,1'
                            elif index_kh_hd[z] in a_fuhao:
                                index_kh_hd[z]=list_sql_select_result[f][z]
                    # print(index_kh_hd[z], list_sql_select_result[1][14])


            len_kh_hd = len(new_list_col_kh_no2)
            print(index_kh_hd[:len_kh_hd])
            values = ','.join(['%s'] * len_kh_hd)
            print(new_list_col_kh_no2)

            print(new_list_col_kh_no2)
            keys_kh_1 = ', '.join(new_list_col_kh_no2)
            # print(keys_kh_1)
            sql = 'insert into {table}({keys}) values ({values})'.format(table=table, keys=keys_kh_1, values=values)
            cursor.execute(sql, index_kh_hd[:len_kh_hd])
            db.commit()

        flag_bd.append(list_cus_id_bd_split[i][1])
        print(index_list_same_bd)

from logging import error
import sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

import pymysql
import random
import math
import tkinter
import tkinter.messagebox
from tkinter import Tk, Label, Frame, StringVar, Entry, Button, filedialog
from tkinter.ttk import Treeview, Combobox

from wenshi210701.DealData import DealData
from wenshi210701.ConnDB import ConnDB
from wenshi210701.AssignYh_model2 import AssYh
from wenshi210701.AssignKh_model1 import AssKh
from wenshi210701.fwzPmIndOfName import fwzPmIndOfName
from wenshi210701.SaveKyResult import SaveKyResult
from wenshi210701.PulpSolve import PulpSolve
from wenshi210701.DetailKy_model4 import DetailKy_ky
from wenshi210701.MatchKy_model3 import MatchKy
from wenshi210701.read_kh_order import readKhOrder
from wenshi210701.finalDealKh import finalDealKh
# 显示界面---------------------------------------------------------------------------------------------------------------------
# 设置窗口为居中
# 1.获得屏幕的宽高
class UIkyMain():
    def __init__(self):
        self.args_excel = []
        self.isflag = 0 #是否插入虚拟养户
        self.bre_num = -1
        self.prepz = 0
        self.prepj = 0
        # self.deal_data() #执行数据处理
        self.conndb = ConnDB(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
        self.conndb.conn()
        kh_tn,r_kh = self.conndb.select("SELECT * FROM order_info")
        self.conndb.close()
        kpind = kh_tn.index('spc_1')
        self.maxpz_num = len(kh_tn) - kpind
        self.mainpage()
    def mainpage(self):
        MainTk = Tk()
        MainTk.title("调度排班系统")
        MainTk.maxsize(1200, 500)  # 设置窗口最大尺寸
        # 设置页面居中
        self.center_window(MainTk, 920, 400)
        Label(MainTk,text="禽类配送站点智能排班系统", font=("华文行楷", 36), fg="#ff590b").grid(row=0, column=0, padx=10,pady=40)
        buttonFrame = Frame(MainTk)
        buttonFrame.grid(row=1, column=0, pady=20)
        Button(buttonFrame, text="调整服务站参数", font=("楷体", 16), width=15,command=lambda:self.createfwzpmbgPage(MainTk)).grid(row=0, column=0, pady=10, padx=10)
        Button(buttonFrame, text="调整运行参数",  font=("楷体", 16),command=lambda:self.createCSpage(MainTk)).grid(row=0, column=1, pady=10, padx=10)
        Button(buttonFrame, text="导入客户养户数据", font=("楷体", 16), command=lambda:self.createfilepage(MainTk)).grid(row=0, column=2, pady=10, padx=10)
        Button(buttonFrame, text="检测数据情况", font=("楷体", 16), command=lambda:self.pre_cvy()).grid(row=0, column=3, pady=10, padx=10)
        Button(buttonFrame, text="运行模型程序",  font=("楷体", 16), command=lambda:self.runMain()).grid(row=0, column=4, pady=10, padx=10)
        buttonFrame1 = Frame(MainTk)
        buttonFrame1.grid(row=2, column=0, pady=20)
        Button(buttonFrame1, text="导出排班结果",  font=("楷体", 16), command=lambda:self.getSuc()).grid(row=0, column=0, pady=10, padx=10)
        Button(buttonFrame1, text="查看客户信息",  font=("楷体", 16)).grid(row=0, column=1, pady=10, padx=10)
        Button(buttonFrame1, text="查看养户信息",  font=("楷体", 16)).grid(row=0, column=2, pady=10, padx=10)
        Button(buttonFrame1, text="查看特殊情况",  font=("楷体", 16)).grid(row=0, column=3, pady=10, padx=10)
        Button(buttonFrame1, text="关闭信息界面",  font=("楷体", 16), command=lambda:self.mainQuit(MainTk)).grid(row=0, column=4, pady=10, padx=10)
        # lambda: self.rollback(filewindow)
        MainTk.mainloop()
    def get_screen_size(self, window):
        return window.winfo_screenwidth(), window.winfo_screenheight()
    def get_window_size(self, window):
        return window.winfo_reqwidth(), window.winfo_reqheight()
    # 2.用屏幕宽高和geometry属性设置居中
    def center_window(self,root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)
    #界面关闭------------------------------------------------------------------------------------------------------------------------------
    def rollback(self,window,tk_name):
        window.destroy()
        tk_name.deiconify()
    def mainQuit(self,tk_name):
        tk_name.destroy()
    def getSuc(self):
        tkinter.messagebox.showinfo("提示","排班结果导出成功")
    #打开excel文件-客户信息表
    def openExcel_kh(self):
        if(os.path.exists(self.khtable)):
            tkinter.messagebox.showinfo("提示","客户信息表打开成功")
            os.startfile(self.khtable)
        else:
            tkinter.messagebox.showinfo('提示','客户信息表文件不存在')
    #打开excel文件-养户调度表
    def openExcel_yh(self):
        if(os.path.exists(self.yhtable)):
            tkinter.messagebox.showinfo("提示","养户调度表打开成功")
            os.startfile(self.yhtable)
        else:
            tkinter.messagebox.showinfo('提示','养户调度表文件不存在')
    #导入客户养户界面-----------------------------------------------------------------------------------------------------------------------
    def createfilepage(self,tk_name):
        tk_name.withdraw()
        # 输入文件窗口
        filewindow = Tk()
        filewindow.title("查找文件并读取")
        filewindow.maxsize(1000, 500)
        # 设置居中
        self.center_window(filewindow, 600, 200)
        khfilePath = StringVar(filewindow)
        yhfilePath = StringVar(filewindow)
        def yhfileopen():
            fileName = filedialog.askopenfilename()
            yhfilePath.set(fileName)

        def khfileopen():
            fileName = filedialog.askopenfilename()
            khfilePath.set(fileName)
        # 读取excel文件
        def insert():
            if (khfilePath.get() != '' and yhfilePath.get() != ''):
                # try:
                    if (khfilePath.get() != '' and yhfilePath.get() != ''):
                        print(khfilePath.get())
                        print(yhfilePath.get())
                        db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
                        cursor = db.cursor()
                    # 读订单数据的部分
                    # 读订单数据的部分
                    path2 = khfilePath.get()
                    data_kh, List_col = readKhOrder().read_kh_xsls(path2)
                    new_list_col = []
                    new_data_kh = [[] for i in range(len(data_kh))]
                    for i in range(len(List_col)): #取出品种名
                        if i not in (0, 1, 2, 3, 4):
                            new_list_col.append(List_col[i])
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
                    for i in range(len(new_list_col)+1,self.maxpz_num+1):
                        sql_apc_name_add = 'update bre_name set yh_name = %s where spec_num = %s'
                        mid_index_spc = ('spc_{}'.format(i), i)
                        # print(i)
                        cursor.execute(sql_apc_name_add, mid_index_spc)
                        db.commit()


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

                    new_list_col_kh_no2 = []
                    str_head = ['cus_name', 'cus_id', 'pre_time', 'content', 'phone']
                    for i in range(len(str_head)):
                        new_list_col_kh_no2.insert(i, str_head[i])

                    for i in range(len(spc_list)):
                        new_list_col_kh_no2.append(spc_list[i])
                    keys_kh = ', '.join(new_list_col_kh_no2)


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
                    #处理时间优先级问题
                        if (data_kh[i][2]== ''):
                            data_kh[i][2] = -1
                        elif '~' not in data_kh[i][2]:
                            if ':' not in data_kh[i][2]:
                                data_kh[i][2] = int(data_kh[i][2])*60
                            else:
                                stlist = data_kh[i][2].split(':')
                                data_kh[i][2] = int(stlist[0])*60+int(stlist[1])
                        else:
                            st = data_kh[i][2].split('~')
                            if len(st)==1:
                                stlist = st[0].split(':')
                                data_kh[i][2] = int(stlist[0])*60+int(stlist[1])
                            elif st[1]=='':
                                stlist = st[0].split(':')
                                data_kh[i][2] = int(stlist[0])*60+int(stlist[1])
                            else:
                                stlist0 = st[0].split(':')
                                stlist1 = st[1].split(':')
                                data_kh[i][2] = math.ceil((int(stlist0[0])*60+int(stlist0[1])+int(stlist1[0])*60+int(stlist1[1]))/2)

                            
                        # if (int(data_kh[i][2].split('~')[0].split(':')[0]) > 5):
                        #     data_kh[i][2] = -1
                        # else:
                        #     data_kh[i][2] = 1
                        cursor.execute(sql, data_kh[i])
                        db.commit()


                    #删除养户数据
                    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
                    cursor = db.cursor()
                    sql3 = 'DELETE FROM bre_info'
                    cursor.execute(sql3)
                    db.commit()
                    table_yh = "bre_info"

                    #读养户信息
                    # path3 = '../data/养户肉鸡上市信息表1.6簕竹.xlsx'
                    path3 = yhfilePath.get()
                    data_yh, List_yh_col = readKhOrder().read_yh_xlsx(path3)

                    str_yh_head = ['bre_id','bre_name','bre_fwz','bre_phone','bre_address','bre_longitude_latitude']
                    list_col_yh = []#存储养户列头数据
                    flag_yh_need_yn = True
                    list_col_yh_data = [[] for i in range(len(data_yh))]
                    for i in range(len(data_yh)):
                        for j in range(len(str_yh_head)):
                            list_col_yh.append(str_yh_head[j])
                        str_spc= data_yh[i][6]
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
                        flag = False
                        if (str(yh_id_cz_yn),) in cursor.fetchall():

                            sql_select_spc = 'select * from bre_info where bre_id = %s '
                            cursor.execute(sql_select_spc,yh_id_cz_yn)
                            clone_data_yh = cursor.fetchall()[0]
                            for c in range(len(clone_data_yh)-6):
                                if clone_data_yh[c+6] != None:
                                    pz_no = list_col_yh[6].split('_')[1]
                                    if int(pz_no) == int(c+1):
                                        pz_num = int(clone_data_yh[c+6].split(',')[0]) + int(data_yh[i][9])
                                        pz_num_date_pj = str(pz_num)+','+str(int(data_yh[i][10])) + ',' + str(int(data_yh[i][12]))
                                        sql_update_same = "update bre_info  set  spc_%s = %s where bre_id = %s"
                                        index_data_clone = (c+1,str(pz_num_date_pj),yh_id_cz_yn)
                                        cursor.execute(sql_update_same,index_data_clone)
                                        db.commit()
                                        flag = True
                                        break
                                    else:
                                        sql_insert_dif = "update bre_info  set  spc_%s = %s  where bre_id = %s"
                                        pz_num_date_pj = str(int(data_yh[i][9])) + ',' + str(int(data_yh[i][10])) + ',' + str(int(data_yh[i][12]))
                                        index_data_clone = (int(pz_no), pz_num_date_pj, yh_id_cz_yn)
                                        cursor.execute(sql_insert_dif, index_data_clone)
                                        db.commit()
                                        flag = True
                                        break
                            # print(clone_data_yh)
                        if flag is True:
                            list_col_yh = []
                            continue

                        cursor.execute(sql, list_col_yh_data[i])
                        db.commit()

                        #令list_col_yh为空，重新存储下一次的列名
                        list_col_yh = []
                    #生成距离数据
                    list_fwz = ['广东省云浮市新兴县簕竹镇榄根村', '广东省云浮市新兴县簕竹镇榄根村', '广东省云浮市新兴县簕竹镇榄根村马屯垌脊',
                                '广东省云浮市新兴县车岗镇工业开发区', '广东省云浮市新兴县车岗镇工业开发区',
                                '广东省云浮市新兴县稔村镇白土开发区', '广东省云浮市新兴县稔村镇白土开发区',
                                '云浮市新兴县东成镇东瑶十里坩秋']
                    # path3 = '../data/养户肉鸡上市信息表1.6簕竹新大地 .xlsx'
                    # path3 = '../data/养户供应系统导入数据2.4.xlsx'
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

                    for i in range(len(gap_data)):
                        index3, index4 = readKhOrder().geocodeG(gap_data[i][3])
                        for j in range(len(list_fwz_ins)):
                            num_mid = readKhOrder().geodistance(float(index3), float(index4), float(list_fwz_ins[j][0]), float(list_fwz_ins[j][1]))
                            gap_data[i].append(round(num_mid / 1000, 3))

                    gap_list_col = ['bre_id','bre_name','bre_fwz','bre_address','gap_1','gap_2','gap_3','gap_4','gap_5','gap_6','gap_7','gap_8']
                    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
                    cursor = db.cursor()
                    sql4 = 'DELETE FROM gap_info'
                    cursor.execute(sql4)
                    db.commit()
                    table_gap = "gap_info"
                    keys_gap = ', '.join(gap_list_col)
                    for i in range(len(gap_data)):
                        for j in range(len(gap_data[i])):
                            if j ==0 :
                                gap_data[i][j] = int(gap_data[i][j])
                    for i in range(len(gap_data)):
                        values_gap = ','.join(['%s'] * len(gap_data[i]))
                        sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table_gap, keys=keys_gap, values=values_gap)
                        # 将字段的value转化为元祖存入
                        cursor.execute(sql, gap_data[i])
                        db.commit()

                    # 将字段的value转化为元祖存入

                    # 实现客户并单
                    # 后面用的这三行代码
                    a = new_list_col_kh_no2[0]
                    new_list_col_kh_no2[0] = new_list_col_kh_no2[1]
                    new_list_col_kh_no2[1] = a

                    sql_select_bd = 'select cus_id,content from order_info '
                    cursor.execute(sql_select_bd)
                    list_cus_id_bd = []
                    list_cus_id_bd_split = []
                    for i in cursor.fetchall():
                        list_cus_id_bd.append(list(i))
                    index_count_dh = 0
                    len_list_cus_id_bd = len(list_cus_id_bd)
                    while index_count_dh < len(list_cus_id_bd):
                        if '#' not in list_cus_id_bd[index_count_dh][1]:
                            del list_cus_id_bd[index_count_dh]
                            continue
                        index_count_dh += 1
                    for i in range(len(list_cus_id_bd)):
                        list_cus_id_bd_split.append(list((list_cus_id_bd[i][0], list_cus_id_bd[i][1].split('#')[0])))

                    flag_bd = ['']
                    for i in range(len(list_cus_id_bd_split)):
                        index_list_same_bd = []
                        index_list_same_bd.append(list_cus_id_bd_split[i])
                        for j in range(i + 1, len(list_cus_id_bd_split)):
                            if list_cus_id_bd_split[i][1] == list_cus_id_bd_split[j][1] and list_cus_id_bd_split[i][
                                1] not in flag_bd:
                                index_list_same_bd.append(list_cus_id_bd_split[j])
                        if len(index_list_same_bd) >= 2:
                            list_sql_select_result = []
                            for z in range(len(index_list_same_bd)):
                                id = index_list_same_bd[z][0]
                                sql_mid_same_select = "select * from order_info where cus_id = %s" % (id)
                                cursor.execute(sql_mid_same_select)
                                db.commit()
                                for d in cursor.fetchall():
                                    list_sql_select_result.append(list(d))
                                sql_mid_delect_same = "delete from order_info where cus_id = %s" % (id)
                                cursor.execute(sql_mid_delect_same)
                                db.commit()

                            index_kh_hd = []
                            a_fuhao = ['', None]
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
                                            if (list_sql_select_result[f][z] not in a_fuhao) and (
                                                    index_kh_hd[z] not in a_fuhao):
                                                
                                                index_kh_hd[z] = str(int(index_kh_hd[z].split(',')[0]) + int(
                                                    list_sql_select_result[f][z].split(',')[0]))
                                                index_kh_hd[z] += ',,,1'
                                            elif index_kh_hd[z] in a_fuhao:
                                                index_kh_hd[z] = list_sql_select_result[f][z]
                                    
                            len_kh_hd = len(new_list_col_kh_no2)                            
                            values = ','.join(['%s'] * len_kh_hd)
                            keys_kh_1 = ', '.join(new_list_col_kh_no2)
                            sql = 'insert into {table}({keys}) values ({values})'.format(table=table, keys=keys_kh_1,
                                                                                        values=values)
                            cursor.execute(sql, index_kh_hd[:len_kh_hd])
                            db.commit()
                        flag_bd.append(list_cus_id_bd_split[i][1])

                    #创建表cus_pm_no
                    sql_create_cus_pm_no = 'select cus_id,cus_name,content from order_info'
                    sql_delect_order_supply_info = 'delete from order_supply_info'
                    cursor.execute(sql_create_cus_pm_no)
                    db.commit()
                    cursor.execute(sql_delect_order_supply_info)
                    db.commit()
                    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
                    cursor = db.cursor()
                    cursor.execute(sql_create_cus_pm_no)
                    db.commit()
                    save_get_order_supply_info = []
                    for i in cursor.fetchall():
                        save_get_order_supply_info.append(list(i))
                    #对每一个客户进行单独处理
                    table_order_supply = 'order_supply_info'
                    for i in range(len(save_get_order_supply_info)):
                        if '/' in  save_get_order_supply_info[i][2]:
                            save_get_order_supply_info[i][2] = save_get_order_supply_info[i][2].split('/')[1]
                        else:
                            save_get_order_supply_info[i][2] = ''
                        list_col_order_pm = ['cus_id','cus_name','appoint_pm']

                        order_supply_kh = ', '.join(list_col_order_pm)
                        values_order_supply = ','.join(['%s'] * len(save_get_order_supply_info[i]))
                        sql_order_supply = 'insert into {table}({keys}) values ({values})'.format(table=table_order_supply, keys=order_supply_kh,
                                                                                    values=values_order_supply)
                        cursor.execute(sql_order_supply,save_get_order_supply_info[i])
                        db.commit()
                    db.close()
                    print('数据导入完成')
                    self.isflag = 1 #是否插入虚拟养户
                # except:
                #     tkinter.messagebox.showerror('错误', '文件导入失败')
                # else:
                #     tkinter.messagebox.showinfo('提示', '文件导入成功')
            else:
                tkinter.messagebox.showerror('错误', '未导入文件')

        # 提示的文本框
        Label(filewindow, text='请导入客户养户信息的文件', width=74, height=2,
            bg='#666666', fg="#F8F8FF", font=("黑体", 12)).grid(row=0, column=0)
        orderWindowFrame = Frame(filewindow)
        orderWindowFrame.grid(row=1, column=0, pady=15)
        Label(orderWindowFrame, text="客户订单文件: ", font=("黑体", 12), fg="#000011").grid(row=0, column=0, pady=5, padx=5)
        Entry(orderWindowFrame, textvariable=khfilePath, width=35).grid(row=0, column=1, pady=5, padx=5)
        Button(orderWindowFrame, text="查找", command=khfileopen, width=10).grid(row=0, column=2, padx=10, pady=2)

        Label(orderWindowFrame, text="养户订单文件: ", font=("黑体", 12), fg="#000011").grid(row=1, column=0, pady=5, padx=5)
        Entry(orderWindowFrame, textvariable=yhfilePath, width=35).grid(row=1, column=1, pady=5, padx=5)
        Button(orderWindowFrame, text="查找", command=yhfileopen, width=10).grid(row=1, column=2, padx=10, pady=5)

        buttonFileFrame = Frame(filewindow)
        buttonFileFrame.grid(row=3, column=0, pady=5)

        Button(buttonFileFrame, text="确定并读取", width=15, command=insert).grid(row=0, column=0, padx=10, pady=5)
        Button(buttonFileFrame, text="返回上一级", width=15, command=lambda: self.rollback(filewindow,tk_name)).grid(row=0, column=1, padx=10,
                                                                                                pady=5)
        # 显示界面
        # filewindow.wm_attributes('-topmost', 1)
        filewindow.mainloop()

    #参数调整界面----------------------------------------------------------------------------------------------------------------------
    def createCSpage(self, tk_name):
        #连接数据库
        self.conndb.conn()
        other_des,other_data = self.conndb.select("SELECT * FROM other_info where oid = 1")
        self.conndb.close()
        tk_name.withdraw()
        modifyTk = Tk()
        modifyTk.title("服务站参数调整")
        modifyTk.maxsize(1200, 500)  # 设置窗口最大尺寸
        # 设置页面居中
        self.center_window(modifyTk, 725, 410)

        Label(modifyTk, text='调整参数界面', width=80, height=2,
              bg='#666666', fg="#F8F8FF", font=("黑体", 13)).grid(row=0, column=0)
        # 中间组件
        Frame1 = Frame(modifyTk)
        Frame1.grid(row=1, column=0, pady=15)
        # 左右两个组件框架
        leftFrame = Frame(Frame1)
        leftFrame.grid(row=0, column=0, pady=15, padx=30)
        # 开始时间设置
        startTime = StringVar(modifyTk)
        startTime.set(other_data[0][1])
        Label(leftFrame, text="开始时间（分钟）: ", font=("黑体", 13), fg="#000011").grid(row=0, column=0)
        Entry(leftFrame, textvariable=startTime, width=8, font=("黑体", 12)).grid(row=0, column=1, pady=12)
        # 每个时间单元每个养户最多送鸡
        yhChickenNum = StringVar(modifyTk)
        yhChickenNum.set(other_data[0][2])
        Label(leftFrame, text="时间单元允许养户最多车趟数: ", font=("黑体", 13), fg="#000011").grid(row=1, column=0)
        Entry(leftFrame, textvariable=yhChickenNum, width=8, font=("黑体", 12)).grid(row=1, column=1, pady=12)

        # 时间宽松度
        timeNum = StringVar(modifyTk)
        timeNum.set(other_data[0][3])
        Label(leftFrame, text="时间宽松度: ", font=("黑体", 13), fg="#000011").grid(row=2, column=0)
        Entry(leftFrame, textvariable=timeNum, width=8, font=("黑体", 12)).grid(row=2, column=1, pady=12)
        # 车辆满载装鸡数
        carFullNum = StringVar(modifyTk)
        carFullNum.set(other_data[0][4])
        Label(leftFrame, text="车辆满载装鸡数: ", font=("黑体", 13), fg="#000011").grid(row=3, column=0)
        Entry(leftFrame, textvariable=carFullNum, width=8, font=("黑体", 12)).grid(row=3, column=1, pady=12)
        # 车辆满载装鸡数
        avgcarNum = StringVar(modifyTk)
        avgcarNum.set(other_data[0][9])
        Label(leftFrame, text="棚面车均化宽松度: ", font=("黑体", 13), fg="#000011").grid(row=4, column=0)
        Entry(leftFrame, textvariable=avgcarNum, width=8, font=("黑体", 12)).grid(row=4, column=1, pady=12)
        # 时间单元长度（分钟）
        timeLen = StringVar(modifyTk)
        timeLen.set(other_data[0][11])
        Label(leftFrame, text="时间单元长度(分钟): ", font=("黑体", 13), fg="#000011").grid(row=5, column=0)
        Entry(leftFrame, textvariable=timeLen, width=8, font=("黑体", 12)).grid(row=5, column=1, pady=12)
        # 右边框架
        rightFrame = Frame(Frame1)
        rightFrame.grid(row=0, column=1, pady=10, padx=10)
        # 养户最大等待时间设置
        yhWaitTime = StringVar(modifyTk)
        yhWaitTime.set(other_data[0][5])
        Label(rightFrame, text="养户允许偏差时间: ", font=("黑体", 13), fg="#000011").grid(row=0, column=0)
        Entry(rightFrame, textvariable=yhWaitTime, width=8, font=("黑体", 12)).grid(row=0, column=1, pady=12)
        # 客户最大等待时间设置
        khWaitTime = StringVar(modifyTk)
        khWaitTime.set(other_data[0][6])
        Label(rightFrame, text="客户允许偏差时间: ", font=("黑体", 13), fg="#000011").grid(row=1, column=0)
        Entry(rightFrame, textvariable=khWaitTime, width=8, font=("黑体", 12)).grid(row=1, column=1, pady=12)
        # 模型六求解时间
        model6Time1 = StringVar(modifyTk)
        model6Time1.set(other_data[0][7])
        Label(rightFrame, text="分配模型1求解最大时间: ", font=("黑体", 13), fg="#000011").grid(row=2, column=0)
        Entry(rightFrame, textvariable=model6Time1, width=8, font=("黑体", 12)).grid(row=2, column=1, pady=12)
        # 模型六补充部分求解时间
        model6Time2 = StringVar(modifyTk)
        model6Time2.set(other_data[0][8])
        Label(rightFrame, text="分配模型2求解最大时间: ", font=("黑体", 13), fg="#000011").grid(row=3, column=0)
        Entry(rightFrame, textvariable=model6Time2, width=8, font=("黑体", 12)).grid(row=3, column=1, pady=12)
        # 模型六补充部分求解时间
        bgMaxEff = StringVar(modifyTk)
        bgMaxEff.set(other_data[0][10])
        Label(rightFrame, text="磅效率（每小时）: ", font=("黑体", 13), fg="#000011").grid(row=4, column=0)
        Entry(rightFrame, textvariable=bgMaxEff, width=8, font=("黑体", 12)).grid(row=4, column=1, pady=12)
        # 每个时间单元最多允许客户车数
        maxCarNum = StringVar(modifyTk)
        maxCarNum.set(other_data[0][12])
        Label(rightFrame, text="时间单元最多客户车数: ", font=("黑体", 13), fg="#000011").grid(row=5, column=0)
        Entry(rightFrame, textvariable=maxCarNum, width=8, font=("黑体", 12)).grid(row=5, column=1, pady=12)
        def getCSpagevalue():
            try:
                #连接数据库
                self.conndb.conn()
                self.conndb.update("UPDATE other_info SET startTime = "+str(int(startTime.get()))\
                    + ", yhChickenNum = "+str(int(yhChickenNum.get())) + ", timeNum = "+str(int(timeNum.get()))\
                        + ", carFullNum = "+str(int(carFullNum.get())) + ", yhWaitTime = "+str(int(yhWaitTime.get()))\
                            + ", khWaitTime = "+str(int(khWaitTime.get())) + ", model6Time1 = "+str(int(model6Time1.get()))\
                                + ", model6Time2 = "+str(int(model6Time2.get()))+ ", avg_car_num = "+str(int(avgcarNum.get()))\
                                    + ", bg_eff = "+str(int(bgMaxEff.get())) + ", nlen = "+str(int(timeLen.get())) 
                                    + ", maxcarnum = "+str(int(maxCarNum.get())) +" WHERE oid = 1 ")
                self.conndb.close()
            except:
                tkinter.messagebox.showinfo('提示', '设置失败')
            else:
                tkinter.messagebox.showinfo('提示', '设置成功')
        # 按钮组件
        Frame2 = Frame(modifyTk)
        Frame2.grid(row=3, column=0)
        Button(Frame2, text="设置完成", width=10, font=("黑体", 12),command=lambda:getCSpagevalue()).grid(row=0, column=0, padx=20)
        Button(Frame2, text="返回上一级", width=10, font=("黑体", 12),command=lambda : self.rollback(modifyTk,tk_name)).grid(row=0, column=1, padx=20)
        modifyTk.mainloop()

    def deal_data(self):
        #连接数据库
        self.conndb.conn()
        ''' 棚面及服务站数据 '''
        other_des,other_data = self.conndb.select("SELECT * FROM other_info where oid = 1")
        max_pbdes,max_pbdata = self.conndb.select("SELECT * FROM pm_bg_info")
        maxpm_num = len(max_pbdata) #最大棚面数
        max_pmdict = {max_pbdata[i][0]:max_pbdata[i][1] for i in range(len(max_pbdata))}  #所有的棚面ID以及棚面名
        pbdes,pbdata = self.conndb.select("SELECT * FROM pm_bg_info WHERE pm_bg_num > 0 ")
        use_pmdict = {pbdata[i][0]:pbdata[i][1] for i in range(len(pbdata))}  #启用的棚面ID以及棚面名
        pm_bg_num = [pbdata[i][2] for i in range(len(pbdata))] #每个启用的棚面的使用磅数量
        pm_kh_num = [pbdata[i][3] for i in range(len(pbdata))] #各棚面中每个时间单元内，棚面内最大客户人数 
        use_pmidlist = list(use_pmdict.keys())
        ftdes,fwzdata = self.conndb.select("SELECT * FROM fwz_name")
        pftdes,pfdata = self.conndb.select("SELECT pm_id,fwz_id FROM tb_pm_fwz_info")
        all_pfdict = {pfdata[i][0]:pfdata[i][1] for i in range(len(pfdata))}  #棚面ID:服务站ID
        use_pfdict = {}
        for p in use_pmidlist:
            use_pfdict[p] = all_pfdict[p]
        all_fwz_dict = {fwzdata[i][0]:fwzdata[i][1] for i in range(len(fwzdata))} #服务站ID:服务站名
        use_fwzTopm_id_dict = {}
        for i in range(len(pfdata)):
            if pfdata[i][0] in use_pmidlist:
                if pfdata[i][1] not in list(use_fwzTopm_id_dict.keys()):
                    use_fwzTopm_id_dict[pfdata[i][1]]=[]
                use_fwzTopm_id_dict[pfdata[i][1]].append(pfdata[i][0])
        maxfwz_num = len(fwzdata) #最大服务站数
        use_fwzdict =  {} #启用的服务站ID以及服务站名
        for c in range(len(use_pmidlist)):
            curr_usefwz_id = pfdata[[pfdata[i][0] for i in range(len(pfdata))].index(use_pmidlist[c])][1]
            curr_usefwz_name = fwzdata[[fwzdata[i][0] for i in range(len(fwzdata))].index(curr_usefwz_id)][1]
            use_fwzdict[curr_usefwz_id] = curr_usefwz_name
        pm_num = len(use_pmdict) # pm_num-棚面个数
        #自定义调节数据
        # pjlist = ['标准','大鸡','小鸡','次品鸡']
        stime = int(other_data[0][1])  #stime-开始时间（分钟，如3点则为180分钟） 
        maxNum = int(other_data[0][10])  #maxNum-每个磅单元最大装载量 
        tj_num = int(other_data[0][9]) #棚面车均化分配宽松度
        n_max_carnum = int(other_data[0][2]) #每个时间单元每个养户最多几趟车
        rs_pm = pm_kh_num # 各棚面中每个时间单元内，棚面内最大客户人数 
        max_t = int(other_data[0][7]) #模型6单个模型最大求解时间（秒）
        bre_num = math.ceil(len(use_pmidlist)/2) #插入每个虚拟养户数量(每个养户可以去两个棚面)
        ad_val = int(other_data[0][3]) # ad_val 用于调节每个棚面时间单元宽松度（增添每个棚面的时间单元个数）
        kh_wait_tnum = int(other_data[0][6]) # kh_wait_tnum-客户最大等待时间单元 
        yh_wait_tnum = int(other_data[0][5]) # yh_wait_tnum-养户最大等待时间单元
        car_max_num = int(other_data[0][4]) #车辆满载装鸡数
        s_m6_mt = int(other_data[0][8]) #养户与客户匹配模型（模型6补充模型）单个模型最大运行时间
        Nlen = int(other_data[0][11]) #时间单元长度
        maxCarNum = int(other_data[0][12]) #每个时间单元最多允许客户车数
        isFlag = True #客户最终调整中是否重排客户时间
        bi = 10 #约定时间客户取货相较于没约定时间的客户取货重要度倍数
        ''' 客户数据 '''
        # kh-客户的个数
        kh_tn,r_kh = self.conndb.select("SELECT * FROM order_info")
        kh_supply_tn,r_supply_kh = self.conndb.select("SELECT * FROM order_supply_info")
        kh_temp = [[r_kh[i][1],r_kh[i][2]] for i in range(len(r_kh))] #客户名与其对应取货优先级标志
        kpind = kh_tn.index('spc_1')
        pz_count = 0
        use_pzInd = []
        for i in range(kpind,len(kh_tn)):
            sum_chicken = 0
            for j in range(len(r_kh)):
                if r_kh[j][i] != '' and isinstance(r_kh[j][i], str):
                    sum_chicken += int(r_kh[j][i].split(',')[0])
            if sum_chicken>0:
                use_pzInd.append(i-kpind)
                pz_count = pz_count + 1
        ''' 品种品级数据 '''
        pz = pz_count #品种个数
        pjdes,pjdata = self.conndb.select("SELECT * FROM pj_info")
        pj = len(pjdata) #品级个数
        pjlist = [pjdata[i][1] for i in range(len(pjdata))] #品级名
        ''' 养户数据 '''
        yh_tn,r_yh = self.conndb.select("SELECT * FROM bre_info") # r_yh用于存放每个养户信息
        ypind = yh_tn.index('spc_1')
        yhlist = [r_yh[i][0] for i in range(len(r_yh))] #获取养户id
        yhAllname = [r_yh[i][1] for i in range(len(r_yh))] # yhAllname 用于存放所有养户的名字
        yh = len(yhlist) #获取养户个数
        #获取养户数据
        yhsl = [[[0 for k in range(pj)] for j in range(pz)] for i in range(yh)]
        # ytab 养户超天龄标记(只要存在超龄鸡就认为该养户所养鸡都超天龄) 1：超天龄 0：足天龄 -1：不足天龄
        ytab = [0 for i in range(yh)]   
        for i in range(len(r_yh)):
            for j in range(ypind,pz+ypind):
                if r_yh[i][j] != '' and isinstance(r_yh[i][j], str):
                    data = r_yh[i][j].split(',')  # data=[数量,天龄(养户超天龄标记),品级]
                    data = list(map(int,list(map(float,data))))
                    yhsl[i][j - ypind][int(data[2]) - 1] += int(data[0])
                    if int(data[1])>1:
                        ytab[i] = 0  #获取养户超龄鸡标志
                    elif int(data[1])<-1:
                        ytab[i] = -1  #获取养户超龄鸡标志
                    else:
                        ytab[i] = int(data[1])  #获取养户超龄鸡标志
        ''' 距离数据 '''
        gap = [[0 for j in range(pm_num)] for i in range(yh)] # gap-养户到pm的距离
        for y in range(yh):
            gapdes,gapdata = self.conndb.select("SELECT * FROM gap_info WHERE bre_id= '%s' ", yhlist[y])
            gap_find = gapdes.index('gap_1')
            for i in range(gap_find,len(gapdes)):
                pid = int(gapdes[i].split('_')[1])
                if pid in use_pmidlist:
                    for j in range(len(gapdata)):
                        if gapdata[j][i] != '' and (isinstance(gapdata[j][i], float) or isinstance(gapdata[j][i], int)):  # 有八个值，分别对应八个棚面距离
                            if ytab[y] == 1:
                                gap[y][use_pmidlist.index(pid)] = 0.0001 #如果该养户存在超龄鸡，则将距离设为0.0001
                            else:
                                gap[y][use_pmidlist.index(pid)] = float(gapdata[j][i])
                        else:
                            gap[y][use_pmidlist.index(pid)] = float('inf')  # 距离设为无穷大
        
        specdes,pz_indToname = self.conndb.select("SELECT * FROM bre_name") #鸡品种id对应品种名
        self.conndb.close()
        # ''' 存表地址 '''
        # #中间过程存表 
        # data_info_path = r'.\wenshi0306\output_tabel\数据信息表.xls'
        # info_path = r'.\wenshi0306\output_tabel\信息表.xls'
        # kyinfo_path = r'.\wenshi0306\output_tabel\调配信息表.xls'
        # car_path = r'.\wenshi0306\output_tabel\车次信息表.xls'
        # #调度结果存表
        # yh_info_path = r'.\wenshi0306\output_tabel\养户调度表.xls'
        # new_path = r'.\wenshi0306\output_tabel\新调度结果表.xls'
        # kh_info_path = r'.\wenshi0306\output_tabel\客户信息表.xls'
        # pathky = r'.\wenshi0306\output_tabel\客户与养户匹配调度表.xls'
        # 执行调度
        args_main = pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_carnum,bi,maxNum,pz,pj,use_pzInd,pm_bg_num,Nlen,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t,ad_val, kh_wait_tnum, yh_wait_tnum, car_max_num, s_m6_mt, maxCarNum, isFlag
        # yh_info_path 养户调度表 data_info_path-数据信息表 kyinfo_path-调配信息表 car_path-车次信息表 kh_info_path-客户信息表
        # args_path = yh_info_path,new_path,kh_info_path,data_info_path,car_path,kyinfo_path,pathky
        # use_fwzdict 启用的服务站ID以及服务站名
        # use_fwzTopm_id_dict 启用服务站ID对应该服务站启用的棚面ID
        # use_pfdict 启用的棚面ID以及启用的服务站ID
        # use_pmdict 启用的棚面ID以及棚面名
        fpb_arg = use_fwzdict, use_pmdict, use_pfdict, use_fwzTopm_id_dict
        self.args_main = args_main
        # self.args_path = args_path
        self.fpb_arg = fpb_arg
        # self.yhtable = yh_info_path
        # self.khtable = kh_info_path
        self.pz_num = pz
    #参数调整界面-----------------------------------------------------------------------------------------------------------
    def createfwzpmbgPage(self,tk_name):
        #连接数据库
        self.conndb.conn()
        
        ''' 棚面及服务站数据 '''
        max_pbdes,max_pbdata = self.conndb.select("SELECT * FROM pm_bg_info")
        ftdes,fwzdata = self.conndb.select("SELECT * FROM fwz_name")
        pftdes,pfdata = self.conndb.select("SELECT pm_id,fwz_id FROM tb_pm_fwz_info")
        self.conndb.close()
        maxpm_num = len(max_pbdata) #最大棚面数
        max_pmdict = {max_pbdata[i][0]:max_pbdata[i][1] for i in range(len(max_pbdata))}  #所有的棚面ID以及棚面名
        all_fwz_dict = {fwzdata[i][0]:fwzdata[i][1] for i in range(len(fwzdata))} #服务站ID:服务站名
        all_fwzTopm_id_dict = {}
        for i in range(len(pfdata)):
            if pfdata[i][1] not in list(all_fwzTopm_id_dict.keys()):
                all_fwzTopm_id_dict[pfdata[i][1]]=[]
            all_fwzTopm_id_dict[pfdata[i][1]].append(pfdata[i][0])
        all_pmTofwz_id_dict = {pfdata[i][0]:pfdata[i][1] for i in range(len(pfdata))}  #棚面ID:服务站ID
        tk_name.withdraw()
        numTk = Tk()
        numTk.title("服务站参数调整")
        numTk.maxsize(1200, 500)  # 设置窗口最大尺寸
        # 设置页面居中
        self.center_window(numTk, 800, 450)
        #动态变化函数
        def bindfunction(*args):
            Label(fwzFrame, text="调整的棚面: ", font=("黑体", 13), fg="#000011", width=13).grid(row=2, column=0, padx=5, pady=10)
            pmcom = Combobox(fwzFrame, textvariable=pmvalue, width=18, font=("黑体", 12))
            pmcom.grid(row=2, column=1)
            curr_fwz_id = list(all_fwz_dict.keys())[list(all_fwz_dict.values()).index(fwzvalue.get())]
            curr_pm_id_list = all_fwzTopm_id_dict[curr_fwz_id]
            curr_pm_name_list = [max_pmdict[curr_pm_id_list[i]] for i in range(len(curr_pm_id_list))]
            pmcom["values"] = curr_pm_name_list
            # pmcom["values"] = ['1号棚面']
            # print("1111")

        Label(numTk, text='调整参数界面     ', width=90, height=2,
              bg='#666666', fg="#F8F8FF", font=("黑体", 13)).grid(row=0, column=0)
        # 调整界面的框架
        fwzFrame = Frame(numTk)
        fwzFrame.grid(row=1, column=0, pady=10)
        # 调整的下拉框--服务站
        Label(fwzFrame, text="调整的服务站: ", font=("黑体", 13), fg="#000011", width=13).grid(row=0, column=0, padx=5, pady=10)
        fwzvalue = StringVar(numTk)
        fwzcom = Combobox(fwzFrame, textvariable=fwzvalue, width=18, font=("黑体", 12))
        fwzcom.grid(row=0, column=1)
        fwzcom["values"] = list(all_fwz_dict.values())
        fwzcom.current(0)
        fwzcom.bind("<<ComboboxSelected>>",bindfunction)

        # 调整的下拉框--棚面
        Label(fwzFrame, text="调整的棚面: ", font=("黑体", 13), fg="#000011", width=13).grid(row=2, column=0, padx=5, pady=10)
        pmvalue = StringVar(numTk)
        pmcom = Combobox(fwzFrame, textvariable=pmvalue, width=18, font=("黑体", 12))
        pmcom.grid(row=2, column=1)
        curr_fwz_id = list(all_fwz_dict.keys())[list(all_fwz_dict.values()).index(fwzvalue.get())]
        curr_pm_id_list = all_fwzTopm_id_dict[curr_fwz_id]
        curr_pm_name_list = [max_pmdict[curr_pm_id_list[i]] for i in range(len(curr_pm_id_list))]
        pmcom["values"] = curr_pm_name_list
        # pmcom["values"] = ['1','2']
        pmcom.current(0)

        #每个棚面每个时间单元容纳的客户数
        pmkhnum = StringVar(numTk)
        pmkhnum.set(20)
        Label(fwzFrame, text="棚面最大客户量: ", font=("黑体", 13), fg="#000011").grid(row=3, column=0, padx=5, pady=10)
        pkcom = Entry(fwzFrame, textvariable=pmkhnum, width=20,font=("黑体", 12))
        pkcom.grid(row=3, column=1)
        # 调整的下拉框--磅
        Label(fwzFrame, text="该棚面的磅个数: ", font=("黑体", 13), fg="#000011").grid(row=4, column=0, padx=5, pady=10)
        bgvalue = StringVar(numTk)
        bgcom = Combobox(fwzFrame, textvariable=bgvalue, width=18, font=("黑体", 12))
        bgcom.grid(row=4, column=1)
        bgcom["values"] = ['0', '1', '2', '3', '4']
        bgcom.current(4)

        fwzpmbgTextValue = StringVar(numTk)
        # fwzpmbgTextValue.set("配置信息")
        #修改配置信息的函数
        def setpageData():
            #连接数据库
            self.conndb.conn()
            ''' 棚面及服务站数据 '''
            use_pbdes,use_pbdata = self.conndb.select("SELECT * FROM pm_bg_info where pm_bg_num>0")
            self.conndb.close()
            use_pm_bg_dict = {use_pbdata[i][0]:[use_pbdata[i][2],use_pbdata[i][3]] for i in range(len(use_pbdata))}
            use_pm_id_list = list(use_pm_bg_dict.keys())
            use_fwz_id_list = [all_pmTofwz_id_dict[use_pm_id_list[i]] for i in range(len(use_pm_id_list))]
            data_info = {}
            for i in range(len(use_fwz_id_list)):
                if use_fwz_id_list[i] not in list(data_info.keys()):
                    data_info[use_fwz_id_list[i]]=[]
                data_info[use_fwz_id_list[i]].append([use_pm_id_list[i],use_pm_bg_dict[use_pm_id_list[i]][0],use_pm_bg_dict[use_pm_id_list[i]][1]])
            strTextValue = ""
            for f in list(data_info.keys()):
                strTextValue += all_fwz_dict[f] + ":"
                for p in range(len(data_info[f])):
                    curr_pm_name = max_pmdict[data_info[f][p][0]]
                    curr_bg_num = int(data_info[f][p][1])
                    max_p = int(data_info[f][p][2])
                    strTextValue += " "+ curr_pm_name + "("+str(max_p)+")启用"+str(curr_bg_num)+"个磅;"
                strTextValue += "\n"

            fwzpmbgTextValue.set(strTextValue)
            Label(dataFrame, text=fwzpmbgTextValue.get(), font=("黑体", 13), bg='#ffffff', \
              fg="#000011", width=80, height=8).grid(row=1, column=0)
        #获取下拉框的函数
        def getfwzpmbgvalue():
            try:
                #连接数据库
                self.conndb.conn()
                curr_fwz_id = list(all_fwz_dict.keys())[list(all_fwz_dict.values()).index(fwzvalue.get())]
                # curr_pm_id = all_fwzTopm_id_dict[curr_fwz_id][int(pmvalue.get())-1]
                curr_pm_id = list(max_pmdict.keys())[list(max_pmdict.values()).index(pmvalue.get())]
                # pmkhnum
                self.conndb.update("UPDATE pm_bg_info SET pm_bg_num = "+str(int(bgvalue.get()))+",pmkhnum = "+str(int(pmkhnum.get()))+" WHERE pm_id = "+str(int(curr_pm_id))+" ")
                # conndb.update("UPDATE pm_bg_info SET pm_bg_num = %d WHERE pm_id = %d ",(int(bgvalue.get()),int(curr_pm_id)))
                self.conndb.close()
            except:
                tkinter.messagebox.showinfo('提示', '修改失败')
            else:
                tkinter.messagebox.showinfo('提示', '修改成功')
                setpageData()
        # 下方的确认按钮框架
        fwzbuttonFrame = Frame(numTk)
        fwzbuttonFrame.grid(row=4, column=0, pady=2)
        Button(fwzbuttonFrame, text="继续修改", width=15, font=("黑体", 14),command=lambda:getfwzpmbgvalue()).grid(row=0, column=0, padx=5)
        # Button(fwzbuttonFrame, text="查看当前配置", width=15, font=("黑体", 12),command=lambda:setpageData()).grid(row=0, column=1, padx=5)
        Button(fwzbuttonFrame, text="返回上一级", width=15, font=("黑体", 14),command=lambda: self.rollback(numTk,tk_name)).grid(row=0, column=2, padx=5)
        
        # 修改的信息栏
        dataFrame = Frame(numTk)
        dataFrame.grid(row=5, column=0, pady=5)
        Label(dataFrame, text="当前的各服务站信息:                                                             ", \
              font=("黑体", 13), fg="#000011").grid(row=0, column=0, padx=5)
        Label(dataFrame, text=fwzpmbgTextValue.get(), font=("黑体", 13), bg='#ffffff', \
              fg="#000011", width=80, height=8).grid(row=1, column=0)
        setpageData()
        numTk.mainloop()
    #插入虚拟养户
    def create_vir_yh(self,args_vy):
        if self.isflag:
            try:
                self.conndb.conn()
                pz, pj, bre_num = args_vy
                # bre_num = 2
                for u in range(pz):
                    for k in range(pj):
                        for i in range(bre_num):
                            if u >= 9:
                                sql_1 = "DELETE FROM bre_info where bre_name = '虚拟养户"+str(u+1) + "0" + str(k+1)+ "0" + str(i+1)+"'"
                                sql_2 = "DELETE FROM gap_info where bre_name = '虚拟养户"+str(u+1) + "0" + str(k+1)+ "0" + str(i+1)+"'"
                            else:
                                sql_1 = "DELETE FROM bre_info where bre_name = '虚拟养户0"+str(u+1) + "0" + str(k+1)+ "0" + str(i+1)+"'"
                                sql_2 = "DELETE FROM gap_info where bre_name = '虚拟养户0"+str(u+1) + "0" + str(k+1)+ "0" + str(i+1)+"'"
                            self.conndb.delete(sql_1)
                            self.conndb.delete(sql_2)
                bre_id = ['' for i in range(pz*pj*bre_num)]
                for u in range(pz):
                    for k in range(pj):
                        for i in range(bre_num):
                            if u >= 9:
                                bre_id[u*pj*bre_num+k*bre_num+i] = 'b'+ str(u+1) + '0' + str(k+1) + '0' + str(i+1)
                            else:
                                bre_id[u*pj*bre_num+k*bre_num+i] = 'b0' + str(u+1) + '0' + str(k+1) + '0' + str(i+1)
                bre_name = ['' for i in range(pz*pj*bre_num)]
                for u in range(pz):
                    for k in range(pj):
                        for i in range(bre_num):
                            if u >= 9:
                                bre_name[u*pj*bre_num+k*bre_num+i] = '虚拟养户'+str(u+1) + '0' + str(k+1) + '0' + str(i+1)
                            else:
                                bre_name[u*pj*bre_num+k*bre_num+i] = '虚拟养户0' + str(u+1) + '0' + str(k+1) + '0' + str(i+1)

                for u in range(pz):
                    for k in range(pj):
                        for i in range(bre_num):
                            sql1 = "insert into bre_info (bre_id, bre_name,bre_fwz,bre_phone,bre_address,bre_longitude_latitude,spc_" + str(u+1) +\
                                    ") values ('" + bre_id[u*pj*bre_num+k*bre_num+i] + "','" + bre_name[u*pj*bre_num+k*bre_num+i] + "',\'\' ,\'\',\'\',\'\','" + str(50000) + ",0,"+str(k+1)+"')"
                            self.conndb.insert(sql1)
                            fwz1 = random.randint(1, 3) * 100000
                            fwz2 = random.randint(1, 3) * 100000
                            fwz3 = random.randint(1, 3) * 100000
                            fwz4 = random.randint(1, 3) * 100000
                            fwz5 = random.randint(1, 3) * 100000

                            sql2 = "insert into gap_info (bre_id, bre_name, bre_fwz, bre_address, gap_1, gap_2, gap_3, gap_4,gap_5, gap_6, gap_7, gap_8)\
                                values ('" + bre_id[u*pj*bre_num+k*bre_num+i] + "','" + bre_name[u*pj*bre_num+k*bre_num+i] + "',\'\' ,\'\'," + str(fwz1)+\
                                    ","+str(fwz1)+","+str(fwz2)+","+str(fwz3)+\
                                        ","+str(fwz3)+","+str(fwz4)+","+str(fwz4)+","+str(fwz5)+")"
                            self.conndb.insert(sql2)
                self.conndb.close()
            except:
                tkinter.messagebox.showinfo('错误', '数据验证失败')
            # else:
            #     tkinter.messagebox.showinfo('提示', '数据验证成功') 
        else:
            tkinter.messagebox.showinfo('提示', '数据已验证成功，无需重新验证！')
    def pre_cvy(self):
        if self.isflag:
            #连接数据库
            self.conndb.conn()
            kh_tn,r_kh = self.conndb.select("SELECT * FROM order_info")
            kpind = kh_tn.index('spc_1')
            pz_count = 0
            for i in range(kpind,len(kh_tn)):
                sum_chicken = 0
                for j in range(len(r_kh)):
                    if r_kh[j][i] != '' and isinstance(r_kh[j][i], str):
                        sum_chicken += int(r_kh[j][i].split(',')[0])
                if sum_chicken>0:
                    # print(kh_tn[i])
                    pz_count = pz_count + 1
            ''' 品种品级数据 '''
            self.prepz = pz_count #品种个数
            pjdes,pjdata = self.conndb.select("SELECT * FROM pj_info")
            self.prepj = len(pjdata) #品级个数
            pbdes,pbdata = self.conndb.select("SELECT * FROM pm_bg_info WHERE pm_bg_num > 0 ")
            self.bre_num = math.ceil(len(pbdata)/2) #插入每个虚拟养户数量(每个养户可以去两个棚面)
            # self.bre_num = 2
            self.conndb.close()
        if self.prepz>0 and self.prepj>0 and self.bre_num>0:
            args_pc = self.prepz,self.prepj,self.bre_num
            self.create_vir_yh(args_pc)
            if self.isflag:
                tkinter.messagebox.showinfo('提示', '数据验证成功') 
            self.isflag = 0
        else:
            tkinter.messagebox.showinfo('错误', '不符合运行检测数据情况的条件，请在适当情况下进行')
    #执行调度程序
    def runMain(self):
        if self.isflag:
            #连接数据库
            self.conndb.conn()
            kh_tn,r_kh = self.conndb.select("SELECT * FROM order_info")
            kpind = kh_tn.index('spc_1')
            pz_count = 0
            for i in range(kpind,len(kh_tn)):
                sum_chicken = 0
                for j in range(len(r_kh)):
                    if r_kh[j][i] != '' and isinstance(r_kh[j][i], str):
                        sum_chicken += int(r_kh[j][i].split(',')[0])
                if sum_chicken>0:
                    # print(kh_tn[i])
                    pz_count = pz_count + 1
            ''' 品种品级数据 '''
            self.prepz = pz_count #品种个数
            pjdes,pjdata = self.conndb.select("SELECT * FROM pj_info")
            self.prepj = len(pjdata) #品级个数
            pbdes,pbdata = self.conndb.select("SELECT * FROM pm_bg_info WHERE pm_bg_num > 0 ")
            # print(len(pbdata))
            self.bre_num = math.ceil(len(pbdata)/2) #插入每个虚拟养户数量(每个养户可以去两个棚面)
            # self.bre_num = 2
            self.conndb.close()
            if self.prepz>0 and self.prepj>0 and self.bre_num>0:
                args_pc = self.prepz,self.prepj,self.bre_num
                print('开始验证数据')
                self.create_vir_yh(args_pc)
                print('数据验证完成')
                self.isflag = 0  
        self.deal_data() #执行数据处理
        # pm_num-棚面个数 stime-开始时间（分钟，如3点则为180分钟） n-时间单元长度（分钟） maxNum-每个磅单元最大装载量 
        # pz-品种 pj-品级 pm_bg_num #每个棚面的磅数量
        # yh-养户个数 yhsl-养户品种品级数量 yhAllname-每个养户对应的养户名 gap-每个养户到每个棚面距离
        # pz_indToname-品种索引对应的品种名 pjlist-品级索引对应的品级名 rs_pm-每个棚面的时间单元最大客户数 max_t-模型最大求解时间（秒）
        # kh_tn-客户表表头名称  r_kh-客户表数据 kh_temp-客户名与其对应取货优先级标志
        # ad_val 用于调节每个棚面时间单元宽松度（增添每个棚面的时间单元个数）
        # yh_info_path 养户调度表 data_info_path-数据信息表 kyinfo_path-调配信息表 car_path-车次信息表 kh_info_path-客户信息表
        pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_carnum,bi,maxNum,pz,pj,use_pzInd,pbgNum,Nlen,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t, ad_val, khOffT, yhOffT, carMaxNum, one_max_t, maxCarNum, isFlag = self.args_main
        
        if self.isflag:
            print('开始插入虚拟养户')
            args_vy = pz, pj, self.bre_num
            self.create_vir_yh(args_vy)
            print('虚拟养户插入完成')
            self.isflag = 0

        args_m1 = use_pzInd,pm_num,tj_num,use_pmidlist,pj,stime,pbgNum,maxNum, kh_tn, r_kh, r_supply_kh
        print('开始进入模型1')
        # pkhName-每个棚面每个客户名
        # khPts-每个棚面每个客户预计取货时间
        # pkhSl-每个棚面每个客户取鸡品种品级数量
        kh_info, pkhName, khPts, pkhSl = AssKh(args_m1).dealKhData()
        print('模型1运行完成')
        #连接数据库
        conndb = ConnDB(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
        conndb.conn()
        # r_yh用于存放每个养户信息
        yh_tn, r_yh = conndb.select("SELECT * FROM bre_info")
        ypind = yh_tn.index('spc_1')
        yhlist = [r_yh[i][0] for i in range(len(r_yh))] # results[i][0] 养户编号位置段
        yh = len(yhlist) #获取养户个数
        #获取养户数据
        yhsl = [[[0 for k in range(pj)] for j in range(pz)] for i in range(yh)]
        # ytab 养户超天龄标记(只要存在超龄鸡就认为该养户所养鸡都超天龄) 1：超天龄 0：足天龄 -1：不足天龄
        ytab = [0 for i in range(yh)]
        # yhAllname 用于存放所有客户的名字
        yhAllname = ['' for i in range(yh)]
        # gap-养户到pm的距离
        gap = [[0 for j in range(pm_num)] for i in range(yh)]
        for y in range(yh):
            ydes, yres = conndb.select("SELECT * FROM bre_info WHERE bre_id= '{}'".format(yhlist[y]))
            for i in range(len(yres)):
                for j in range(1, len(yres[i])):  # 5为养户表中鸡品种开始索引位置，可调整
                    if j == 1:
                        yhAllname[y] = yres[i][j]
                    if j >= ypind:
                        if yres[i][j] != '' and isinstance(yres[i][j], str):
                            data = yres[i][j].split(',')  # data=[数量,天龄(养户超天龄标记),品级]
                            data = list(map(int,list(map(float,data))))
                            yhsl[y][j - ypind][int(data[2]) - 1] += int(data[0])
                            if int(data[1])>1:
                                ytab[y] = 0  #获取养户超龄鸡标志
                            elif int(data[1])<-1:
                                ytab[y] = -1  #获取养户超龄鸡标志
                            else:
                                ytab[y] = int(data[1])  #获取养户超龄鸡标志
            
            gdes,gres = conndb.select("SELECT * FROM gap_info WHERE bre_id= '{}'".format(yhlist[y]))
            for i in range(4,len(gres[0])-8 + pm_num):
                # isinstance 判断类型
                if gres[0][i] != '' and (isinstance(gres[0][i], float) or isinstance(gres[0][i], int)):  # 有八个值，分别对应八个棚面距离
                    if ytab[y] == 1:
                        gap[y][i-4] = 0.0001 #如果该养户存在超龄鸡，则将距离设为0.0001
                    else:
                        gap[y][i-4] = float(gres[0][i])
                else:
                    gap[y][i-4] = float('inf')  # 距离设为无穷大
        
        #关闭连接
        conndb.close()

        # 获取每个棚面客户数
        kpt = [len(kh_info[i]) for i in range(pm_num)]
        # 获取每个棚面时间单元整合客户需求品种品级情况
        KFSLfpz = [[[[0 for d in range(pj)] for p in range(pz)] for j in range(kpt[i])] for i in range(pm_num)]
        # 获取每个棚面每个时间单元中每个客户需求品种品级情况
        KHNpp = [[[[[0 for d in range(pj)] for p in range(pz)] for k in range(len(kh_info[i][j]['cus_name']))] for j in range(len(kh_info[i]))] for i in range(len(kh_info))]
        # 获取每个棚面每个时间单元中每个客户名
        KHNname = [[['' for k in range(len(kh_info[i][j]['cus_name']))] for j in range(len(kh_info[i]))] for i in range(len(kh_info))]

        for i in range(len(kh_info)):
            for j in range(len(kh_info[i])):
                key_name = list(kh_info[i][j].keys())[2:-2]
                for k in range(len(key_name)):
                    if key_name[k]=='detail_info':
                        for m in range(len(kh_info[i][j][key_name[k]])):
                            KHNname[i][j][m] = kh_info[i][j][key_name[k]][m]['cus_name']
                            kname = list(kh_info[i][j][key_name[k]][m].keys())[1:]
                            for n1 in range(len(kname)):
                                KHNpp[i][j][m][int(kname[n1].split('_')[1])-1][kh_info[i][j][key_name[k]][m][kname[n1]][1]-1] = kh_info[i][j][key_name[k]][m][kname[n1]][0]
                    else:
                        for d in range(pj):
                            KFSLfpz[i][j][int(key_name[k].split('_')[1])-1][d] = kh_info[i][j][key_name[k]][d]
        
        args = yh, pm_num, pz, pj, gap, KHNpp, KHNname, yhsl, yhAllname
        print('开始进入模型2')
        # pyhSL 每个棚面每个养户送品种品级鸡数量
        # yh_detail每个棚面每个养户每个时间单元送品种品级鸡数量
        # yh_temp 每个棚面每个养户每个时间单元是否送鸡
        # yhsl 每个养户剩余品种品级鸡的数量
        pyhSL, yh_detail, yh_temp, yhsl = AssYh(args).assy()
        print('模型2运行完成')
        # fwzPmInd-每个服务站所属棚面索引
        # pkhSl-每个棚面每个客户取鸡品种品级数量
        # pyhSL 每个棚面每个养户送品种品级鸡数量
        # stList-每个棚面开棚时间(分钟)
        # Nt-每个棚面时间单元松弛变量
        # Prs-每个棚面时间单元允许最大客户数
        # pbgNum-每个棚面开磅数
        # bgEff-磅每个时间单元处理效率
        # Nlen-磅处理时间单元长度（分钟）
        # khPt-该棚面每个客户预计取货时间单元
        # khOffT-每个客户允许偏差时间单元
        # yhOffT-每个养户最早开始送货和最晚结束送货之间允许偏差时间单元
        # fktYn-每个服务站每个养户已经开始卸货车辆卸货所属时间[[]]
        # fktYse-每个服务站每个养户已知的最早开始卸货时间和最晚卸货时间
        # car_path-车辆结果表存储地址
        use_pyhSL = [[] for i in range(len(pyhSL))]
        use_yhAllname = []
        for j in range(len(yhAllname)):
            if sum([sum([sum([pyhSL[i][j][p][d] for d in range(len(pyhSL[i][j][p]))]) for p in range(len(pyhSL[i][j]))]) for i in range(len(pyhSL))])>0:
                use_yhAllname.append(yhAllname[j])
                for i in range(len(pyhSL)):
                    use_pyhSL[i].append(pyhSL[i][j])
        
        pidList = sorted(use_pmidlist)
        fidList = sorted(list(set(list(use_pfdict.values()))))
        fwzPmInd = [[] for i in range(len(fidList))]
        for i in list(use_pfdict.keys()):
            fwzPmInd[fidList.index(use_pfdict[i])].append(pidList.index(i))
        stList = [stime for i in range(len(pidList))]
        Nt = [ad_val for i in range(len(pidList))]
        # Prs = rs_pm+20
        Prs = [rs_pm[i] for i in range(len(rs_pm))]
        # Nlen = 60
        bgEff = int(maxNum*Nlen/60)
        # kh_temp #客户名与其对应取货时间
        khPt = [[(math.floor((khPts[i][j]-stList[i])/Nlen) if khPts[i][j]!=-1 else khPts[i][j]) for j in range(len(khPts[i]))] for i in range(len(khPts))]
        print("************************")
        print(khPt)
        print("************************")
        fktYn = [[[] for j in range(yh)] for i in range(len(fidList))]
        fktYse = [[[math.inf,-math.inf] for j in range(yh)] for i in range(len(fidList))]
        car_path = r'.\wenshi210701\output_table\车次信息表.xlsx'
        kyinfo_path = r'.\wenshi210701\output_table\调配信息表.xlsx'
        kh_path = r'.\wenshi210701\output_table\客户调度表.xlsx'
        yh_path = r'.\wenshi210701\output_table\养户调度表.xlsx'
        ky_path = r'.\wenshi210701\output_table\调配结果信息表.xlsx' 
        new_path = r'.\wenshi210701\output_table\新调度结果表.xlsx'
        argsM3 = max_t, pz, pj, use_yhAllname, pz_indToname, pjlist,pkhSl,use_pyhSL,carMaxNum,fwzPmInd,stList,Nt,Prs,pbgNum,n_max_carnum,bi,bgEff,Nlen,khPt,khOffT,yhOffT,fktYn,fktYse,car_path
        ynpp_res, knpp_res, carpYhInd, fktYn, fktYse, yhCarNum = MatchKy(argsM3,self.fpb_arg).matchKy()
        pzlist = [pz_indToname[i][1] for i in range(pz)]
        ky_res, vir_ky = DetailKy_ky(knpp_res,ynpp_res,use_yhAllname,carpYhInd,bgEff,one_max_t).detKy()

        args_ky = pkhName,carpYhInd,use_yhAllname,pz,pj,pzlist,pjlist,ynpp_res, knpp_res, fktYn, fktYse , ky_res, vir_ky, stList, pbgNum, carMaxNum, maxNum, Nlen
        args_path = yh_path, ky_path, new_path,kyinfo_path
        SaveKyResult(args_ky,args_path,self.fpb_arg).saveResult()

        output_path = r"D:\VSCode\Wenshi2020\wenshi210701\output_table\最终调配结果信息表.xlsx"
        finalDealKh(ky_path, kyinfo_path, output_path, pbgNum, bgEff, Nlen, maxCarNum, pkhName, khPt, isFlag).saveKh()

if __name__ == '__main__':
    UIkyMain()


from gurobipy import *
from pulp.apis.gurobi_api import GUROBI
from Obj_fun import Obj_fun
from ConnDB import ConnDB
import pulp as pulp
import math as m1
# 小时转分钟
def t2m(t):
    h,m,s = t.strip().split(":")
    s1=0
    if int(s)>0:
        s1=1
    return int(h) * 60 + int(m) + s1
def solve_ilp(objective, constraints):
    # print(objective)
    # print(constraints)
    prob = pulp.LpProblem('LP', pulp.LpMinimize)
    prob += objective
    for cons in constraints:
        prob += cons
    # print(prob)
    # status = prob.solve(GUROBI(mip=1, msg=1 , timeLimit=3000))
    status = prob.solve(pulp.GUROBI_CMD(keepFiles=0, mip=1, msg=1 ,timeLimit=1200 ,options=[("MIPGap", "0.15")]))
    # status = prob.solve(GUROBI(mip=1, msg=1 , timeLimit=3000))
    # status = prob.solve(pulp.PULP_CBC_CMD(msg=1,maxSeconds=60))
    print(status)
    if status != 1:
        # print 'status'
        # print status
        return None
    else:
        # return prob
        # return [v.name for v in prob.variables()]

        return [(v.name,v.varValue) for v in prob.variables()]

if __name__ == '__main__':
    # 连接数据库
    conndb = ConnDB(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
    conndb.conn()
    ''' 客户关系 '''
    # kh-客户的个数
    sql = "SELECT * FROM order_info"
    data = ()
    r_kh = conndb.select(sql, data)
    khlist = []
    for i in range(len(r_kh)):
        khlist.append(r_kh[i][0])  # r_yh[i][0] 客户编号位置段
    # khlist=list(set(khlist))
    khlist = list(khlist)
    kh = len(khlist)
    ''' 养户关系 '''
    # yh-养户个数
    sql = "SELECT * FROM bre_info"
    data = ()
    r_yh = conndb.select(sql, data)
    yhlist = []
    for i in range(len(r_yh)):
        yhlist.append(r_yh[i][0])  # results[i][0] 养户编号位置段
    # yhlist=list(set(yhlist))
    yhlist = list(yhlist)
    yh = len(yhlist)
    # pz-品种数 （已知）
    setpz = -87 + 15
    pz = len(r_kh[0]) - 6 + setpz # 每条订单数据的长度减去客户编号、客户名、预计提货时间、客户详细地址、客户经度、客户纬度六项，可调整
    # pj-品级种数 每种品级代表：1-大 2-标准 3-小 4-不合格
    pj = 1  # 暂时不考虑不合格品种
    ''' 生产线关系 '''
    # fwz-服务站个数   服务站-->["勒竹","新大地","稔村","车岗"]
    fwz = 1
    # pm-每个服务站拥有棚面个数
    pm = [2]
    # bg-磅个数
    bg = 4
    # Ttotal-服务站员工的总工作时间长度（分钟）
    # to-服务站员工开始工作时间（分钟），可调整
    # te-服务站员工结束工作时间（分钟），可调整
    te = 720
    to = 180
    Ttotal = te - to
    # n-时间维度切分次数
    # t-切分时间单元长度，先假设60分钟为一段，可调整
    t = 60
    n = int(Ttotal / t) + 1
    # m-最大出车次数，可调整
    m = 30
    # gap-养户到服务站的距离
    gap = [[0 for j in range(fwz)] for i in range(yh)]
    for y in range(yh):
        sql = "SELECT * FROM gap_info WHERE bre_id= '%s' "
        data = (yhlist[y],)  # yhlist[y] 养户id
        res = conndb.select(sql, data)
        for i in range(2, len(res[0])-(4-fwz)):
            if res[0][i] != None:  # 有四个值，分别对应四个服务站距离
                gap[y][i - 2] = float(res[0][i])
            else:
                gap[y][i - 2] = float('inf')  # 距离设为无穷大
            # theta1 某一客户的某一品种的鸡实际装货量的上下浮动百分比，可调整
    theta1 = 0
    # theta2 某一客户的所有品种的鸡实际装货量的上下浮动百分比，可调整
    theta2 = 0
    # theta3 所有客户的某一品种的鸡实际装货量的上下浮动百分比，可调整
    theta3 = 0
    # theta4 所有客户的所有品种的鸡实际装货量的上下浮动百分比，可调整
    theta4 = 0
    # theta5 某一养户的某一品种的鸡实际装货量的上下浮动百分比，可调整
    theta5 = 0
    # theta6 某一养户的所有品种的鸡实际装货量的上下浮动百分比，可调整
    theta6 = 0
    # theta7 所有养户的某一品种的鸡实际装货量的上下浮动百分比，可调整
    theta7 = 0
    # theta8 所有养户的所有品种的鸡实际装货量的上下浮动百分比，可调整
    theta8 = 0
    # sl-订单中每个客户要求每个品种品级数量
    # kht-订单中每个客户要求预计提货时间
    sl = [[[0 for k in range(pj)] for j in range(pz)] for i in range(kh)]
    kht = ['' for i in range(kh)]
    for k in range(kh):
        sql = "SELECT * FROM order_info WHERE cus_id= '%s' "
        data = (khlist[k],)  # khlist[k] 客户id
        res = conndb.select(sql, data)
        for i in range(len(res)):
            for j in range(5, len(res[i]) + setpz):
                if j == 5:  # 5为订单表中客户预计开始取货时间的索引位置，可调整
                    kht[k] = res[i][j]  # 暂时忽略同一客户多次订单要求不同取货时间情况
                if j >= 6:  # 6为订单表中鸡品种开始索引位置，可调整
                    if res[i][j] != '' and isinstance(res[i][j], str):
                        data = res[i][j].split(',')  # data=[数量,天龄,均重,品级]
                        sl[k][j - 6][int(data[3]) - 1] += int(data[0])
    # print(sl)
    # ysl-订单中每个养户可提供每个品种品级数量
    ysl = [[[0 for k in range(pj)] for j in range(pz)] for i in range(yh)]
    for y in range(yh):
        sql = "SELECT * FROM bre_info WHERE bre_id= '%s' "
        data = (yhlist[y],)  # yhlist[y] 养户id
        res = conndb.select(sql, data)
        for i in range(len(res)):
            for j in range(5, len(res[i]) + setpz):  # 5为养户表中鸡品种开始索引位置，可调整
                if res[i][j] != '' and isinstance(res[i][j], str):
                    data = res[i][j].split(',')  # data=[数量,天龄,均重,品级]
                    ysl[y][j - 5][int(data[3]) - 1] += int(data[0])
    # print(ysl)
    # khon-客户预计最早提货时间
    # khend-客户预计最晚取完货时间
    # kh_tw-客户时间窗
    khon = [0 for i in range(kh)]
    khend = [0 for i in range(kh)]
    kh_tw = []
    eff = 2000  # 每个时间维度处理效率
    for k in range(kh):
        t1 = kht[k].split(' ')  # "2019-5-10 23:40:00"
        khon[k] = t2m(t1[1])  # 时间转分钟
        khend[k] = khon[k] + m1.ceil(sum(sum(sl[k][p][d] for d in range(pj)) for p in range(pz)) / eff) * 60 + 120
        kh_tw.append([khon[k], khend[k]])
        # time_t1 = datetime.strptime(t1[1],'%H:%M:%S')
    args = kh, yh, fwz, pm, bg, n, pz, pj, m, gap, t
    args1 = theta1, theta2, theta3, theta4, theta5, theta6, theta7, theta8
    args2 = kh, yh, fwz, pm, bg, n, pz, pj, m, t, khon, khend, sl, ysl
    mm1 = m * yh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
    mm2 = kh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
    print(mm1)
    print(mm2)
    print(mm1 + mm2)
    print(kh, yh, fwz, pm, bg, n, pz, pj, m, t)
    # print(kh, yh, fwz, pm, bg, n, pz, pj, m, t, khon, khend, kh_tw, sl, ysl)

    objfun = Obj_fun(args, args1, args2)
    # objective = objfun.obj()
    # constraints = objfun.con()   
    objective, constraints = objfun.obj()
    res = solve_ilp(objective, constraints)
    value = []
    dict1 = {}
    for i in range(len(res)):
        if ('X' in res[i][0]):
            value.append(res[i][1])
            if res[i][1]>0:
                # str1 = ()[:]
                ind = res[i][0]
                # ind = len(value) - 1
                val = res[i][1]
                dict1[ind] = val

    for k, v in dict1.items():           
	    print( k, v)
    # for key in dict1.keys():
    #     print(key)
    # for value in dict1.values():
    #     print(value)
    print('******************************************************')
    fwzname = {0:"勒竹",1:"新大地",2:"稔村",3:"车岗"}
    khdata = []
    yhdata = []
    cc = 0
    for u in range(m):
        for i in range(yh):
            for j in range(fwz):
                for k in range(pm[j]):
                    for b in range(bg):
                        for c in range(n):
                            for p in range(pz):
                                for d in range(pj): 
                                    # cc = cc+1
                                    for k1, v1 in dict1.items():
                                        if ('X' in k1):  
                                            if int(k1[1:]) <mm1:
                                                if cc == int(k1[1:]): 
                                                    yhdata.append([u+1,yhlist[i],fwzname[j],k+1,b+1,c+1,p+1,d+1,int(v1)])
                                                    print('养户编号:%s,服务站:%s,棚面:%d,磅:%d,时间单元:%d,品种:%d,品级:%d,数量:%d'%(yhlist[i],fwzname[j],k+1,b+1,c+1,p+1,d+1,int(v1)))
                                                    continue
                                    cc = cc+1      
    for i in range(kh):
        for j in range(fwz):
            for k in range(pm[j]):
                for b in range(bg):
                    for c in range(n):
                        for p in range(pz):
                            for d in range(pj): 
                                # cc = cc+1
                                for k1, v1 in dict1.items():
                                    if ('X' in k1):  
                                        if int(k1[1:]) >=mm1:
                                            if cc == int(k1[1:]): 
                                                khdata.append([khlist[i],fwzname[j],k+1,b+1,c+1,p+1,d+1,int(v1)])
                                                print('客户编号:%s,服务站:%s,棚面:%d,磅:%d,时间单元:%d,品种:%d,品级:%d,数量:%d'%(khlist[i],fwzname[j],k+1,b+1,c+1,p+1,d+1,int(v1)))
                                                continue
                                cc = cc+1
    print('******************************************************')
    # khdata = sorted(khdata, key=lambda khd: khd[len(khdata[0])-1])
    # yhdata = sorted(yhdata, key=lambda yhd: yhd[len(yhdata[0])-1])
    # print(khdata)
    # print(yhdata)
    # khdata.sort()
    # yhdata.sort()
    from tkinter import Tk,Label, Frame, StringVar, Entry, Button, Toplevel
    from tkinter.ttk import Treeview, Combobox
    import tkinter as tk
    #显示界面---------------------------------------------------------------------------------------------------------------------
    #设置窗口为居中
    #1.获得屏幕的宽高
    def get_screen_size(window):
        return window.winfo_screenwidth(), window.winfo_screenheight()
    def get_window_size(window):
        return window.winfo_reqwidth(), window.winfo_reqheight()
    #2.用屏幕宽高和geometry属性设置居中
    def center_window(root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def createKHPage():
        def destroyPage():
            khTk.destroy()
            tk.destroy()
        khTk = Tk()
        khTk.title("客户信息")
        khTk.maxsize(1500, 500)  # 设置窗口最大尺寸
        # 设置页面居中
        center_window(khTk, 960, 450)

        Label(khTk, text='客户信息    ', width=105, height=2,
            bg='#666666', fg="#F8F8FF", font=("黑体", 13)).grid(row=0, column=0)
        columns = ( '客户编号', '服务站', '棚面', '磅', '时间单元', '品种', '品级', '数量')
        khTable = Treeview(khTk, height=17, show="headings", columns=columns)
        khTable.column('客户编号', width=150, anchor='center')
        khTable.column('服务站', width=150, anchor='center')
        khTable.column('棚面', width=100, anchor='center')
        khTable.column('磅', width=100, anchor='center')
        khTable.column('时间单元', width=100, anchor='center')
        khTable.column('品种', width=100, anchor='center')
        khTable.column('品级', width=100, anchor='center')
        khTable.column('数量', width=150, anchor='center')
        khTable.heading('客户编号', text="客户编号")
        khTable.heading('服务站', text="服务站")
        khTable.heading('棚面', text="棚面")
        khTable.heading('磅', text="磅")
        khTable.heading('时间单元', text="时间单元")
        khTable.heading('品种', text="品种")
        khTable.heading('品级', text="品级")
        khTable.heading('数量', text="数量")
        for i in range(khdata.__len__()):
            khTable.insert('',i, values=(khdata[i][0],khdata[i][1],khdata[i][2],khdata[i][3],khdata[i][4],khdata[i][5],khdata[i][6],khdata[i][7]))
        khTable.grid(row=1, column=0)
        Button(khTk, text="关闭信息界面", width=15, command=destroyPage).grid(row=2, column=0, pady=10)


        khTk.mainloop()



    tk = Tk()
    tk.title("订单分派系统")
    tk.maxsize(1500, 500)  # 设置窗口最大尺寸
    #设置页面居中
    center_window(tk, 1050, 470)

    Label(tk, text='规划结果信息    ', width=117, height=2,
        bg='#666666', fg="#F8F8FF", font=("黑体", 13)).grid(row=0, column=0)
    columns = ('趟数', '养户编号', '服务站','棚面','磅','时间单元','品种','品级','数量')
    yhTable = Treeview(tk, height=17, show="headings", columns=columns)
    yhTable.column('趟数', width=100, anchor='center')
    yhTable.column('养户编号', width=150, anchor='center')
    yhTable.column('服务站', width=150, anchor='center')
    yhTable.column('棚面', width=100, anchor='center')
    yhTable.column('磅', width=100, anchor='center')
    yhTable.column('时间单元', width=100, anchor='center')
    yhTable.column('品种', width=100, anchor='center')
    yhTable.column('品级', width=100, anchor='center')
    yhTable.column('数量', width=150, anchor='center')
    yhTable.heading('趟数', text="趟数")
    yhTable.heading('养户编号', text="养户编号")
    yhTable.heading('服务站', text="服务站")
    yhTable.heading('棚面', text="棚面")
    yhTable.heading('磅', text="磅")
    yhTable.heading('时间单元', text="时间单元")
    yhTable.heading('品种', text="品种")
    yhTable.heading('品级', text="品级")
    yhTable.heading('数量', text="数量")
    for i in range(yhdata.__len__()):
        yhTable.insert('',i, values=(yhdata[i][0],yhdata[i][1],yhdata[i][2],yhdata[i][3],yhdata[i][4],yhdata[i][5],yhdata[i][6],yhdata[i][7],yhdata[i][8]))
    yhTable.grid(row=1, column=0)

    Button(tk, text="查看客户信息", width=15, command=createKHPage).grid(row=2, column=0, pady=10)

    tk.mainloop()


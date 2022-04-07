import sys,os
import time
import pulp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

from wenshi210701.PulpSolve import PulpSolve
from wenshi210701.AssignKh_model1 import AssKh
from wenshi210701.DealData import DealData
from wenshi210701.ConnDB import ConnDB

class AssYh():
    
    def __init__(self,args):
        self.args = args
    
    def objfun(self,args_obj): #针对棚面而言
        # KHNpp_obj-该棚面每个时间单元中每个客户需求品种品级情况
        # yhsl_obj 每个养户有品种品级鸡数量
        # temp-每个养户在每个棚面每个时间单元开栏标志（1：开栏；0：不开栏）
        # pz-品种 pj-品级
        # gap_pm-该棚面到每个养户的距离
        KHNpp_obj, yhsl_obj, pz, pj , gap_pm, temp = args_obj
        # temp_pm 每个养户在每个棚面是否开栏（1：开栏；0：不开栏）
        temp_pm = [[(1 if sum(temp[i][j][k] for k in range(len(temp[i][j])))>0 else 0) for j in range(len(temp[i]))]\
             for i in range(len(temp))]
        yh = len(yhsl_obj) #养户数
        N = len(KHNpp_obj) #时间单元数

        # 变量：每个养户在每个时间单元提供品种品级鸡的数量
        yhslpm = [[[[pulp.LpVariable('yhslpm_%d_%d_%d_%d' %(i,j,k,p), lowBound=0, cat=pulp.LpInteger)\
             for p in range(pj)] for k in range(pz)] for j in range(N)] for i in range(yh)]
        # 变量：每个养户在每个时间单元的出栏情况
        delta_pm = [[pulp.LpVariable('deltapm_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger)\
             for j in range(N)] for i in range(yh)]
        # 变量：每个养户的出栏情况
        beta_pm = [pulp.LpVariable('betapm_%d' %(i), lowBound=0, upBound=1, cat=pulp.LpInteger) for i in range(yh)]
        
        # 目标函数
        objective = pulp.lpSum([gap_pm[i] * pulp.lpSum([pulp.lpSum([pulp.lpSum([yhslpm[i][j][k][p] for p in range(pj)]) for k in range(pz)]) for j in range(N)]) for i in range(yh)])
        
        # 约束条件
        constraints = []
        for i in range(yh):
            constraints.append(beta_pm[i] <= pulp.lpSum([delta_pm[i][j] for j in range(N)]) <= N * beta_pm[i])
            for k in range(pz):
                for p in range(pj):
                    constraints.append(pulp.lpSum([yhslpm[i][j][k][p] for j in range(N)]) <= yhsl_obj[i][k][p])
            for j in range(N):
                constraints.append(200 * delta_pm[i][j] <= pulp.lpSum([pulp.lpSum([yhslpm[i][j][k][p] for p in range(pj)])\
                     for k in range(pz)]) <= 9000 * delta_pm[i][j])
        for j in range(N):
            for k in range(pz):
                for p in range(pj):
                    constraints.append(pulp.lpSum([yhslpm[i][j][k][p] for i in range(yh)]) == pulp.lpSum([KHNpp_obj[j][c][k][p] for c in range(len(KHNpp_obj[j]))]))      
        for i in range(yh):
            if sum([temp_pm[i][j] for j in range(len(temp_pm[i]))]) >= 2:
                constraints.append(beta_pm[i] == 0)
            # for k in range(N):
            #     if sum([(temp[i][j][k] if len(temp[i][j])>k else 0) for j in range(len(temp[i]))]) >= 1:
            #         constraints.append(delta_pm[i][k] == 0)
        
        return objective, constraints

    def assy(self):
        yh, pm_num, pz, pj, gap, KHNpp, KHNname, yhsl, yhAllname = self.args
        pm_n = [len(KHNname[i]) for i in range(pm_num)]
        gap_pm = [[0 for j in range(yh)] for i in range(pm_num)]
        # 每个养户在每个棚面每个时间单元开栏标志（1：开栏；0：不开栏）
        temp_ypn = [[[0 for k in range(pm_n[j])] for j in range(pm_num)] for i in range(yh)]
        for i in range(pm_num):
            for j in range(yh):
                gap_pm[i][j] = gap[j][i]
        # yh_detail 每个棚面养户分配细节
        yh_detail = [] #每个棚面每个养户每个时间单元送品种品级鸡数量
        pyhSL = [] #每个棚面每个养户送品种品级鸡数量
        yh_temp = [[[0 for k in range(pm_n[i])] for j in range(yh)] for i in range(pm_num)]
        yh_temp1 = [[0 for j in range(yh)] for i in range(pm_num)]

        for i in range(pm_num):
            time_start=time.time()
            print('开始进入棚面'+str(i+1))
            args_obj = KHNpp[i], yhsl, pz, pj, gap_pm[i],temp_ypn
            print('开始为棚面'+str(i+1)+'添加目标函数和约束')
            objective, constraints = self.objfun(args_obj)
            print('棚面'+str(i+1)+'添加目标函数和约束完成,开始进入求解模型')
            res = PulpSolve(solverName='CBC',solverTime=1200,isMsg=0).solver(objective, constraints)
            print('棚面'+str(i+1)+'求解模型运算完毕,开始提取关键数据')
            list_pm1 = [[[[0 for g4 in range(pj)] for g3 in range(pz)] for g2 in range(len(KHNname[i]))] for g1 in range(len(yhAllname))]
            for c in range(res.__len__()):
                if res[c][1]!=0:
                    if ('yhslpm' in res[c][0]):
                        name1 = res[c][0].strip().split("_")
                        list_pm1[int(name1[1])][int(name1[2])][int(name1[3])][int(name1[4])] = int(res[c][1])
                        
                        yhsl[int(name1[1])][int(name1[3])][int(name1[4])] -= int(res[c][1])
                        temp_ypn[int(name1[1])][i][int(name1[2])] = 1
                    if ('deltapm' in res[c][0]):
                        name2 = res[c][0].strip().split("_")
                        yh_temp[i][int(name2[1])][int(name2[2])] = int(res[c][1])
                    if ('betapm' in res[c][0]):
                        name3 = res[c][0].strip().split("_")
                        yh_temp1[i][int(name3[1])] = int(res[c][1])
            #将使用过的养户距离设为极小值
            sum_pm1 = [0 for g1 in range(len(list_pm1))]
            for g1 in range(len(list_pm1)):
                sum_pm1[g1] = sum([sum([sum([list_pm1[g1][g2][g3][g4] for g4 in range(pj)]) for g3 in range(pz)]) for g2 in range(len(list_pm1[g1]))])
                if sum_pm1[g1]>0:
                    for c in range(i+1,len(gap_pm)):
                        gap_pm[c][g1] = 0.001 * gap_pm[c][g1]
            pyhSL.append([[[sum([list_pm1[g1][g2][g3][g4] for g2 in range(len(list_pm1[g1]))]) for g4 in range(pj)] for g3 in range(pz)] for g1 in range(len(list_pm1))])
            yh_detail.append(list_pm1)
            print('棚面'+str(i+1)+'提取数据完成，该棚面执行完毕！')
            time_end=time.time()
            print('totally cost',time_end-time_start)
        return pyhSL,yh_detail, yh_temp, yhsl
    
if __name__ == "__main__":
    args_main,fpb_arg = DealData().deal()
    pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_jinum,maxNum,pz,pj,use_pzInd,pm_bg_num,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t, ad_val, kh_wait_tnum, yh_wait_tnum, car_max_num, s_m6_mt= args_main
    args_m1 = use_pzInd,pm_num,tj_num,use_pmidlist,pj,stime,pm_bg_num,maxNum, kh_tn, r_kh, r_supply_kh
    print('开始进入模型1')
    # pm_kh = AssKh(args_m1).assk()
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
    pyhSL, yh_detail, yh_temp, yhsl = AssYh(args).assy()
    print('模型2运行完成')
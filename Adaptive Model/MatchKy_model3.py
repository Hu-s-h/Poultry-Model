# 详细分配养户和对应客户 
import sys,os
import pulp
import xlwt
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

from wenshi210701.DealData import DealData
from wenshi210701.ConnDB import ConnDB
from wenshi210701.AssignYh_model2 import AssYh
from wenshi210701.AssignKh_model1 import AssKh
from wenshi210701.fwzPmIndOfName import fwzPmIndOfName
from wenshi210701.SaveKyResult import SaveKyResult
from wenshi210701.PulpSolve import PulpSolve
from wenshi210701.DetailKy_model4 import DetailKy_ky

class MatchKy():

    def __init__(self,args,fpb_arg):
        self.args = args
        self.fpb_arg = fpb_arg
    #养户切分车辆
    def TransCar(self):
        pyhSL = self.pyhSL #每个棚面每个养户送品种品级鸡数
        # self.carMaxNum
        car_yh_list = [[] for i in range(len(pyhSL))] #每个棚面每个车次养户送货信息
        for i in range(len(pyhSL)): #棚面
            for j in range(len(pyhSL[i])): #养户
                jsum = 0
                curr_num = 0
                car_yh_info = [j,[],[],[]] 
                for p in range(len(pyhSL[i][j])):
                    for d in range(len(pyhSL[i][j][p])):
                        if pyhSL[i][j][p][d]>0:
                            if jsum+pyhSL[i][j][p][d]>self.carMaxNum:
                                car_yh_info[1].append(p) 
                                car_yh_info[2].append(d) 
                                car_yh_info[3].append(self.carMaxNum-jsum)
                                curr_num = pyhSL[i][j][p][d] - self.carMaxNum + jsum
                                jsum = self.carMaxNum 
                            else:
                                car_yh_info[1].append(p) 
                                car_yh_info[2].append(d) 
                                car_yh_info[3].append(pyhSL[i][j][p][d])
                                jsum += pyhSL[i][j][p][d]
                            if jsum == self.carMaxNum:
                                jsum = 0
                                car_yh_list[i].append(car_yh_info)
                                car_yh_info = [j,[],[],[]]
                            while curr_num>0:
                                if jsum + curr_num >= self.carMaxNum:
                                    car_yh_info[1].append(p) 
                                    car_yh_info[2].append(d) 
                                    car_yh_info[3].append(self.carMaxNum-jsum)
                                    car_yh_list[i].append(car_yh_info)
                                    car_yh_info = [j,[],[],[]]
                                    curr_num = curr_num - self.carMaxNum + jsum
                                    jsum = 0
                                else:
                                    car_yh_info[1].append(p) 
                                    car_yh_info[2].append(d) 
                                    car_yh_info[3].append(curr_num)
                                    jsum += curr_num
                                    curr_num = 0
                if jsum>0:
                    car_yh_list[i].append(car_yh_info)
        # yhnc 每个棚面中每次出车送每个品种品级鸡的数目
        yhnc = [[[[0 for d in range(self.pj)] for p in range(self.pz)] for j in range(len(car_yh_list[i]))] for i in range(len(car_yh_list))]
        for i in range(len(car_yh_list)):
            for j in range(len(car_yh_list[i])):
                for k in range(len(car_yh_list[i][j][1])):
                    yhnc[i][j][car_yh_list[i][j][1][k]][car_yh_list[i][j][2][k]] += int(car_yh_list[i][j][3][k])
        return car_yh_list,yhnc
    #存储车辆信息而且返回车辆信息和每个养户每个棚面出车索引信息
    def saveCarDataToR(self,car_path):
        car_yh_list,yhnc = self.TransCar()
        yhAllname = self.yhAllname
        table_car = xlwt.Workbook()  # 创建一个excel
        sheet_car = table_car.add_sheet("车次表")
        title_car = ['养户名', '服务站名', '棚面名', '品种', '品级', '数量']
        i = 0
        for header in title_car:
            sheet_car.write(0, i, header)
            i += 1
        row_car = 1
        for i in range(len(car_yh_list)):#棚面
            for j in range(len(car_yh_list[i])):#车次
                sheet_car.write(row_car, 0, yhAllname[car_yh_list[i][j][0]]) #养户名
                sheet_car.write(row_car, 1, fwzPmIndOfName(self.fpb_arg,i,0).getpmOffwzName()) #服务站名
                sheet_car.write(row_car, 2, fwzPmIndOfName(self.fpb_arg,i,0).getpmIndofName()) #棚面名
                if len(car_yh_list[i][j][3])==1:
                    sheet_car.write(row_car, 3, str(self.pzAllname[car_yh_list[i][j][1][0]])) #品种
                    sheet_car.write(row_car, 4, str(self.pjAllname[car_yh_list[i][j][2][0]])) #品级
                    sheet_car.write(row_car, 5, int(car_yh_list[i][j][3][0])) #数量
                else:
                    sheet_car.write(row_car, 3, str([self.pzAllname[car_yh_list[i][j][1][p]] for p in range(len(car_yh_list[i][j][1]))])) #品种
                    sheet_car.write(row_car, 4, str([self.pjAllname[car_yh_list[i][j][2][d]] for d in range(len(car_yh_list[i][j][2]))])) #品级
                    sheet_car.write(row_car, 5, str(car_yh_list[i][j][3])) #数量
                row_car += 1
        if car_path == '':
            car_path = r'.\wenshi0306\output_tabel\车次信息表.xls'
        if os.path.exists(car_path):
            os.remove(car_path)
        table_car.save(car_path)
        print("车次信息表导出成功！")
        # yhnc-每个棚面中每次出车送每个品种品级鸡的数目
        # yhpCarNum-每个棚面每个养户出车索引
        # carpYhInd-每个棚面中每个车次对应养户索引
        yhCarNum = [[[] for j in range(len(yhAllname))] for i in range(len(yhnc))] 
        carpYhInd = [[] for i in range(len(yhnc))]
        for i in range(len(yhnc)):#棚面
            for j in range(len(yhnc[i])):#车次
                yhCarNum[i][car_yh_list[i][j][0]].append(j)
                carpYhInd[i].append(car_yh_list[i][j][0])
    
        return yhnc,yhCarNum,carpYhInd
    
    def objfun(self,arg_pky):
        # carSL-该棚面中每次出车送每个品种品级鸡的数目
        # yhCarNum-该棚面中每个养户出车索引
        # pCarYh-该棚面中每个车次对应养户索引
        # khSl-该棚面每个客户取鸡品种品级数量
        # pstime-该棚面开棚时间(分钟)
        # kh-该棚面客户数 cnum-该棚面车次数
        # Nt-每个棚面时间单元松弛变量
        # N-该棚面时间单元数
        # RS-该棚面每时间单元最大客户数
        # bgNum-该棚面磅数
        # bgEff-磅每个时间单元处理效率
        # khPt-该棚面每个客户预计取货时间单元
        # Nlen-磅处理时间单元长度（分钟）
        # khOffT-每个客户允许偏差时间单元
        # yhOffT-每个养户最早开始送货和最晚结束送货之间允许偏差时间单元
        # ktYn-该服务站每个养户已经开始卸货车辆卸货所属时间单元[[]]
        # ktYse-该服务站每个养户已知的最早开始卸货时间单元和最晚卸货时间单元
        carSL,yhCarNum,khSl,N,RS,bgNum,n_max_carnum,bi,bgEff,khPt,khOffT,yhOffT,ktYn,ktYse = arg_pky
        kh = len(khSl)
        cnum = len(carSL)
        pz = len(carSL[0])
        pj = len(carSL[0][0])
        t = [i for i in range(N)] #时间单元常数序列
        # 每个时间单元第car号车向棚面中运送第pz号品种第pj号品级的数量
        yhsl_nycpp = [[[[pulp.LpVariable('ynycpp_%d_%d_%d_%d' %(i,j,x,y), lowBound=0, cat=pulp.LpInteger)\
             for y in range(pj)] for x in range(pz)] for j in range(cnum)] for i in range(N)]
        #每个时间单元每个客户对品种品级数量需求
        khsl_nkpp = [[[[pulp.LpVariable('knkpp_%d_%d_%d_%d' %(i,j,k,z), lowBound=0, cat=pulp.LpInteger)\
             for z in range(pj)] for k in range(pz)] for j in range(kh)] for i in range(N)]
        # 表示第n个时间单元，第kh号客户进行装货的有无
        theta_kh = [[pulp.LpVariable('tkh_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger)\
             for j in range(kh)] for i in range(N)]
        # 表示第n个时间单元的第car辆车进行卸货的有无。
        theta_yh = [[pulp.LpVariable('tyh_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger)\
             for j in range(cnum)] for i in range(N)]
        # 第kh客户最早取货时间单元
        tkearly = [pulp.LpVariable('tkearly_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(kh)]
        # 第kh客户最晚取货时间单元
        tklate = [pulp.LpVariable('tklate_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(kh)]
        # 第car辆车最早送货时间单元 tcearly
        tcearly = [pulp.LpVariable('tcearly_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(cnum)]
        # 第car辆车最晚送货时间单元
        tclate = [pulp.LpVariable('tclate_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(cnum)]
        # 每个养户最早送货时间单元
        tyearly = [pulp.LpVariable('tyearly_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(len(yhCarNum))]
        # 每个养户最晚送货时间单元
        tylate = [pulp.LpVariable('tylate_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(len(yhCarNum))]
        # 目标函数
        objective = pulp.lpSum([((tklate[i]-tkearly[i])*bi if khPt[i]!=-1 else (tklate[i]-tkearly[i])) for i in range(kh)])#+pulp.lpSum([(tkearly[i]-khPt[i]) for i in range(kh)])
        # 约束条件
        constraints = []
        for j in range(kh):
            if khPt[j]!=-1:
                constraints.append(-1*khOffT<= tkearly[j]-khPt[j] <= khOffT)
            for p in range(pz):
                for d in range(pj):
                    constraints.append(pulp.lpSum([khsl_nkpp[i][j][p][d] for i in range(N)]) == khSl[j][p][d])
        for j in range(cnum):
            for p in range(pz):
                for d in range(pj):
                    constraints.append(pulp.lpSum([yhsl_nycpp[i][j][p][d] for i in range(N)]) == carSL[j][p][d])
        for i in range(N):
            constraints.append(pulp.lpSum([theta_kh[i][j] for j in range(kh)]) <= RS)
            constraints.append(pulp.lpSum([pulp.lpSum([pulp.lpSum([yhsl_nycpp[i][j][p][d] for d in range(pj)]) for p in range(pz)]) for j in range(cnum)]) <= bgNum * bgEff)
            for j in range(kh):
                constraints.append(theta_kh[i][j] <= pulp.lpSum([pulp.lpSum([khsl_nkpp[i][j][p][d] for d in range(pj)]) for p in range(pz)]) <= bgNum * bgEff * theta_kh[i][j])
                constraints.append(tkearly[j] <= tklate[j])
                constraints.append(tklate[j] >= t[i]*theta_kh[i][j])
                constraints.append(tkearly[j] <= (t[i]-(N+1))*theta_kh[i][j]+(N+1))
            for j in range(cnum):
                constraints.append(theta_yh[i][j] <= pulp.lpSum([pulp.lpSum([yhsl_nycpp[i][j][p][d] for d in range(pj)]) for p in range(pz)]) <= bgEff * theta_yh[i][j])
                constraints.append(tcearly[j] <= tclate[j])
                constraints.append(tclate[j] >= t[i]*theta_yh[i][j])
                constraints.append(tcearly[j] <= (t[i]-(N+1))*theta_yh[i][j]+(N+1))
                constraints.append(tclate[j] - tcearly[j] + 1 <= math.ceil(sum([sum([carSL[j][p][d] for d in range(pj)]) for p in range(pz)])/bgEff))
            for p in range(pz):
                for d in range(pj):
                    constraints.append(pulp.lpSum([yhsl_nycpp[i][j][p][d] for j in range(cnum)]) == pulp.lpSum([khsl_nkpp[i][j][p][d] for j in range(kh)]))
            for y in range(len(yhCarNum)):
                if len(yhCarNum[y])!=0:
                    constraints.append(pulp.lpSum([theta_yh[i][j] for j in yhCarNum[y]]) <= n_max_carnum)
                constraints.append(tyearly[y] <= tylate[y])
                for j in yhCarNum[y]:
                    constraints.append(tylate[y] >= t[i]*theta_yh[i][j])
                    constraints.append(tyearly[y] <= (t[i]-(N+1))*theta_yh[i][j]+(N+1))
                constraints.append(tylate[y] - tyearly[y] + 1 <= math.ceil(sum([sum([sum([carSL[j][p][d] for d in range(pj)]) for p in range(pz)]) for j in yhCarNum[y]])/bgEff + yhOffT))
        for y in range(len(ktYn)):
            for t in ktYn[y]:
                if t<N:
                    for j in yhCarNum[y]:
                        constraints.append(theta_yh[t][j]==0)
            # ktYse-该服务站每个养户已知的最早开始卸货时间和最晚卸货时间
            if ktYse[y][0]!=math.inf:
                at = math.ceil(sum([sum([sum([carSL[j][p][d] for d in range(pj)]) for p in range(pz)]) for j in yhCarNum[y]])/bgEff + yhOffT)
                constraints.append(-1*at <= tylate[y]-ktYse[y][0] <= at)
            if ktYse[y][1]!=-math.inf:
                at = math.ceil(sum([sum([sum([carSL[j][p][d] for d in range(pj)]) for p in range(pz)]) for j in yhCarNum[y]])/bgEff + yhOffT)
                constraints.append(-1*at <= tyearly[y]-ktYse[y][1] <= at)
                 
        return objective, constraints  
    
    def matchKy(self):
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
        max_t, pz, pj, yhAllname, pz_indToname, pjlist, pkhSl,pyhSl,carMaxNum,fwzPmInd,stList,Nt,Prs,pbgNum,n_max_carnum,bi,bgEff,Nlen,khPt,khOffT,yhOffT,fktYn,fktYse,car_path = self.args
        pzlist = [pz_indToname[i][1] for i in range(len(pz_indToname))]
        self.pyhSL = pyhSl #每个棚面每个养户送品种品级鸡数
        self.carMaxNum = carMaxNum
        self.pz = pz
        self.pj = pj
        self.yhAllname = yhAllname
        self.pzAllname = pzlist
        self.pjAllname = pjlist
        yhnc,yhCarNum,carpYhInd = self.saveCarDataToR(car_path)
        ynpp_res = [[] for i in range(len(pyhSl))]
        knpp_res = [[] for i in range(len(pkhSl))]
        ptLen = [[] for i in range(len(pkhSl))]
        ytEarly = [math.inf for j in range(len(yhAllname))]
        ytLate = [-math.inf for j in range(len(yhAllname))]
        ctEarly = [[math.inf for j in range(len(yhnc[i]))] for i in range(len(yhnc))]
        for i in range(len(fwzPmInd)): #服务站
            for j in fwzPmInd[i]: #棚面
                carSL = yhnc[j]
                pCarYh = carpYhInd[j]
                khSl = pkhSl[j]
                pstime = stList[j]
                RS = Prs[j]
                bgNum = pbgNum[j]
                ktYn = fktYn[i]
                ktYse = fktYse[i]
                N = math.ceil(sum([sum([sum([carSL[a][b][c] for c in range(len(carSL[a][b]))]) for b in range(len(carSL[a]))]) for a in range(len(carSL))])/(bgNum * bgEff))+Nt[j]
                ynpp_res[j] = [[[[0 for d in range(len(carSL[b][p]))] for p in range(len(carSL[b]))] for b in range(len(carSL))] for a in range(N)]
                knpp_res[j] = [[[[0 for d in range(len(khSl[b][p]))] for p in range(len(khSl[b]))] for b in range(len(khSl))] for a in range(N)]
                # print(len(knpp_res[j]),len(knpp_res[j][0]),len(knpp_res[j][0][0]),len(knpp_res[j][0][0][0]))
                ptLen[j].append([0 for a in range(N)])
                arg_pky = carSL,yhCarNum[j],khSl,N,RS,bgNum,n_max_carnum,bi,bgEff,khPt[j],khOffT,yhOffT,ktYn,ktYse
                print('开始对棚面'+str(j+1)+'添加约束')
                # 构建目标函数和约束
                objective, constraints = self.objfun(arg_pky)
                print('棚面'+str(j+1)+'添加约束完成,开始进入求解程序')
                # 求解带约束的目标规划
                # res = PulpSolve(solverName='CBC',solverTime=max_t,isMsg=1).solver(objective, constraints)
                res = PulpSolve(solverName='GUROBI',solverTime=max_t,isMsg=1,minGap=0.5).solver(objective, constraints)
                snum = 1
                while res == None:
                    snum += 1
                    max_t = math.ceil(1.5*max_t)
                    print('此次无解，正在进行下一次求解，重新分配求解时间'+str(max_t)+'秒')
                    res = PulpSolve(solverName='GUROBI',solverTime=max_t,isMsg=1,minGap=0.5).solver(objective, constraints)
                    if snum>=3:
                        print('多次求解失败无解，请检查约束是否合理或者参数调整是否过于苛刻')
                        break
                for a in range(res.__len__()):
                    # 每个时间单元第car号车向棚面中运送第pz号品种第pj号品级的数量
                    if ('ynycpp' in res[a][0]):
                        name1 = res[a][0].strip().split("_")
                        ynpp_res[j][int(name1[1])][int(name1[2])][int(name1[3])][int(name1[4])] = int(res[a][1])
                    #每个时间单元每个客户对品种品级数量需求
                    if ('knkpp' in res[a][0]):
                        name2 = res[a][0].strip().split("_")
                        knpp_res[j][int(name2[1])][int(name2[2])][int(name2[3])][int(name2[4])] = int(res[a][1])
                    # 每个养户最早送货时间
                    if ('tyearly' in res[a][0]):
                        name4 = res[a][0].strip().split("_")
                        ytEarly[int(name4[1])] = int(res[a][1])
                    # 每个养户最晚送货时间
                    if ('tylate' in res[a][0]):
                        name5 = res[a][0].strip().split("_")
                        ytLate[int(name5[1])] = int(res[a][1])
                    # 第car辆车最早送货时间
                    if ('tcearly' in res[a][0]):
                        name6 = res[a][0].strip().split("_")
                        ctEarly[j][int(name6[1])] = int(res[a][1])
                # fktYn-每个服务站每个养户已经开始卸货车辆卸货所属时间单元[[]]
                # fktYse-每个服务站每个养户已知的最早开始卸货时间和最晚卸货时间单元
                # pCarYh-棚面中每个车次对应养户索引
                for a in range(len(ctEarly[j])):
                    if abs(ctEarly[j][a]) != math.inf:
                        if ctEarly[j][a] not in fktYn[i][pCarYh[a]]:
                            fktYn[i][pCarYh[a]].append(ctEarly[j][a])
                for a in range(len(ytEarly)):
                    if ytEarly[a] != math.inf:
                        fktYse[i][a][0] = min(ytEarly[a],fktYse[i][a][0])
                    if ytLate[a] != -math.inf:
                        fktYse[i][a][1] = max(ytLate[a],fktYse[i][a][1])
        # ynpp_res-每个棚面每个时间单元每辆车次送品种品级鸡数
        # knpp_res-每个棚面每个时间单元每个客户取品种品级鸡数
        # fktYn-每个服务站每个养户已经开始卸货车辆卸货所属时间单元
        # fktYse-每个服务站每个养户已知的最早开始卸货时间和最晚卸货时间单元
        return ynpp_res, knpp_res, carpYhInd, fktYn, fktYse, yhCarNum

if __name__ == '__main__':
    args_main, fpb_arg = DealData().deal()
    pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_jinum,maxNum,pz,pj,use_pzInd,pbgNum,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t, ad_val, kh_wait_tnum, yh_wait_tnum, carMaxNum, s_m6_mt= args_main
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
    # use_pkhSl = [[] for i in range(len(pkhSl))]
    # print(pz,pj)
    # print(aaaaaaaaa)
    # for j in range(len(pkhSl))
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
    Nt = [ad_val*3 for i in range(len(pidList))]
    # Prs = rs_pm+20
    Prs = [rs_pm[i]+20 for i in range(len(rs_pm))]
    bgEff = int(maxNum/10)
    Nlen = 6
    one_max_t = 60
    # kh_temp #客户名与其对应取货时间
    khPt = [[math.floor((khPts[i][j]-stList[i])/Nlen) for j in range(len(khPts[i]))] for i in range(len(khPts))]
    khOffT = kh_wait_tnum*10
    # yhOffT = yh_wait_tnum
    yhOffT = 40
    fktYn = [[[] for j in range(yh)] for i in range(len(fidList))]
    fktYse = [[[math.inf,-math.inf] for j in range(yh)] for i in range(len(fidList))]
    car_path = r'.\wenshi210701\output_table\车次信息表.xlsx'
    kyinfo_path = r'.\wenshi210701\output_table\调配信息表.xlsx'
    kh_path = r'.\wenshi210701\output_tabel\客户信息表.xlsx'
    yh_path = r'.\wenshi210701\output_tabel\养户调度表.xlsx'
    ky_path = r'.\wenshi210701\output_table\调配结果信息表.xlsx' 
    new_path = r'.\wenshi210701\output_table\新调度结果表.xlsx'
    argsM3 = max_t, pz, pj, use_yhAllname, pz_indToname, pjlist,pkhSl,use_pyhSL,carMaxNum,fwzPmInd,stList,Nt,Prs,pbgNum,bgEff,Nlen,khPt,khOffT,yhOffT,fktYn,fktYse,car_path
    ynpp_res, knpp_res, carpYhInd,fktYn, fktYse = MatchKy(argsM3,fpb_arg).matchKy()
    pzlist = [pz_indToname[i][1] for i in range(pz)]
    ky_res = DetailKy_ky(knpp_res,ynpp_res,bgEff,one_max_t).detKy()
    args_ky = pkhName,carpYhInd,use_yhAllname,pz,pj,pzlist,pjlist,ynpp_res, knpp_res, fktYn, fktYse , ky_res, stList, pbgNum, carMaxNum, maxNum
    args_path = yh_path, ky_path, new_path,kyinfo_path
    SaveKyResult(args_ky,args_path,fpb_arg).saveResult()
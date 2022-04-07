#均化客户在每个棚面的品种及数量
from logging import error
import sys,os
import math
import pulp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

from wenshi210701.PulpSolve import PulpSolve

class avgkh():
    def __init__(self,args):
        self.args = args
    
    def objfun(self,obj_args):
        ban_khpm,appoint_khpm,sum_khpz,pm_num,tj_num,use_pmidlist,kh,pz,pj,kh_all_sum,pm_bg_num,maxNum = obj_args
        # 每个客户分配到棚面情况
        delta_ppp = [[[pulp.LpVariable('deppp_%d_%d_%d' %(i,j,k), lowBound=0, upBound=1, cat=pulp.LpInteger) for k in range(pj)] for j in range(pz)]\
             for i in range(pm_num)]
        omega_kp = [[pulp.LpVariable('omkp_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger) for j in range(pm_num)]\
             for i in range(kh)]
        num_kppp = [[[[pulp.LpVariable('numkppp_%d_%d_%d_%d' %(i,j,k,g), lowBound=0, cat=pulp.LpInteger) for g in range(pj)] for k in range(pz)]\
             for j in range(pm_num)] for i in range(kh)]
        # 目标函数
        # objective = self.my_sum([self.my_sum([self.my_sum([num_kpp[u][i][j]*delta_pp[i][j] for j in range(pz)]) for i in range(pm_num)]) for u in range(kh)])
        objective = pulp.lpSum([pulp.lpSum([pulp.lpSum([delta_ppp[i][j][k] for k in range(pj)]) for j in range(pz)]) for i in range(pm_num)])
        # 约束条件
        constraints = []
        for j in range(pm_num):
            constraints.append(pulp.lpSum([omega_kp[i][j] for i in range(kh)]) <= math.ceil(kh/pm_num)+tj_num)
        for i in range(kh):
            constraints.append(pulp.lpSum([omega_kp[i][j] for j in range(pm_num)]) == 1)         
            #棚面指定与棚面禁止
            if appoint_khpm[i]==-1:
                if ban_khpm[i]!=-1:
                    for x in range(len(ban_khpm[i])):
                        if ban_khpm[i][x] in use_pmidlist:
                            constraints.append(omega_kp[i][use_pmidlist.index(ban_khpm[i][x])] == 0)
            else:
                for j in range(pm_num):
                    if use_pmidlist[j] not in appoint_khpm[i]:
                        constraints.append(omega_kp[i][j] == 0)

            for j in range(pm_num): # kh_all_sum/9000/8
                constraints.append(omega_kp[i][j] <= pulp.lpSum([pulp.lpSum([num_kppp[i][j][k][g] for g in range(pj)]) for k in range(pz)]) <= 100000 * omega_kp[i][j])
                # constraints.append(sum(num_kpp[i][j][k] for k in range(pz)) <= 50000 * omega_kp[i][j])
                for k in range(pz):
                    for g in range(pj):
                    # constraints.append(num_kpp[i][j][k] >= omega_kp[i][j])
                    # constraints.append(omega_kp[i][j] <= num_kpp[i][j][k] <= 50000 * omega_kp[i][j])
                        constraints.append(delta_ppp[j][k][g] <= num_kppp[i][j][k][g] <= 100000 * delta_ppp[j][k][g])
        for i in range(kh):
            for k in range(pz):
                for g in range(pj):
                    constraints.append(pulp.lpSum([num_kppp[i][j][k][g] for j in range(pm_num)]) == sum_khpz[i][k][g])
        # print((round(kh_all_sum/(pm_num*maxNum))+0.05))
        for j in range(pm_num): # kh_all_sum/maxNum/pm_num 5.75 * 9000
            constraints.append(pulp.lpSum([pulp.lpSum([pulp.lpSum([num_kppp[i][j][k][g] for g in range(pj)]) for k in range(pz)]) for i in range(kh)]) <= round((kh_all_sum/(sum([pm_bg_num[cc] for cc in range(len(pm_bg_num))])*maxNum)+0.1) * pm_bg_num[j] * maxNum))
        return objective, constraints

    def avgs(self):
        #获取客户信息和棚面个数
        r_kh, r_supply_kh, pm_num, use_pmidlist, kh, pz, pj, pm_bg_num, maxNum,spind,tj_num = self.args
        # 所有客户需要鸡总数
        kh_all_sum = sum([sum([(int(r_kh[i][j].split(',')[0]) if r_kh[i][j] != '' and isinstance(r_kh[i][j],str) else 0) for j in range(spind,len(r_kh[i]))]) for i in range(len(r_kh))])
        print(kh_all_sum)   
        #每个客户禁止去的棚面
        ban_khpm = [(r_supply_kh[k][2].split(',') if (r_supply_kh[k][2] != '' and isinstance(r_supply_kh[k][2], str)) else -1) for k in range(len(r_supply_kh))]
        ban_khpm = [[int(ban_khpm[i][j]) for j in range(len(ban_khpm[i]))] if type(ban_khpm[i])==list else int(ban_khpm[i]) for i in range(len(ban_khpm))]
        #每个客户指定去的棚面
        appoint_khpm=[(r_supply_kh[k][3].split(',') if (r_supply_kh[k][3] != '' and isinstance(r_supply_kh[k][3], str)) else -1) for k in range(len(r_supply_kh))]
        # print(appoint_khpm)
        appoint_khpm = [(([int(appoint_khpm[i][j]) for j in range(len(appoint_khpm[i]))]) if type(appoint_khpm[i])==list else int(appoint_khpm[i])) for i in range(len(appoint_khpm))]
        #去除每个客户禁止去的棚面里面存在客户指定要去的棚面相同的值(二选其一)
        for k in range(len(ban_khpm)):
            if ban_khpm[k]!=-1:
                ban_khpm[k] = [ val for val in ban_khpm[k] if val not in appoint_khpm[k]]
        # #去除每个客户指定去的棚面里面存在客户禁止要去的棚面相同的值(二选其一)
        # for k in range(appoint_khpm):
            # if appoint_khpm[k]!=-1:
                # appoint_khpm[k] = [ val for val in appoint_khpm[k] if val not in ban_khpm[k]]

        #每个客户订单总量
        sum_kh = [sum([(int(r_kh[k][i].split(',')[0]) if (r_kh[k][i] != '' and isinstance(r_kh[k][i], str)) else 0)\
              for i in range(spind,len(r_kh[k]))]) for k in range(len(r_kh))]
        #每个客户订单要每个品种品级量
        sum_khpz = [[[((int(r_kh[k][i].split(',')[0]) if int(r_kh[k][i].split(',')[3])==j+1 else 0) if (r_kh[k][i] != '' and isinstance(r_kh[k][i], str)) else 0)\
             for j in range(pj)] for i in range(spind,len(r_kh[k]))] for k in range(len(r_kh))]
        #每个客户订单品种个数
        pz_kh = [sum([((1 if int(r_kh[k][i].split(',')[0])>0 else 0) if (r_kh[k][i] != '' and isinstance(r_kh[k][i], str))\
             else 0) for i in range(spind,len(r_kh[k]))]) for k in range(len(r_kh))]
        ##每个客户订单要每个品种品级情况
        temp_pz_kh = [[[((1 if int(r_kh[k][i].split(',')[0])>0 and int(r_kh[k][i].split(',')[3])==j+1 else 0) if (r_kh[k][i] != '' and isinstance(r_kh[k][i], str))\
             else 0) for j in range(pj)] for i in range(spind,len(r_kh[k]))] for k in range(len(r_kh))]
        # 构建目标函数和约束
        obj_args = ban_khpm,appoint_khpm,sum_khpz,pm_num,tj_num,use_pmidlist,kh,pz,pj,kh_all_sum,pm_bg_num,maxNum
        objective, constraints = self.objfun(obj_args)
        # 求解带约束的目标规划
        res = PulpSolve(solverName='CBC',solverTime=300,isMsg=0).solver(objective, constraints)
        solve_num = 0
        while res == None:
            solve_num = solve_num + 1
            if solve_num >= 10:
                error("求解无效，请检查数据是否有误或者格式是否正确")
            print('第'+str(solve_num)+'次求解无解，正在进行重新求解，请耐心等待(大概需要300秒)！！！')
            res = self.PulpSolve(solverName='CBC',solverTime=300,isMsg=0).solver(objective, constraints)
        # khinfo = [[[0 for k in range(pz)] for j in range(pm_num)] for i in range(kh)]
        khb = [[[0 for g in range(pj)] for k in range(pz)] for j in range(pm_num)]
        khpb = [[0 for k in range(pm_num)] for j in range(kh)]
        # numkp = [[[[0 for g in range(pj)] for k in range(pz)] for j in range(pm_num)] for i in range(kh)]
        khpsl = [[[[0 for g in range(pj)] for k in range(pz)] for j in range(kh)] for i in range(pm_num)]
        for i in range(res.__len__()):
            if res[i][1]!=0: 
                if ('deppp' in res[i][0]):
                    name2 = res[i][0].strip().split("_")
                    khb[int(name2[1])][int(name2[2])][int(name2[3])] = int(res[i][1])
                if ('omkp' in res[i][0]):
                    name3 = res[i][0].strip().split("_")
                    khpb[int(name3[1])][int(name3[2])] = int(res[i][1])
                if ('numkppp' in res[i][0]):
                    name4 = res[i][0].strip().split("_")
                    khpsl[int(name4[2])][int(name4[1])][int(name4[3])][int(name4[4])] = int(res[i][1])
                    # numkp[int(name4[1])][int(name4[2])][int(name4[3])][int(name4[4])] = int(res[i][1])
        # print('各棚面分配到的品级数为：',[sum(sum(khb[i][j][k] for k in range(pj)) for j in range(pz)) for i in range(pm_num)])
        # print('各棚面分配到的鸡数量为：',[sum(sum(sum(khpsl[i][j][k][g] for g in range(pj)) for k in range(pz)) for j in range(kh)) for i in range(pm_num)])
        # print('各客户分到棚面数：',[sum([khpb[i][j] for j in range(len(khpb[i]))]) for i in range(len(khpb))])
        # khp_detail = []
        # for i in range(pm_num):
        #     temp_kp = []
        #     for j in range(pz):
        #         for k in range(pj):
        #             if khb[i][j][k]!=0:
        #                 temp_kp.append('spc_'+str(j+1)+':pj_'+str(k+1))
        #     khp_detail.append(temp_kp)
        # for i in range(pm_num):
        #     print('棚面'+str(i+1)+'分配到的品种分别是：',khp_detail[i])
        # print(sum(khb[i][j] for j in range(pz)))
        return khpb,khpsl
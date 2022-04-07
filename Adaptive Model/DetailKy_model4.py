import pulp
from wenshi210701.PulpSolve import PulpSolve

class DetailKy_ky():

    def __init__(self,kh_detail,yh_detail,use_yhAllname,carpYhInd,bg_Eff,one_max_t):
        # yh_detail-每个棚面每个时间单元每辆车次送品种品级鸡数
        # kh_detail-每个棚面每个时间单元每个客户取品种品级鸡数
        # bg_Eff-时间单元磅效率
        # one_max_t-单个模型允许最大运行时间
        # use_yhAllname 参与出车的养户名
        # carpYhInd 每个棚面中每个车次对应养户索引
        # virYhInd 每个棚面虚拟养户对应的车次索引
        self.kh_detail = kh_detail
        self.yh_detail = yh_detail
        self.bg_Eff = bg_Eff
        self.t = one_max_t
        self.carpYhInd = carpYhInd
        self.virYhInd = [[] for i in range(len(self.carpYhInd))]
        for i in range(len(self.carpYhInd)):
            for j in range(len(self.carpYhInd[i])):
                if '虚拟养户' in use_yhAllname[self.carpYhInd[i][j]]:
                    self.virYhInd[i].append(j)
    # 该模型针对每个棚面每个时间单元下运行的
    def objfun(self,kpp_sl,ypp_sl):
        # kpp_sl-每个客户取品种品级鸡数
        # ypp_sl-每辆车次送品种品级鸡数
        # bg_Eff-时间单元磅效率
        #每个客户每个车次对品种品级数量需求
        kcpp = [[[[pulp.LpVariable('kcpp_%d_%d_%d_%d' %(i,j,k,z), lowBound=0, cat=pulp.LpInteger)\
             for z in range(len(kpp_sl[i][k]))] for k in range(len(kpp_sl[i]))] for j in range(len(ypp_sl))] for i in range(len(kpp_sl))]
        #每个客户对每个车次装鸡的有无
        delta_kc = [[pulp.LpVariable('dkc_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger)\
             for j in range(len(ypp_sl))] for i in range(len(kpp_sl))]
        # 目标函数
        objective = sum([sum([delta_kc[i][j] for j in range(len(ypp_sl))]) for i in range(len(kpp_sl))])
        # 约束条件
        constraints = []
        for i in range(len(kpp_sl)):
            for k in range(len(kpp_sl[i])):
                for z in range(len(kpp_sl[i][k])):
                    # 客户从所有车上取鸡的数量等于其要的量
                    constraints.append(sum([kcpp[i][j][k][z] for j in range(len(ypp_sl))]) == kpp_sl[i][k][z])
            for j in range(len(ypp_sl)):
                constraints.append(delta_kc[i][j] <=sum([sum([kcpp[i][j][k][z] for z in range(len(kpp_sl[i][k]))]) for k in range(len(kpp_sl[i]))]) <= self.bg_Eff * delta_kc[i][j])
        for j in range(len(ypp_sl)):
            for k in range(len(ypp_sl[j])):
                for z in range(len(ypp_sl[j][k])):
                    # 所有客户从该车上取鸡的数量等于该车配送的量
                    constraints.append(sum([kcpp[i][j][k][z] for i in range(len(kpp_sl))]) == ypp_sl[j][k][z])
        return objective, constraints
    
    def detKy(self):
        ky_res = [[] for pn in range(len(self.kh_detail))]
        vir_ky = [[] for pn in range(len(self.kh_detail))]
        print("开始处理结果，请稍后！")
        anum = 0
        for pn in range(len(self.kh_detail)):
            for sn in range(len(self.kh_detail[pn])):
                kpp_sl = self.kh_detail[pn][sn]
                ypp_sl = self.yh_detail[pn][sn]
                objective, constraints = self.objfun(kpp_sl,ypp_sl)
                res = PulpSolve(solverName='CBC',solverTime=self.t,isMsg=0).solver(objective, constraints)
                kcpp_res = [[[[0 for d in range(len(self.kh_detail[pn][sn][i][p]))] for p in range(len(self.kh_detail[pn][sn][i]))] for j in range(len(self.yh_detail[pn][sn]))] for i in range(len(self.kh_detail[pn][sn]))]
                for i in range(res.__len__()):
                    if res[i][1]!=0:
                        if ('kcpp' in res[i][0]):
                            name1 = res[i][0].strip().split("_")
                            if int(name1[2]) in self.virYhInd[pn]:
                                vir_ky[pn].append([sn,int(name1[1]),int(name1[2]),int(name1[3]),int(name1[4]),int(res[i][1])])
                            else:
                                kcpp_res[int(name1[1])][int(name1[2])][int(name1[3])][int(name1[4])] = int(res[i][1])
                ky_res[pn].append(kcpp_res)
                anum += 1
                print("正在处理，已处理"+str(anum)+"/"+str(sum([len(self.kh_detail[pn]) for pn in range(len(self.kh_detail))])))
        print("处理完成，开始导出结果表！")
        # ky_res 每个棚面 每个时间单元 每个客户 每辆车次 取品种 品级鸡数
        return ky_res, vir_ky
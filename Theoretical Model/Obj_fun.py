# 目标函数块
import pulp as pulp

class Obj_fun():
    def __init__(self,args,args1,args2):
        self.args = args
        self.args1 = args1
        self.args2 = args2
        # kh, yh, fwz, pm, bg, n, pz, pj, m, gap, t = self.args
        # mm1 = m * yh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        # mm2 = kh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        # self.variables = [pulp.LpVariable('X%d' % i, lowBound=0, cat=pulp.LpInteger) for i in range(0, mm1 + mm2)]
    def obj(self):
        kh, yh, fwz, pm, bg, n, pz, pj, m, gap, t = self.args
        mm1 = m * yh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        mm2 = kh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        variables = [pulp.LpVariable('X%d' % i, lowBound=0, cat=pulp.LpInteger) for i in range(0, mm1 + mm2)]
        czh = [[[[[[[[pulp.LpVariable('czh_%d_%d_%d_%d_%d_%d_%d_%d' %(u,i,j,k,b,c,p,d), lowBound=0, upBound=1, cat=pulp.LpInteger)  for d in range(pj)]\
             for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])]\
                 for j in range(fwz)] for i in range(yh)] for u in range(m)]
        cc = [[[[[[pulp.LpVariable('cc_%d_%d_%d_%d_%d_%d' %(u,i,j,k,b,c), lowBound=0, upBound=1, cat=pulp.LpInteger) for c in range(n)]\
                  for b in range(bg)] for k in range(pm[j])] for j in range(fwz)]\
               for i in range(yh)] for u in range(m)]
        cc1 = [pulp.LpVariable('cc1_%d' %(u), lowBound=0, upBound=1, cat=pulp.LpInteger) for u in range(m)]
        psi = [[pulp.LpVariable('psi_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger) for j in range(fwz)] for i in range(yh)]
        delta = [[[[[[[pulp.LpVariable('delta_%d_%d_%d_%d_%d_%d_%d' %(i,j,k,b,c,p,d), lowBound=0, upBound=1, cat=pulp.LpInteger)\
             for d in range(pj)] for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])]\
                  for j in range(fwz)] for i in range(kh)]
        delta1 = [[[[[pulp.LpVariable('delta1_%d_%d_%d_%d_%d' %(i,j,k,c,p), lowBound=0, upBound=1, cat=pulp.LpInteger) for p in range(pz)] \
                    for c in range(n)] for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        chi = [[[[pulp.LpVariable('chi_%d_%d_%d_%d' %(i,j,k,c), lowBound=0, upBound=1, cat=pulp.LpInteger) for c in range(n)] \
                            for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        w = [[[pulp.LpVariable('w_%d_%d_%d' %(i,j,p), lowBound=0, upBound=1, cat=pulp.LpInteger) for p in range(pz)]\
             for j in range(fwz)] for i in range(kh)]
        omega = [[pulp.LpVariable('omega_%d_%d' %(i,j), lowBound=0, upBound=1, cat=pulp.LpInteger) for j in range(fwz)] for i in
                            range(kh)]
        # tkhon = [pulp.LpVariable('tkhon_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(kh)]
        # tkhend = [pulp.LpVariable('tkhend_%d' %(i), lowBound=0, cat=pulp.LpInteger) for i in range(kh)]
        hwsl = [[[[[[[[variables[u * yh * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj +\
                                 i * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj +\
                                            sum(pm[o] for o in range(0,j)) * bg * n * pz * pj + k * bg * n * pz * pj +\
                                            b * n * pz * pj + c * pz * pj + p * pj + d] for d in range(pj)]\
                                 for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])]\
                             for j in range(fwz)] for i in range(yh)] for u in range(m)]
        x1 = [[[[[[[variables[mm1 + i * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj\
                             + sum(pm[o] for o in range(0, j)) * bg * n * pz * pj + k * bg * n * pz * pj\
                             + b * n * pz * pj +  c * pz * pj + p * pj + d] for d in range(pj)] for p in range(pz)]\
                 for c in range(n)] for b in range(bg)] for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        
        kzsl = [[(sum(sum(sum(sum((2000 * cc[u][i][j][k][b][c] - sum(sum(hwsl[u][i][j][k][b][c][p][d]\
                                                                         for d in range(pj)) for p in range(pz)))\
                                  for c in range(n)) for b in range(bg)) for k in range(pm[j])) for u in range(m)))\
                 for j in range(fwz)] for i in range(yh)]
        y1 = [[[[[[[sum(hwsl[u][i][j][k][b][c][p][d] for u in range(m)) for d in range(pj)]\
                   for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])]\
               for j in range(fwz)] for i in range(yh)]
        y = [[[(sum(sum(sum(sum(y1[i][j][k][b][c][p][d] for c in range(n))\
                            for b in range(bg)) for k in range(pm[j])) for j in range(fwz)))\
               for d in range(pj)] for p in range(pz)] for i in range(yh)]
        x = [[[(sum(sum(sum(sum(x1[i][j][k][b][c][p][d] for c in range(n)) for b in range(bg)) for k in range(pm[j])) \
                               for j in range(fwz))) for d in range(pj)] for p in range(pz)] for i in range(kh)]

        tzh = [[[[[(delta1[i][j][k][c][p] * (c + 3) * t) for p in range(pz)] for c in range(n)] for k in range(pm[j])] \
             for j in range(fwz)] for i in range(kh)]


        # tkhon = [min([min([min([min([(tzh[i][j][k][c][p] if (tzh[i][j][k][c][p]!=0) else float('inf')) \
        #                         for p in range(pz)]) for c in range(n)]) for k in range(pm[j])]) for j in range(fwz)])\
        #          for i in range(kh)]

        # tkhend = [max([max([max([max([tzh[i][j][k][c][p] for p in range(pz)]) for c in range(n)]) \
        #                                for k in range(pm[j])]) for j in range(fwz)]) for i in range(kh)]
        cost1 = sum(sum((kzsl[i][j] * gap[i][j]) for j in range(fwz)) for i in range(yh))
        # twait = sum((tkhend[i] - tkhon[i]) for i in range(kh))
        objective = 0.7 *cost1 #+ 0.3 * twait

        # theta1 某一客户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta2 某一客户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta3 所有客户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta4 所有客户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta5 某一养户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta6 某一养户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta7 所有养户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta8 所有养户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        theta1, theta2, theta3, theta4,theta5, theta6, theta7, theta8 = self.args1
        # kh-客户数 yh-养户 fwz-服务站数 pm-棚面数 bg-磅数 n-时间段数 pz-鸡品种数 pj-品级数(大,中,小) t-时间单元长度（分钟,t取 60）（已知）
        # m-最大出车趟数,估算设定为 600 以上即可 gap-养户到服务站的距离(已知)
        # sl-客户对鸡品种品级的订单数量 list类型-三层嵌套模型 （已知）
        # ysl-养户对鸡品种品级的供给数量 list类型-三层嵌套模型（已知）
        kh, yh, fwz, pm, bg, n, pz, pj, m, t, khon, khend, sl, ysl = self.args2
        # sl_kh 客户对鸡的订单数量 list类型-一层嵌套模型 （已知）
        # sl_khpz 客户对鸡品种的订单数量 list类型-两层嵌套模型 （已知）
        # sl_pz 各种鸡品种在所有客户中的订单数量 list类型-一层嵌套模型 （已知）
        # ss1 所有客户所有品种所有品级鸡总数量 整数值（已知）
        sl_kh = [0 for i in range(kh)]
        sl_khpz = [[0 for j in range(pz)] for i in range(kh)]
        sl_pz = [0 for i in range(pz)]
        for i in range(kh):
            sl_kh[i] = sum(sum(sl[i][j][k] for k in range(pj)) for j in range(pz))
            for j in range(pz):
                sl_khpz[i][j] = sum(sl[i][j][k] for k in range(pj))
        for j in range(pz):
            sl_pz[j] = sum(sum(sl[i][j][k] for k in range(pj)) for i in range(kh))
        ssl = sum(sum(sum(sl[i][j][k] for k in range(pj)) for j in range(pz)) for i in range(kh))
        # sl_yh 养户对鸡的供给数量 list类型-一层嵌套模型 （已知）
        # sl_yhpz 养户户对鸡品种的供给数量 list类型-两层嵌套模型 （已知）
        # ysl_pz 各种鸡品种在所有养户中的供给数量 list类型-一层嵌套模型 （已知）
        # ss1 所有养户所有品种所有品级鸡总数量--整数值（已知）
        sl_yh = [0 for i in range(yh)]
        sl_yhpz = [[0 for j in range(pz)] for i in range(yh)]
        ysl_pz = [0 for i in range(pz)]
        for i in range(yh):
            sl_yh[i] = sum(sum(ysl[i][j][k] for k in range(pj)) for j in range(pz))
            for j in range(pz):
                sl_yhpz[i][j] = sum(ysl[i][j][k] for k in range(pj))
        for j in range(pz):
            ysl_pz[j] = sum(sum(ysl[i][j][k] for k in range(pj)) for i in range(yh))
        sysl = sum(sum(sum(ysl[i][j][k] for k in range(pj)) for j in range(pz)) for i in range(yh))
        # 约束条件
        constraints = []
        constraints.append(sum(sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
                               for i in range(kh)) <= (1 + theta4) * ssl)
        constraints.append(sum(sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
                               for i in range(kh)) >= (1 - theta4) * ssl)
        #添加时间约束
        # kh  fwz pm bg n pz pj
        for a in range(kh):
            n1 = int((khon[a] -180)/60)
            n2 = int((khend[a] -180)/60)
            for b in range(fwz):
                for c in range(pm[b]):
                    for d in range(bg):
                        for f in range(pz):
                            for g in range(pj):
                                for e in range(n1):
                                    constraints.append(x1[a][b][c][d][e][f][g] == 0)
                                for e in range(n2+1,n):
                                    constraints.append(x1[a][b][c][d][e][f][g] == 0)

        for i in range(kh):
            # 客户的所有品种的鸡的实际装货量可在客户对所有品种的鸡的订单量的theta2的变化范围内
            constraints.append(sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
                               >= (1 - theta2) * sl_kh[i])
            constraints.append(sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
                               <= (1 + theta2) * sl_kh[i])
            for j in range(pz):
                # 客户对鸡品种的实际装货量可在客户对该品种的鸡的订单量的theta1的变化范围内
                constraints.append(sum(x[i][j][k] for k in range(pj)) >= (1-theta1)*sl_khpz[i][j])
                constraints.append(sum(x[i][j][k] for k in range(pj)) <= (1+theta1)*sl_khpz[i][j])
                # 客户对每个品种大鸡实际装货量不得少于该客户对每个品种大鸡订单量
                constraints.append(x[i][j][0] >= sl[i][j][0])
        for j in range(pz):
            # 所有客户的鸡品种的实际装货量可在所有客户的该品种的鸡的总订单量的theta3的变化范围内
            constraints.append(sum(sum(x[i][j][k] for k in range(pj)) for i in range(kh)) >= (1-theta3)*sl_pz[j])
            constraints.append(sum(sum(x[i][j][k] for k in range(pj)) for i in range(kh)) <= (1+theta3)*sl_pz[j])
        # 所有养户对所有品种的鸡的实际供给量处于所有养户对所有品种的鸡的订单供给量的theta8的变化范围内
        constraints.append(sum(sum(sum(y[i][j][k] for k in range(pj)) for j in range(pz)) \
                               for i in range(yh)) <= (1 + theta8) * sysl)
        for i in range(yh):
            # 养户对所有品种的鸡的实际供给量处于养户对所有品种的鸡的订单供给量的theta6的变化范围内
            constraints.append(sum(sum(y[i][j][k] for k in range(pj)) for j in range(pz)) <= (1+theta6)*sl_yh[i])
            for j in range(pz):
                # 养户对鸡品种的实际供给量处于养户对鸡品种的订单供给量的theta5的变化范围内
                constraints.append(sum(y[i][j][k] for k in range(pj)) <= (1+theta5)*sl_yhpz[i][j])
        # 所有养户对鸡品种的实际供给量处于所有养户对鸡品种的订单供给量的theta7的变化范围内
        for j in range(pz):
            constraints.append(sum(sum(y[i][j][k] for k in range(pj)) for i in range(yh)) <= (1+theta7)*ysl_pz[j])
        for j in range(fwz):
            for k in range(pm[j]):
                for b in range(bg):
                    for c in range(n):
                        for p in range(pz):
                            for d in range(pj):
                                # 单位时间内在服务站内的供求平衡
                                constraints.append(sum(x1[i][j][k][b][c][p][d] for i in range(kh))\
                                     == sum(y1[i][j][k][b][c][p][d] for i in range(yh)))
        for i in range(kh):
            for j in range(fwz):
                constraints.append(sum(w[i][j][p] for p in range(pz)) >= omega[i][j])
                constraints.append(sum(w[i][j][p] for p in range(pz)) <= 1000*omega[i][j])
                for p in range(pz):
                    constraints.append(sum(sum(delta1[i][j][k][c][p] for c in range(n)) for k in range(pm[j]))>= w[i][j][p])
                    constraints.append(sum(sum(delta1[i][j][k][c][p] for c in range(n)) for k in range(pm[j]))<= 4000*w[i][j][p])
                for k in range(pm[j]):
                    
                    for c in range(n):
                        constraints.append(sum(delta1[i][j][k][c][p] for p in range(pz)) >= chi[i][j][k][c])
                        constraints.append(sum(delta1[i][j][k][c][p] for p in range(pz)) <= 3000*chi[i][j][k][c])
                        for p in range(pz):
                            constraints.append(sum(sum(x1[i][j][k][b][c][p][d] for d in range(pj)) for b in range(bg))\
                                 >= delta1[i][j][k][c][p])
                            constraints.append(sum(sum(x1[i][j][k][b][c][p][d] for d in range(pj)) for b in range(bg))\
                                 <= 300000*delta1[i][j][k][c][p])
                            
        # 客户在单位时间单元中最多只能去某个服务站的某个棚面进行装货
        # 客户在服务站棚面时间段装鸡品种的装货情况（0-1变量 0：装货 1：不装货）delta-->list类型，五层嵌套(客户->服务站->棚面->时间段->品种)
        # 客户在服务站棚面的时间段装货情况（0-1变量 0：装货 1：不装货）chi-->list类型，四层嵌套(客户->服务站->棚面->时间段)
        # 客户在服务站装货情况（0-1变量 0：装货 1：不装货） omega-->list类型，两层嵌套(养户->服务站)
        # 实际开始装货的最早时间 tkhon-->list类型 一层循环[客户]
        # 实际装完货的最晚时间 tkhend-->list类型 一层循环[客户]
        # 客户订单预计最早开始装货时间 khon-->list类型 一层循环[客户](已知)
        # 客户订单预计最晚装完货时间 khend-->list类型 一层循环[客户](已知)
        for i in range(kh):
            constraints.append(sum(omega[i][j] for j in range(fwz)) >= 0)
            constraints.append(sum(omega[i][j] for j in range(fwz)) <= 1)
            # constraints.append(tkhon[i] >= khon[i])
            # constraints.append(tkhon[i] <= tkhend[i])
            # constraints.append(tkhend[i] <= khend[i])
            for j in range(fwz):
                for k in range(pm[j]):
                    for b in range(bg):
                        for c in range(n):
                            for p in range(pz):
                                for d in range(pj):
                                    constraints.append(x1[i][j][k][b][c][p][d] >= delta[i][j][k][b][c][p][d])
                                    constraints.append(x1[i][j][k][b][c][p][d] <= 2000*delta[i][j][k][b][c][p][d])
                                    
            for c in range(n):
                # 每号客户在某个时间单元内只能到达某号服务站的某个棚面进行装货
                constraints.append(sum(sum(chi[i][j][k][c] for k in range(pm[j])) for j in range(fwz)) >= 0)
                constraints.append(sum(sum(chi[i][j][k][c] for k in range(pm[j])) for j in range(fwz)) <= 1)
        for j in range(fwz):
            for k in range(pm[j]):
                for b in range(bg):
                    for c in range(n):
                        # 加工能力的限制即任意一个服务站的任意个棚面的任意个磅在每个工作单元中
                        # 对所有养户的所有品种所有品级的鸡加工的总量不超过单位工作单元的最大处理量（t取 60）
                        constraints.append(sum(sum(sum(y1[i][j][k][b][c][p][d] for d in range(pj))\
                             for p in range(pz)) for i in range(yh)) <= 2300*t/60)
        # cc-第m趟车从第 fwz号服务站到第yh号养户在第n个时间单元到第pm号棚面的第bg号磅卸所有品种所有品级的鸡的出车情况(0-1变量 1-出车 0-不出车)
        # cc-->list类型 六层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元]）
        # 第 m趟车的出车情况(0-1变量 1-出车 0-不出车)-cc1-->list类型 一层（[车趟数]）
        # czh-第m趟车从第fwz号服务站到第yh号养户在第n个时间单元到第pm号棚面的第bg号磅卸第pz号品种pj品级的鸡后货的载货情况(0-1变量 1-载货 0-不载货)
        # czh-->list类型 八层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元,品种,品级]）
        # hwsl-第m趟车从第fwz号服务站到第yh号养户在第n个时间单元回到第fwz号服务站的第pm号棚面的第bg号磅卸第pz种品种 pj 品级的鸡的卸货数量
        # hwsl-->list类型 八层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元,品种,品级]）
        # 第fwz号服务站是否派出车辆到第yh号客户-psi-->list类型 两层嵌套（[养户,服务站]）
        # zts-总趟数
        # 第fwz个服务站到第yh养户的派车的所有趟数的总空置数-kzsl-->list类型 两层嵌套（[养户,服务站]）
        for u in range(m):
            # 同一趟车只能在某个时间单元内从某个服务站去某个养户回到服务站的某个棚面的某个磅进行卸货
            # cons.append({'type': 'eq', 'fun':lambda hwsl:cc1[u] - sum(sum(sum(sum(sum(cc[u][i][j][k][b][c]\
            #      for c in range(n)) for b in range(bg)) for k in range(pm[j])) for j in range(fwz)) for i in range(yh))})
            constraints.append(sum(sum(sum(sum(sum(cc[u][i][j][k][b][c] for c in range(n))\
                 for b in range(bg)) for k in range(pm[j])) for j in range(fwz)) for i in range(yh)) >= cc1[u])
            constraints.append(sum(sum(sum(sum(sum(cc[u][i][j][k][b][c] for c in range(n))\
                 for b in range(bg)) for k in range(pm[j])) for j in range(fwz)) for i in range(yh)) <= 30000*cc1[u])
            for i in range(yh):
                for j in range(fwz):
                    for k in range(pm[j]):
                        for b in range(bg):
                            for c in range(n):
                                # 每趟车的载重数量控制在1500~2000只
                                constraints.append(sum(sum(hwsl[u][i][j][k][b][c][p][d] \
                                        for d in range(pj)) for p in range(pz)) >= 1500 * cc[u][i][j][k][b][c])
                                constraints.append(sum(sum(hwsl[u][i][j][k][b][c][p][d] \
                                        for d in range(pj)) for p in range(pz)) <= 2000 * cc[u][i][j][k][b][c])
                                constraints.append(sum(sum(czh[u][i][j][k][b][c][p][d] \
                                        for d in range(pj)) for p in range(pz)) >= cc[u][i][j][k][b][c])
                                constraints.append(sum(sum(czh[u][i][j][k][b][c][p][d] \
                                        for d in range(pj)) for p in range(pz)) <= 3000*cc[u][i][j][k][b][c])
                                for p in range(pz):
                                    for d in range(pj):
                                        constraints.append(czh[u][i][j][k][b][c][p][d] <= hwsl[u][i][j][k][b][c][p][d])
                                        constraints.append( hwsl[u][i][j][k][b][c][p][d] <= 3000* czh[u][i][j][k][b][c][p][d])
        # zts = sum(cc1[u] for u in range(m))
        for i in range(yh):
            # 一个养户只能去一个服务站卸货（一个养户只能从一个服务站调车前往）
            constraints.append(sum(psi[i][j] for j in range(fwz)) >= 0)
            constraints.append(sum(psi[i][j] for j in range(fwz)) <= 1)
            constraints.append(sum(sum(sum(sum(cc[u][i][j][k][b][c] for c in range(n))\
                 for b in range(bg)) for k in range(pm[j])) for u in range(m)) >= psi[i][j])
            constraints.append(sum(sum(sum(sum(cc[u][i][j][k][b][c] for c in range(n))\
                 for b in range(bg)) for k in range(pm[j])) for u in range(m)) <= 30000000*psi[i][j])
        
        # for u in range(m):
        #     for i in range(yh):
        #         for j in range(fwz):
        #             for k in range(pm[j]):
        #                 for b in range(bg):
        #                     for c in range(n):
        #                         for p in range(pz):
        #                             for d in range(pj):
                                        
        #                                 constraints.append(-10 <= hwsl[u][i][j][k][b][c][p][d] <=30)
        # ss = [(variables[i+1] - variables[i] - 1) for i in range(mm1+mm2-1)]
        # for i in range(mm1+mm2):
        #     constraints.append(variables[i] <= 60)
        #     constraints.append(variables[i]>=1)
        # constraints.append(sum(variables[i] for i in range(mm1+mm2)) <= 100)
        # for i in range(mm1+mm2-1):
        #     constraints.append(ss[i] >= 0)
        return objective,constraints#,constraints1,constraints2
    def con(self):
        # theta1 某一客户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta2 某一客户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta3 所有客户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta4 所有客户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta5 某一养户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta6 某一养户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta7 所有养户的某一品种的鸡实际装货量的上下浮动百分比 （已知）
        # theta8 所有养户的所有品种的鸡实际装货量的上下浮动百分比 （已知）
        theta1, theta2, theta3, theta4,theta5, theta6, theta7, theta8 = self.args1
        # kh-客户数 yh-养户 fwz-服务站数 pm-棚面数 bg-磅数 n-时间段数 pz-鸡品种数 pj-品级数(大,中,小) t-时间单元长度（分钟,t取 60）（已知）
        # m-最大出车趟数,估算设定为 600 以上即可 gap-养户到服务站的距离(已知)
        # sl-客户对鸡品种品级的订单数量 list类型-三层嵌套模型 （已知）
        # ysl-养户对鸡品种品级的供给数量 list类型-三层嵌套模型（已知）
        kh, yh, fwz, pm, bg, n, pz, pj, m, t, khon, khend, sl, ysl = self.args2
        # sl_kh 客户对鸡的订单数量 list类型-一层嵌套模型 （已知）
        # sl_khpz 客户对鸡品种的订单数量 list类型-两层嵌套模型 （已知）
        # sl_pz 各种鸡品种在所有客户中的订单数量 list类型-一层嵌套模型 （已知）
        # ss1 所有客户所有品种所有品级鸡总数量 整数值（已知）
        sl_kh = [0 for i in range(kh)]
        sl_khpz = [[0 for j in range(pz)] for i in range(kh)]
        sl_pz = [0 for i in range(pz)]
        for i in range(kh):
            sl_kh[i] = sum(sum(sl[i][j][k] for k in range(pj)) for j in range(pz))
            for j in range(pz):
                sl_khpz[i][j] = sum(sl[i][j][k] for k in range(pj))
        for j in range(pz):
            sl_pz[j] = sum(sum(sl[i][j][k] for k in range(pj)) for i in range(kh))
        ssl = sum(sum(sum(sl[i][j][k] for k in range(pj)) for j in range(pz)) for i in range(kh))
        # sl_yh 养户对鸡的供给数量 list类型-一层嵌套模型 （已知）
        # sl_yhpz 养户户对鸡品种的供给数量 list类型-两层嵌套模型 （已知）
        # ysl_pz 各种鸡品种在所有养户中的供给数量 list类型-一层嵌套模型 （已知）
        # ss1 所有养户所有品种所有品级鸡总数量--整数值（已知）
        sl_yh = [0 for i in range(yh)]
        sl_yhpz = [[0 for j in range(pz)] for i in range(yh)]
        ysl_pz = [0 for i in range(pz)]
        for i in range(yh):
            sl_yh[i] = sum(sum(ysl[i][j][k] for k in range(pj)) for j in range(pz))
            for j in range(pz):
                sl_yhpz[i][j] = sum(ysl[i][j][k] for k in range(pj))
        for j in range(pz):
            ysl_pz[j] = sum(sum(ysl[i][j][k] for k in range(pj)) for i in range(yh))
        sysl = sum(sum(sum(ysl[i][j][k] for k in range(pj)) for j in range(pz)) for i in range(yh))

        mm1 = m * yh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        mm2 = kh * sum(pm[i] for i in range(fwz)) * bg * n * pz * pj
        hwsl = [[[[[[[[self.variables[u * yh * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj + \
                                      i * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj + \
                                      sum(pm[o] for o in range(0, j)) * bg * n * pz * pj + k * bg * n * pz * pj + \
                                      b * n * pz * pj + c * pz * pj + p * pj + d] for d in range(pj)] \
                      for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])] \
                  for j in range(fwz)] for i in range(yh)] for u in range(m)]
        x1 = [[[[[[[self.variables[mm1 + i * sum(pm[o] for o in range(fwz)) * bg * n * pz * pj \
                                   + sum(pm[o] for o in range(0, j)) * bg * n * pz * pj + k * bg * n * pz * pj \
                                   + b * n * pz * pj + c * pz * pj + p * pj + d] for d in range(pj)] for p in range(pz)] \
                  for c in range(n)] for b in range(bg)] for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        czh = [[[[[[[[(1 if hwsl[u][i][j][k][b][c][p][d] != 0 else 0) for d in range(pj)] \
                     for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])] \
                 for j in range(fwz)] for i in range(yh)] for u in range(m)]
        cc = [[[[[[(1 if sum(sum(czh[u][i][j][k][b][c][p][d] for d in range(pj)) \
                             for p in range(pz)) != 0 else 0) for c in range(n)] \
                  for b in range(bg)] for k in range(pm[j])] for j in range(fwz)] \
               for i in range(yh)] for u in range(m)]
        cc1 = [(1 if (sum(sum(sum(sum(sum(cc[u][i][j][k][b][c] for c in range(n)) for b in range(bg)) \
                                  for k in range(pm[j])) for j in range(fwz)) \
                          for i in range(yh))) != 0 else 0) for u in range(m)]
        psi = [[(1 if sum(sum(sum(sum(sum(sum(hwsl[u][i][j][k][b][c][p][d] for d in range(pj)) for p in range(pz)) \
                                      for c in range(n)) for b in range(bg)) for k in range(pm[j])) \
                          for u in range(m)) != 0 else 0) for j in range(fwz)] for i in range(yh)]
        kzsl = [[(sum(sum(sum(sum((2000 * cc[u][i][j][k][b][c] - sum(sum(hwsl[u][i][j][k][b][c][p][d] \
                                                                         for d in range(pj)) for p in range(pz))) \
                                  for c in range(n)) for b in range(bg)) for k in range(pm[j])) for u in range(m))) \
                 for j in range(fwz)] for i in range(yh)]
        y1 = [[[[[[[sum(hwsl[u][i][j][k][b][c][p][d] for u in range(m)) for d in range(pj)] \
                   for p in range(pz)] for c in range(n)] for b in range(bg)] for k in range(pm[j])] \
               for j in range(fwz)] for i in range(yh)]
        y = [[[(sum(sum(sum(sum(y1[i][j][k][b][c][p][d] for c in range(n)) \
                            for b in range(bg)) for k in range(pm[j])) for j in range(fwz))) \
               for d in range(pj)] for p in range(pz)] for i in range(yh)]
        x = [[[(sum(sum(sum(sum(x1[i][j][k][b][c][p][d] for c in range(n)) for b in range(bg)) for k in range(pm[j])) \
                    for j in range(fwz))) for d in range(pj)] for p in range(pz)] for i in range(kh)]

        delta = [[[[[[[(1 if x1[i][j][k][b][c][p][d] != 0 else 0) for d in range(pj)] for p in range(pz)] for c in range(n)] \
               for b in range(bg)] for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        delta1 = [[[[[(1 if sum(sum(x1[i][j][k][b][c][p][d] for d in range(pj)) for b in range(bg)) != 0 else 0) for p
                      in range(pz)] for c in range(n)] for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        chi = [[[[(1 if sum(delta1[i][j][k][c][p] for p in range(pz)) != 0 else 0) for c in range(n)] \
                 for k in range(pm[j])] for j in range(fwz)] for i in range(kh)]
        w = [[[(1 if sum(sum(delta1[i][j][k][c][p] for c in range(n)) for k in range(pm[j])) != 0 else 0) \
               for p in range(pz)] for j in range(fwz)] for i in range(kh)]
        omega = [[(1 if sum(w[i][j][p] for p in range(pz)) != 0 else 0) for j in range(fwz)] for i in
                 range(kh)]
        tzh = [[[[[(delta1[i][j][k][c][p] * (c + 3) * t) for p in range(pz)] for c in range(n)] for k in range(pm[j])] \
                for j in range(fwz)] for i in range(kh)]

        tkhon = [min([min([min([min([(tzh[i][j][k][c][p] if (tzh[i][j][k][c][p] != 0) else float('inf')) \
                                     for p in range(pz)]) for c in range(n)]) for k in range(pm[j])]) for j in
                      range(fwz)]) \
                 for i in range(kh)]

        tkhend = [max([max([max([max([tzh[i][j][k][c][p] for p in range(pz)]) for c in range(n)]) \
                            for k in range(pm[j])]) for j in range(fwz)]) for i in range(kh)]
        # 约束条件
        constraints = []
        # constraints.append((1 - theta4) * ssl <= sum(sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
        #                        for i in range(kh)) <= (1 + theta4) * ssl)
        # for i in range(kh):
        #     # 客户的所有品种的鸡的实际装货量可在客户对所有品种的鸡的订单量的theta2的变化范围内
        #     constraints.append((1 - theta2) * sl_kh[i] <= sum(sum(x[i][j][k] for k in range(pj)) for j in range(pz)) \
        #                        <= (1 + theta2) * sl_kh[i])
        #     for j in range(pz):
        #         # 客户对鸡品种的实际装货量可在客户对该品种的鸡的订单量的theta1的变化范围内
        #         constraints.append((1-theta1)*sl_khpz[i][j] <= sum(x[i][j][k] for k in range(pj))\
        #                            <= (1+theta1)*sl_khpz[i][j])
        #         # 客户对每个品种大鸡实际装货量不得少于该客户对每个品种大鸡订单量
        #         constraints.append(x[i][j][0] >= sl[i][j][0])
        # for j in range(pz):
        #     # 所有客户的鸡品种的实际装货量可在所有客户的该品种的鸡的总订单量的theta3的变化范围内
        #     constraints.append((1-theta3)*sl_pz[j] <= sum(sum(x[i][j][k] for k in range(pj))\
        #                                                   for i in range(kh)) <= (1+theta3)*sl_pz[j])
        # # 所有养户对所有品种的鸡的实际供给量处于所有养户对所有品种的鸡的订单供给量的theta8的变化范围内
        # constraints.append(sum(sum(sum(y[i][j][k] for k in range(pj)) for j in range(pz)) \
        #                        for i in range(yh)) <= (1 + theta8) * sysl)
        # for i in range(yh):
        #     # 养户对所有品种的鸡的实际供给量处于养户对所有品种的鸡的订单供给量的theta6的变化范围内
        #     constraints.append(sum(sum(y[i][j][k] for k in range(pj)) for j in range(pz)) <= (1+theta6)*sl_yh[i])
        #     for j in range(pz):
        #         # 养户对鸡品种的实际供给量处于养户对鸡品种的订单供给量的theta5的变化范围内
        #         constraints.append(sum(y[i][j][k] for k in range(pj)) <= (1+theta5)*sl_yhpz[i][j])
        # # 所有养户对鸡品种的实际供给量处于所有养户对鸡品种的订单供给量的theta7的变化范围内
        # for j in range(pz):
        #     constraints.append(sum(sum(y[i][j][k] for k in range(pj)) for i in range(yh)) <= (1+theta7)*ysl_pz[j])
        # for j in range(fwz):
        #     for k in range(pm[j]):
        #         for b in range(bg):
        #             for c in range(n):
        #                 for p in range(pz):
        #                     for d in range(pj):
        #                         # 单位时间内在服务站内的供求平衡
        #                         constraints.append(sum(x1[i][j][k][b][c][p][d] for i in range(kh))\
        #                                            - sum(y1[i][j][k][b][c][p][d] for i in range(yh)))
        # # 客户在单位时间单元中最多只能去某个服务站的某个棚面进行装货
        # # 客户在服务站棚面时间段装鸡品种的装货情况（0-1变量 0：装货 1：不装货）delta-->list类型，五层嵌套(客户->服务站->棚面->时间段->品种)
        # # 客户在服务站棚面的时间段装货情况（0-1变量 0：装货 1：不装货）chi-->list类型，四层嵌套(客户->服务站->棚面->时间段)
        # # 客户在服务站装货情况（0-1变量 0：装货 1：不装货） omega-->list类型，两层嵌套(养户->服务站)
        # # 实际开始装货的最早时间 tkhon-->list类型 一层循环[客户]
        # # 实际装完货的最晚时间 tkhend-->list类型 一层循环[客户]
        # # 客户订单预计最早开始装货时间 khon-->list类型 一层循环[客户](已知)
        # # 客户订单预计最晚装完货时间 khend-->list类型 一层循环[客户](已知)
        # for i in range(kh):
        #     constraints.append(0 <= sum(omega[i][j] for j in range(fwz)) <= 1)
        #     constraints.append(khon[i] <= tkhon[i] <= tkhend[i] <= khend[i])
        #     for j in range(fwz):
        #         for k in range(pm[j]):
        #             for b in range(bg):
        #                 for c in range(n):
        #                     for p in range(pz):
        #                         for d in range(pj):
        #                             constraints.append(x1[i][j][k][b][c][p][d] >= delta[i][j][k][b][c][p][d])
        #                             constraints.append(x1[i][j][k][b][c][p][d] <= 2000*delta[i][j][k][b][c][p][d])
        #     for c in range(n):
        #         # 每号客户在某个时间单元内只能到达某号服务站的某个棚面进行装货
        #         constraints.append(0 <= sum(sum(chi[i][j][k][c] for k in range(pm[j])) for j in range(fwz)) <= 1)
        # for j in range(fwz):
        #     for k in range(pm[j]):
        #         for b in range(bg):
        #             for c in range(n):
        #                 # 加工能力的限制即任意一个服务站的任意个棚面的任意个磅在每个工作单元中
        #                 # 对所有养户的所有品种所有品级的鸡加工的总量不超过单位工作单元的最大处理量（t取 60）
        #                 constraints.append(sum(sum(sum(y1[i][j][k][b][c][p][d] for d in range(pj))\
        #                      for p in range(pz)) for i in range(yh)) <= 2300*t/60)
        # # cc-第m趟车从第 fwz号服务站到第yh号养户在第n个时间单元到第pm号棚面的第bg号磅卸所有品种所有品级的鸡的出车情况(0-1变量 1-出车 0-不出车)
        # # cc-->list类型 六层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元]）
        # # 第 m趟车的出车情况(0-1变量 1-出车 0-不出车)-cc1-->list类型 一层（[车趟数]）
        # # czh-第m趟车从第fwz号服务站到第yh号养户在第n个时间单元到第pm号棚面的第bg号磅卸第pz号品种pj品级的鸡后货的载货情况(0-1变量 1-载货 0-不载货)
        # # czh-->list类型 八层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元,品种,品级]）
        # # hwsl-第m趟车从第fwz号服务站到第yh号养户在第n个时间单元回到第fwz号服务站的第pm号棚面的第bg号磅卸第pz种品种 pj 品级的鸡的卸货数量
        # # hwsl-->list类型 八层嵌套（[车趟数,养户,服务站,棚面,磅,时间单元,品种,品级]）
        # # 第fwz号服务站是否派出车辆到第yh号客户-psi-->list类型 两层嵌套（[养户,服务站]）
        # # zts-总趟数
        # # 第fwz个服务站到第yh养户的派车的所有趟数的总空置数-kzsl-->list类型 两层嵌套（[养户,服务站]）
        # for u in range(m):
        #     # 同一趟车只能在某个时间单元内从某个服务站去某个养户回到服务站的某个棚面的某个磅进行卸货
        #     # cons.append({'type': 'eq', 'fun':lambda hwsl:cc1[u] - sum(sum(sum(sum(sum(cc[u][i][j][k][b][c]\
        #     #      for c in range(n)) for b in range(bg)) for k in range(pm[j])) for j in range(fwz)) for i in range(yh))})
        #     constraints.append(0 <= cc1[u] <= 1)
        #     for i in range(yh):
        #         for j in range(fwz):
        #             for k in range(pm[j]):
        #                 for b in range(bg):
        #                     for c in range(n):
        #                         # 每趟车的载重数量控制在1500~2000只
        #                         constraints.append(sum(sum(hwsl[u][i][j][k][b][c][p][d] \
        #                                 for d in range(pj)) for p in range(pz)) - 1500 * cc[u][i][j][k][b][c] >=0)
        #                         constraints.append(sum(sum(hwsl[u][i][j][k][b][c][p][d] \
        #                                 for d in range(pj)) for p in range(pz)) + 2000 * cc[u][i][j][k][b][c] >=0)
        # # zts = sum(cc1[u] for u in range(m))
        # for i in range(yh):
        #     # 一个养户只能去一个服务站卸货（一个养户只能从一个服务站调车前往）
        #     constraints.append(0 <= sum(psi[i][j] for j in range(fwz)) <= 1)
        # for u in range(m):
        #     for i in range(yh):
        #         for j in range(fwz):
        #             for k in range(pm[j]):
        #                 for b in range(bg):
        #                     for c in range(n):
        #                         for p in range(pz):
        #                             for d in range(pj):
        #                                 constraints.append(-10 <= hwsl[u][i][j][k][b][c][p][d] <=30)
        
        return constraints


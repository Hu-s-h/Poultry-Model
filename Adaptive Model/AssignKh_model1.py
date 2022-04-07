# 分配客户
import sys,os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)

from wenshi210701.avgKh import avgkh
from wenshi210701.TimeTrans import TimeTrans
from wenshi210701.DealData import DealData

class AssKh():
    
    def __init__(self,args):
        # pm_num 棚面个数 stime棚面开始运作时间（分钟） n时间单元长度
        # pm_num,stime,n = self.args
        self.args = args 
    
    def assk(self):
        use_pzInd,pm_num,tj_num,use_pmidlist,pj,stime,pm_bg_num,maxNum, kh_tn, r_kh, r_supply_kh = self.args
        self.pm_num = pm_num
        self.pj = pj
        #品种开始索引位置
        spind = kh_tn.index('spc_1')
        
        # 按时间倒序，数量倒序，品种正序排序
        r_kh.sort(key=lambda data:(-TimeTrans(data[2] if (data[2]!='' and data[2]!='-1') else stime,'m').trans(),-sum([(int(data[i].split(',')[0])\
            if (data[i] != '' and isinstance(data[i], str)) else 0)  for i in range(spind,len(data))]),\
                sum([((1 if int(data[i].split(',')[0])>0 else 0) if (data[i] != '' and isinstance(data[i]\
                    , str)) else 0)  for i in range(spind,len(data))])), reverse=False)
        index_dict = {k: i for i, k in enumerate([r_kh[x][0] for x in range(len(r_kh))])}
        r_supply_kh = sorted(r_supply_kh, key=lambda x: index_dict[x[0]])
        khName = [r_kh[i][1] for i in range(len(r_kh))]
        # str_stime = ('0'+str(stime//60) if (stime//60)<10 else str(stime//60))+':'+('0'+str(stime%60) if (stime%60)<10 else str(stime%60))
        # print(str_stime)
        # kh_temp = [(r_kh[i][2] if (r_kh[i][2]!='' and r_kh[i][2]!='-1') else str(stime)) for i in range(len(r_kh))] #客户对应取货时间
        kh_temp = [r_kh[i][2] for i in range(len(r_kh))]
        # 分配棚面
        args = r_kh,r_supply_kh,pm_num,use_pmidlist,len(r_kh),len(r_kh[0]) - spind, pj, pm_bg_num, maxNum, spind, tj_num
        khpb,khpsl = avgkh(args).avgs()
        pkhName = [[] for i in range(len(khpsl))]
        pkhSl = [[] for i in range(len(khpsl))]
        khPts = [[] for i in range(len(khpsl))]
        for i in range(len(khpsl)): #棚面
            for j in range(len(khpsl[i])): #客户
                if sum([sum([khpsl[i][j][p][d] for d in range(len(khpsl[i][j][p]))]) for p in range(len(khpsl[i][j]))])>0:
                    pkhSl[i].append([khpsl[i][j][p] for p in use_pzInd])

        pmlist = [[] for i in range(pm_num)]
        for i in range(len(khpb)):
            for j in range(len(khpb[i])):
                if khpb[i][j] == 1:
                    pmlist[j].append(r_kh[i])
                    pkhName[j].append(khName[i])
                    khPts[j].append(int(kh_temp[i]))
                    break
        #********************************************************************
        #用字典存储客户订单信息
        rr = []
        for i in range(len(r_kh)):
            dicts = {}
            for j in range(len(r_kh[i])):
                if j == 1:
                    dicts['cus_name'] = r_kh[i][j]
                if j == 2:
                    dicts['pre_time'] = TimeTrans(r_kh[i][j],'m').trans() if r_kh[i][j]!='' else stime
                if j >= spind:
                    if r_kh[i][j] != '' and isinstance(r_kh[i][j], str):
                        dd = r_kh[i][j].split(',')
                        dicts['spc_'+str(j-spind+1)] = [dd[0],dd[3]]
            rr.append(dicts)
        # 用以存储每个棚面存储客户分配情况
        pm_kh = [[] for i in range(pm_num)]

        for p in range(len(pmlist)):
            # for p in range(1,2):
            t_ind = []
            exr_kh = []
            ex = -1
            # for r_index, r_data in enumerate(r_kh):
            endflag = 0
            for i in range(len(pmlist[p])):
                each_kh = {}   
                sum_NUm = 0 #判断多客户鸡总数
                each_kh['cus_name']=[]
                each_kh['pz_and_num'] = []
                each_kh['pz'] = []
                each_kh['sum'] = []
                each_kh['pre_time'] = []
                if i in t_ind:
                    if i == len(pmlist[p]) - 1:
                        if exr_kh!=[] and ex<len(exr_kh)-1:
                            for ei in range(ex+1,len(exr_kh)):
                                temp = {}
                                num = 0 #计算品种数
                                sum_kh = 0 #计算客户需求鸡总数
                                for ej in range(len(exr_kh[ei])):
                                    if ej == 1:
                                        each_kh['cus_name'].append(exr_kh[ei][ej] if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else ('未知客户名'+str(ei)))
                                    if ej == 2:
                                        each_kh['pre_time'].append(TimeTrans(exr_kh[ei][ej],'m').trans() if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else stime)
                                    if ej>=spind and exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str):
                                        num = num + 1
                                        data = exr_kh[ei][ej].split(',')
                                        temp[kh_tn[ej]] = [int(data[0]),int(data[3])]
                                        sum_kh += int(data[0])
                                        sum_NUm += int(data[0])
                                each_kh['pz_and_num'].append(temp)
                                each_kh['pz'].append(num)
                                each_kh['sum'].append(sum_kh)        
                                ex = ex + 1
                            each_kh['sum_Num']= sum(each_kh['sum'])
                            pm_kh[p].append(each_kh)
                    continue
                while sum_NUm <= pm_bg_num[p]*maxNum: 
                    if exr_kh!=[] and ex<len(exr_kh)-1:
                        for ei in range(ex+1,len(exr_kh)):
                            temp = {}
                            num = 0 #计算品种数
                            sum_kh = 0 #计算客户需求鸡总数
                            for ej in range(len(exr_kh[ei])):
                                if ej == 1:
                                    each_kh['cus_name'].append(exr_kh[ei][ej] if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else ('未知客户名'+str(ei)))
                                if ej == 2:
                                    each_kh['pre_time'].append(TimeTrans(exr_kh[ei][ej],'m').trans() if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else stime)
                                if ej>=spind and exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str):
                                    num = num + 1
                                    data = exr_kh[ei][ej].split(',')
                                    temp[kh_tn[ej]] = [int(data[0]),int(data[3])]
                                    sum_kh += int(data[0])
                                    sum_NUm += int(data[0])
                            each_kh['pz_and_num'].append(temp)
                            each_kh['pz'].append(num)
                            each_kh['sum'].append(sum_kh)        
                            ex = ex + 1
                    temp ={}
                    num = 0 #计算品种数
                    sum_kh = 0 #计算客户需求鸡总数
                    for j in range(len(pmlist[p][i])):
                        if j == 1:
                            each_kh['cus_name'].append(pmlist[p][i][j] if (pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str)) else ('未知客户名'+str(int(pmlist[p][i][0][1:])))) 
                        if j == 2: #TimeTrans(pmlist[p][i][j],'m').trans()
                            each_kh['pre_time'].append(TimeTrans(pmlist[p][i][j],'m').trans() if (pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str)) else stime)
                        if j >= spind and pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str):
                                    num = num + 1
                                    data = pmlist[p][i][j].split(',')
                                    temp[kh_tn[j]] = [int(data[0]),int(data[3])]
                                    sum_kh += int(data[0])
                                    sum_NUm += int(data[0])
                    each_kh['pz_and_num'].append(temp)
                    each_kh['pz'].append(num)
                    each_kh['sum'].append(sum_kh)
                    if sum_NUm > pm_bg_num[p]*maxNum:
                        each_kh['sum_Num'] = sum(each_kh['sum'])
                        flag = 0
                        if each_kh['cus_name']!=[] and each_kh['pz_and_num']!=[] and each_kh['pz']!=[] and each_kh['sum']!=[]:
                            asum = each_kh['sum'][0:-1]
                            overSum = ((pm_bg_num[p]*maxNum - sum(asum)) if asum != [] else pm_bg_num[p]*maxNum) #里最大效率剩余的数目
                            each_kh['cus_name'] = each_kh['cus_name'][0:-1]
                            each_kh['pre_time'] = each_kh['pre_time'][0:-1]
                            each_kh['pz_and_num'] = each_kh['pz_and_num'][0:-1]
                            each_kh['pz'] = each_kh['pz'][0:-1]
                            each_kh['sum'] = asum
                            each_kh['sum_Num'] = sum(each_kh['sum'])
                            if overSum == 0:
                                pm_kh[p].append(each_kh)
                                i = i - 1
                                break
                            elif overSum <= pm_bg_num[p]*maxNum:
                                temp ={}
                                num = 0 #计算品种数
                                sum_kh = 0 #计算客户需求鸡总数
                                cus_name = '未知客户名'
                                pre_time = stime
                                
                                for j in range(len(pmlist[p][i])):
                                    if j == 1:
                                        cus_name = (pmlist[p][i][j] if (pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str)) else ('未知客户名'+str(int(pmlist[p][i][0][1:])))) 
                                    if j == 2: #
                                        pre_time = (TimeTrans(pmlist[p][i][j],'m').trans() if (pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str)) else stime)
                                    if j >= spind and pmlist[p][i][j] != '' and isinstance(pmlist[p][i][j], str):
                                        da = pmlist[p][i][j].split(',')
                                        temp[kh_tn[j]] = [int(da[0]),int(da[3])]
                                        # sum_kh += int(da[0])
                                temp_list=sorted(temp.items(),key=lambda x:(x[1][0],-x[1][1]),reverse=True)
                                temp = {}
                                for k in range(len(temp_list)):
                                    if temp_list[k][1][0]!=0:
                                        sum_kh += int(temp_list[k][1][0])
                                        temp[temp_list[k][0]] = temp_list[k][1][:]
                                        num = num + 1
                                        temp_list[k][1][0] = 0
                                        if sum_kh >= overSum:
                                            if sum_kh > overSum:
                                                temp_list[k][1][0] = sum_kh - overSum
                                                temp[temp_list[k][0]] = [overSum - sum_kh + int(temp[temp_list[k][0]][0]),temp_list[k][1][1]]
                                                sum_kh = overSum
                                            each_kh['cus_name'].append(cus_name) 
                                            each_kh['pre_time'].append(pre_time)
                                            each_kh['pz_and_num'].append(temp)
                                            each_kh['pz'].append(num)
                                            each_kh['sum'].append(sum_kh)
                                            each_kh['sum_Num'] = sum(each_kh['sum'])
                                            pm_kh[p].append(each_kh)
                                            break
                                if sum([temp_list[c][1][0] for c in range(len(temp_list))]) >= pm_bg_num[p]*maxNum:
                                    while sum([temp_list[c][1][0] for c in range(len(temp_list))])>=pm_bg_num[p]*maxNum:
                                        each_kh = {}   
                                        sum_NUm = 0 #判断多客户鸡总数
                                        each_kh['cus_name']=[]
                                        each_kh['pz_and_num'] = []
                                        each_kh['pz'] = []
                                        each_kh['sum'] = []
                                        each_kh['pre_time'] = []

                                        temp ={}
                                        num = 0 #计算品种数
                                        sum_kh = 0 #计算客户需求鸡总数
                                        for k in range(len(temp_list)):
                                            if temp_list[k][1][0]!=0:
                                                sum_kh += int(temp_list[k][1][0])
                                                temp[temp_list[k][0]] = temp_list[k][1][:]
                                                num = num + 1
                                                temp_list[k][1][0] = 0
                                                if sum_kh >= pm_bg_num[p]*maxNum:
                                                    if sum_kh > pm_bg_num[p]*maxNum:
                                                        temp_list[k][1][0] = sum_kh - pm_bg_num[p]*maxNum
                                                        temp[temp_list[k][0]] = [pm_bg_num[p]*maxNum - sum_kh + int(temp[temp_list[k][0]][0]),temp_list[k][1][1]]
                                                        sum_kh = pm_bg_num[p]*maxNum
                                                    each_kh['pz_and_num'].append(temp)
                                                    each_kh['pz'].append(num)
                                                    each_kh['sum'].append(sum_kh)
                                                    each_kh['sum_Num'] = sum(each_kh['sum'])
                                                    each_kh['cus_name'].append(cus_name) 
                                                    each_kh['pre_time'].append(pre_time)
                                                    each_kh['sum_Num'] = sum(each_kh['sum'])
                                                    pm_kh[p].append(each_kh)
                                                    break
                                if sum([temp_list[c][1][0] for c in range(len(temp_list))]) < pm_bg_num[p]*maxNum:
                                    name1 = []
                                    for k in range(len(temp_list)):
                                        if temp_list[k][1][0]!=0:
                                            name1.append([int(temp_list[k][0].strip().split("_")[1]),int(temp_list[k][1][0])])
                                    r_kh_new = list(pmlist[p][i])[:]
                                    ulist = [name1[u][0] for u in range(len(name1))]
                                    for c in range(spind,len(r_kh_new)):
                                        if (c-spind+1) not in ulist:
                                            r_kh_new[c] = None
                                    for x in range(len(ulist)):
                                        da1 = r_kh_new[ulist[x]+spind-1].split(',')
                                        r_kh_new[ulist[x]+spind-1] = str(name1[x][1])+','+str(da1[1])+','+str(da1[2])+','+str(da1[3])
                                    if sum([(1 if r_kh_new[x] != None else 0) for x in range(spind,len(r_kh_new))])>0:
                                        exr_kh.append(r_kh_new)
                                break                   
                    if i<len(pmlist[p])-1:
                        i = i + 1
                        t_ind.append(i)                        
                    else:                      
                        endflag = 1
                        if exr_kh!=[] and ex<len(exr_kh)-1:
                            for ei in range(ex+1,len(exr_kh)):
                                temp = {}
                                num = 0 #计算品种数
                                sum_kh = 0 #计算客户需求鸡总数
                                for ej in range(len(exr_kh[ei])):
                                    if ej == 1:
                                        each_kh['cus_name'].append(exr_kh[ei][ej] if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else ('未知客户名'+str(ei)))
                                    if ej == 2: #
                                        each_kh['pre_time'].append(TimeTrans(exr_kh[ei][ej],'m').trans() if (exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str)) else stime)
                                    if ej >= spind and exr_kh[ei][ej] != '' and isinstance(exr_kh[ei][ej], str):
                                        num = num + 1
                                        data = exr_kh[ei][ej].split(',')
                                        temp[kh_tn[ej]] = [int(data[0]),int(data[3])]
                                        sum_kh += int(data[0])
                                        sum_NUm += int(data[0])
                                each_kh['pz_and_num'].append(temp)
                                each_kh['pz'].append(num)
                                each_kh['sum'].append(sum_kh)        
                                ex = ex + 1
                        break 
                if endflag:
                    each_kh['sum_Num'] = sum(each_kh['sum'])
                    pm_kh[p].append(each_kh)
                    break
        # print(sum([sum([pm_kh[i][j]['sum_Num'] for j in range(len(pm_kh[i]))]) for i in range(len(pm_kh))]))

        return pkhName, khPts, pkhSl,pm_kh

    def dealKhData(self):
        pkhName, khPts, pkhSl,pm_kh = self.assk()
        kh_info = [[] for i in range(self.pm_num)]
        for i in range(len(pm_kh)): #棚面
            for j in range(len(pm_kh[i])):
                dict_kh={}
                dict_kh['cus_name'] = pm_kh[i][j]['cus_name']
                dict_kh['pre_time'] = j * 60 + 180
                dict_kh['detail_info'] = [[] for c in range(len(pm_kh[i][j]['cus_name']))]
                for p in range(len(pm_kh[i][j]['pz_and_num'])):
                    dinfo_dict = {}
                    dinfo_dict['cus_name'] = pm_kh[i][j]['cus_name'][p]
                    key_name = list(pm_kh[i][j]['pz_and_num'][p].keys())
                    for na in key_name:
                        dinfo_dict[na] = pm_kh[i][j]['pz_and_num'][p][na]
                    dict_kh['detail_info'][p] = dinfo_dict
                for pz_num in (pm_kh[i][j]['pz_and_num']):
                    key_name = list(pz_num.keys())
                    for k in range(len(key_name)):
                        if key_name[k] not in list(dict_kh.keys()):
                            dict_kh[key_name[k]] = [0 for d in range(self.pj)]
                            dict_kh[key_name[k]][pz_num[key_name[k]][1]-1] = pz_num[key_name[k]][0]
                        else:
                            dict_kh[key_name[k]][pz_num[key_name[k]][1]-1] += pz_num[key_name[k]][0]
                name1 = list(dict_kh.keys())[3:]
                dict_kh['sum'] = sum(sum(dict_kh[name1[c]]) for c in range(len(name1)))
                dict_kh['pre_pm'] = i
                kh_info[i].append(dict_kh)
        return kh_info, pkhName, khPts, pkhSl

if __name__ == '__main__':
    args_main,fpb_arg = DealData().deal()
    pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_jinum,maxNum,pz,pj,use_pzInd,pm_bg_num,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t, ad_val, kh_wait_tnum, yh_wait_tnum, car_max_num, s_m6_mt= args_main
    args_m1 = use_pzInd,pm_num,tj_num,use_pmidlist,pj,stime,pm_bg_num,maxNum, kh_tn, r_kh, r_supply_kh
    print('开始进入模型1')
    # pkhName, pkhSl = AssKh(args_m1).assk()
    kh_info, pkhName, khPts, pkhSl = AssKh(args_m1).dealKhData()
    
    # print('模型1运行完成')

    # print(kh_info[0][1])
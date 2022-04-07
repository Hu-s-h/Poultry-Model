import math
from wenshi210701.ConnDB import ConnDB

class DealData():
    def __init__(self):
        pass
    def deal(self):
        #连接数据库
        conndb = ConnDB(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
        conndb.conn()
        ''' 棚面及服务站数据 '''
        other_des,other_data = conndb.select("SELECT * FROM other_info where oid = 1")
        max_pbdes,max_pbdata = conndb.select("SELECT * FROM pm_bg_info")
        maxpm_num = len(max_pbdata) #最大棚面数
        max_pmdict = {max_pbdata[i][0]:max_pbdata[i][1] for i in range(len(max_pbdata))}  #所有的棚面ID以及棚面名
        pbdes,pbdata = conndb.select("SELECT * FROM pm_bg_info WHERE pm_bg_num > 0 ")
        use_pmdict = {pbdata[i][0]:pbdata[i][1] for i in range(len(pbdata))}  #启用的棚面ID以及棚面名
        pm_bg_num = [pbdata[i][2] for i in range(len(pbdata))] #每个启用的棚面的使用磅数量
        pm_kh_num = [pbdata[i][3] for i in range(len(pbdata))] #各棚面中每个时间单元内，棚面内最大客户人数 
        use_pmidlist = list(use_pmdict.keys())
        ftdes,fwzdata = conndb.select("SELECT * FROM fwz_name")
        pftdes,pfdata = conndb.select("SELECT pm_id,fwz_id FROM tb_pm_fwz_info")
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
        n_max_jinum = int(other_data[0][2]) #每个时间单元每个养户最多送鸡数
        rs_pm = pm_kh_num # 各棚面中每个时间单元内，棚面内最大客户人数 
        max_t = int(other_data[0][7]) #模型6单个模型最大求解时间（秒）
        # each_yh_num = len(use_pmidlist)/2 #插入每个虚拟养户数量(每个养户可以去两个棚面)
        # self.bre_num = each_yh_num
        bre_num = math.ceil(len(use_pmidlist)/2) #插入每个虚拟养户数量(每个养户可以去两个棚面)
        # each_yh_num = 2 #插入每个虚拟养户数量
        ad_val = int(other_data[0][3]) # ad_val 用于调节每个棚面时间单元宽松度（增添每个棚面的时间单元个数）
        kh_wait_tnum = int(other_data[0][6]) # kh_wait_tnum-客户最大等待时间单元 
        yh_wait_tnum = int(other_data[0][5]) # yh_wait_tnum-养户最大等待时间单元
        car_max_num = int(other_data[0][4]) #车辆满载装鸡数
        s_m6_mt = int(other_data[0][8]) #养户与客户匹配模型（模型6补充模型）单个模型最大运行时间
        ''' 客户数据 '''
        # kh-客户的个数
        kh_tn,r_kh = conndb.select("SELECT * FROM order_info")
        kh_supply_tn,r_supply_kh = conndb.select("SELECT * FROM order_supply_info")
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
        pjdes,pjdata = conndb.select("SELECT * FROM pj_info")
        pj = len(pjdata) #品级个数
        pjlist = [pjdata[i][1] for i in range(len(pjdata))] #品级名
        ''' 养户数据 '''
        yh_tn,r_yh = conndb.select("SELECT * FROM bre_info") # r_yh用于存放每个养户信息
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
            gapdes,gapdata = conndb.select("SELECT * FROM gap_info WHERE bre_id= '%s' ", yhlist[y])
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
        
        specdes,pz_indToname = conndb.select("SELECT * FROM bre_name") #鸡品种id对应品种名
        conndb.close()
        ''' 存表地址 '''
        #中间过程存表 
        data_info_path = r'.\wenshi0306\output_tabel\数据信息表.xls'
        info_path = r'.\wenshi0306\output_tabel\信息表.xls'
        kyinfo_path = r'.\wenshi0306\output_tabel\调配信息表.xls'
        car_path = r'.\wenshi0306\output_tabel\车次信息表.xls'
        #调度结果存表
        yh_info_path = r'.\wenshi0306\output_tabel\养户调度表.xls'
        new_path = r'.\wenshi0306\output_tabel\新调度结果表.xls'
        kh_info_path = r'.\wenshi0306\output_tabel\客户信息表.xls'
        pathky = r'.\wenshi0306\output_tabel\客户与养户匹配调度表.xls'
        # 执行调度
        args_main = pm_num,tj_num,use_pmidlist,use_pfdict,stime,n_max_jinum,maxNum,pz,pj,use_pzInd,pm_bg_num,kh_tn, r_kh, r_supply_kh, yh, yhsl, yhAllname, gap, pz_indToname, pjlist, rs_pm, max_t,ad_val, kh_wait_tnum, yh_wait_tnum, car_max_num, s_m6_mt
        # yh_info_path 养户调度表 data_info_path-数据信息表 kyinfo_path-调配信息表 car_path-车次信息表 kh_info_path-客户信息表
        args_path = yh_info_path,new_path,kh_info_path,data_info_path,car_path,kyinfo_path,pathky
        # use_fwzdict 启用的服务站ID以及服务站名
        # use_fwzTopm_id_dict 启用服务站ID对应该服务站启用的棚面ID
        # use_pfdict 启用的棚面ID以及启用的服务站ID
        # use_pmdict 启用的棚面ID以及棚面名
        fpb_arg = use_fwzdict, use_pmdict, use_pfdict, use_fwzTopm_id_dict
        return args_main,fpb_arg
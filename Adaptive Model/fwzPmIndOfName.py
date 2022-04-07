import sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)
from wenshi210701.ConnDB import ConnDB


class fwzPmIndOfName():
    def __init__(self,fpb_arg,indOrname,flag=0):
        self.indOrname = indOrname
        self.flag = flag
        # use_fwzdict 启用的服务站ID以及服务站名
        # use_fwzTopm_id_dict 启用服务站ID对应该服务站启用的棚面ID
        # use_pfdict 启用的棚面ID以及启用的服务站ID
        # use_pmdict 启用的棚面ID以及棚面名
        self.use_fwzdict, self.use_pmdict, self.use_pfdict, self.use_fwzTopm_id_dict = fpb_arg
        self.fwz_list = list(self.use_fwzdict.values())
        # self.fwz_list = ['稔村服务站']
        self.fwz_pm_num = [len(self.use_fwzTopm_id_dict[kf]) for kf in list(self.use_fwzdict.keys())]
    # 棚面编号与棚面名互转
    def getpmIndofName(self):
        if self.flag == 0: #棚面编号转棚面名
            pm_id_list = list(self.use_pmdict.keys())
            return self.use_pmdict[pm_id_list[self.indOrname]]
        else:
            pm_name_list = list(self.use_pmdict.values())
            return pm_name_list.index(self.indOrname)
    # 棚面编号转服务站名
    def getpmOffwzName(self):
        return self.use_fwzdict[self.use_pfdict[list(self.use_pfdict.keys())[self.indOrname]]]
    # 服务站编号与服务站名互转
    def getfwzIndofName(self):
        if self.flag == 0: #服务站编号转服务站名
            return self.fwz_list[self.indOrname]
        else: #服务站名转服务站编号
            if self.indOrname not in self.fwz_list:
                print('未找到对应服务站名')
            return self.fwz_list.index(self.indOrname)

if __name__ == '__main__':
    #连接数据库
    conndb = ConnDB(host='localhost', port=3306, user='root', passwd='root', db='ws_chicken_db')
    conndb.conn()
    ''' 棚面及服务站数据 '''
    max_pbdes,max_pbdata = conndb.select("SELECT * FROM pm_bg_info")
    maxpm_num = len(max_pbdata) #最大棚面数
    max_pmdict = {max_pbdata[i][0]:max_pbdata[i][1] for i in range(len(max_pbdata))}  #所有的棚面ID以及棚面名
    pbdes,pbdata = conndb.select("SELECT * FROM pm_bg_info WHERE pm_bg_num > 0 ")
    use_pmdict = {pbdata[i][0]:pbdata[i][1] for i in range(len(pbdata))}  #启用的棚面ID以及棚面名
    pm_bg_num = [pbdata[i][2] for i in range(len(pbdata))] #每个启用的棚面的使用磅数量
    use_pmidlist = list(use_pmdict.keys())
    ftdes,fwzdata = conndb.select("SELECT * FROM fwz_name")
    pftdes,pfdata = conndb.select("SELECT pm_id,fwz_id FROM tb_pm_fwz_info")
    all_pfdict = {pfdata[i][0]:pfdata[i][1] for i in range(len(pfdata))}  #棚面ID:服务站ID
    use_pfdict = {}
    for p in use_pmidlist:
        use_pfdict[p] = all_pfdict[p]
    all_fwz_dict = {fwzdata[i][0]:fwzdata[i][1] for i in range(len(fwzdata))} #服务站ID:服务站名
    # all_fwzTopm_id_dict = {}
    # for i in range(len(pfdata)):
    #     if pfdata[i][1] not in list(all_fwzTopm_id_dict.keys()):
    #         all_fwzTopm_id_dict[pfdata[i][1]]=[]
    #     all_fwzTopm_id_dict[pfdata[i][1]].append(pfdata[i][0])
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
    fpb_arg = use_fwzdict, use_pmdict, use_pfdict, use_fwzTopm_id_dict
    for i in range(pm_num):
        pm_na = fwzPmIndOfName(fpb_arg,i,0).getpmIndofName()
        print(pm_na)
        fwz_na = fwzPmIndOfName(fpb_arg,i,0).getpmOffwzName()
        print(fwz_na)
        pm_in = fwzPmIndOfName(fpb_arg,pm_na,1).getpmIndofName()
        print(pm_in)
    # for i in range(len(use_fwzdict)):
    #     fwz_na = fwzPmIndOfName(fpb_arg,i,0).getfwzIndofName()
    #     print(fwz_na)
    #     fwz_in = fwzPmIndOfName(fpb_arg,fwz_na,1).getfwzIndofName()
    #     print(fwz_in)
    # gapdes,gapdata = conndb.select("SELECT * FROM gap_info WHERE bre_id= '%s' ", '6609')
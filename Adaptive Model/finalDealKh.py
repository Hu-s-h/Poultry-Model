from functools import reduce
from logging import error
import math
import os
import xlrd
from xlutils.copy import copy as xl_copy
import xlwt
'''
（1）首先判断某工作单元里的客户是否在后边工作单元取货，如果不取了，就一定把他安排在该工作单元。
（2）如果某工作单元的客户还要到后边的工作单元取货，则设置为可调配客户；
（3）判断工作单元客户数量，要小于12个（建议可调参）。
     如果小于12，则所有客户不动。如果大于12，则选可调配客户里装鸡量最小的客户客户往下一工作单元调，直到小于等于12为止。
（4）按棚面跑就行。
'''


class finalDealKh():
    def __init__(self, path, lackpath, output_path, pbgNum, bgEff, Nlen, maxcarnum, pkhName, khPt, isFlag = True):
        self.path = path
        self.lackpath = lackpath
        self.output_path = output_path
        self.pbgNum = pbgNum #每个棚面开磅数
        self.bgEff = bgEff # 磅每个时间单元处理效率
        self.Nlen = Nlen #时间单元长度
        self.maxcarnum = maxcarnum #每个时间单元最多允许客户车数
        self.khPt = khPt #每个棚面每个客户预计取货时间单元
        self.pkhName = pkhName #每个棚面每个客户的名字
        self.isFlag = isFlag #是否重新调整客户时间

    def getMinute(self, time_list):
        if len(time_list) == 1:
            return 60 * time_list[0]
        return 60 * time_list[0] + time_list[1]

    def getMinInd(self, each_sum, tname, kname, tind, pkhName, khPt):
        resind = len(each_sum) # 初始化最大
        for i in range(len(each_sum)):
            # 如果该客户后面时间单元还要取货且(resind为初始值或者当前客户取鸡总数比resind索引位置的客户取鸡数少,更新resind位置) 且 客户不存在预定时间
            if sum(kname[tname[i]][tind + 1:]) > 0 and (resind == len(each_sum) or each_sum[i] < each_sum[resind]) and (khPt[pkhName.index(tname[i])] == -1):
                resind = i
        # 如果resind仍为初始值，直接选择不存在预定时间的最小取货总数的客户所在索引 否则返回-1
        if resind == len(each_sum):
            eList = [each_sum[i] for i in range(len(each_sum)) if khPt[pkhName.index(tname[i])] == -1]
            resind = each_sum.index(min(eList)) if len(eList)>0 else -1

        return resind
    def transtime(self,str_time, int_m):
        h,m = map(int,str_time.split(":"))
        h += (m+int_m)//60
        m = (m+int_m)%60
        return (('0'+str(h)) if h<10 else str(h)) +':'+ (('0'+str(m)) if m<10 else str(m))
        
    def getKh(self):
        worktable = xlrd.open_workbook(self.path)  # 打开此地址下的exl文档
        # 获取所有sheet
        sheetnames = worktable.sheet_names()
        # sheet_name = worktable.sheets()
        sname = '客户调度表'
        if sname not in sheetnames:
            error("养户调度表中不存在'" + sname + "'部分")
            return
        ind = sheetnames.index(sname)
        sheet_kh = worktable.sheet_by_index(ind)
        row_num = sheet_kh.nrows
        col_num = sheet_kh.ncols
        func = lambda x, y: x if y in x else x + [y]
        pm_name = reduce(func, [[],] + sheet_kh.col_values(2)[1:])
        khdata = [[] for _ in range(len(pm_name))]
        for i in range(1, row_num):
            khdata[pm_name.index(sheet_kh.row_values(i)[2])].append(sheet_kh.row_values(i))
        kname = []  #每个棚面每个客户每个时间段是否出现
        pdata = []  #每个棚面每个时间段的客户排班数据
        ktimes = [{} for _ in range(len(khdata))]  #每个棚面每个时间段客户数
        pkt = []  #每个棚面的每个时间段时间
        for i in range(len(khdata)):
            # kname.append([da[0] for da in khdata[i]])
            kt = reduce(func, [
                [],
            ] + [da[3] for da in khdata[i]])
            pkt.append(kt)
            kn = reduce(func, [
                [],
            ] + [da[0] for da in khdata[i]])
            kname.append(
                dict(
                    zip(kn, [[0 for _ in range(len(kt))]
                             for _ in range(len(kn))])))
            pdata.append(dict(zip(kt, [{} for _ in range(len(kt))])))
            for j in range(len(khdata[i])):
                if khdata[i][j][0] not in pdata[i][khdata[i][j][3]].keys():
                    pdata[i][khdata[i][j][3]][khdata[i][j][0]] = [[], 0]
                pdata[i][khdata[i][j][3]][khdata[i][j][0]][0].append(
                    khdata[i][j])

                pdata[i][khdata[i][j][3]][khdata[i][j][0]][1] += int(
                    khdata[i][j][6])
                kname[i][khdata[i][j][0]][kt.index(khdata[i][j][3])] = 1
            for key in pdata[i].keys():
                ktimes[i][key] = len(pdata[i][key])

        for i in range(len(pdata)): #棚面
            tList = list(pdata[i].keys())
            key = 0
            while key < len(tList):
                while ktimes[i][tList[key]] > self.maxcarnum:
                    tdata = list(pdata[i][tList[key]].values()) #本时间段每个客户的数据列表及其各自取鸡总数
                    tname = list(pdata[i][tList[key]].keys()) #本时间段每个客户的客户名
                    each_sum = [tdata[i][1] for i in range(len(tdata))] #每个客户的各自取鸡总数
                    tind = pkt[i].index(tList[key]) #本时间段所属时间段索引
                    minind = self.getMinInd(each_sum, tname, kname[i], tind, self.pkhName[i], self.khPt[i]) #获取应该移动的客户索引
                    if minind == -1:
                        break
                    if key+1 < len(pkt[i]):
                        if tname[minind] not in pdata[i][tList[key + 1]].keys():
                            ktimes[i][tList[key + 1]] += 1
                            pdata[i][tList[key + 1]][tname[minind]] = [[], 0]
                    else:
                        lh, lm = map(int,pkt[i][-1].split(":"))
                        newt = str(lh+1)+':'+str(lm)
                        pkt[i].append(newt)
                        if len(kname[i][tname[minind]])<len(pkt[i]):
                            for kk in kname[i].keys(): kname[i][kk].append(0)
                        kname[i][tname[minind]][key+1] = 1
                        if newt not in pdata[i].keys():
                            ktimes[i][newt] = 0
                            pdata[i][newt] = {}
                            tList = list(pdata[i].keys())
                        if tname[minind] not in pdata[i][newt].keys():
                            pdata[i][newt][tname[minind]]=[[],0]
                        
                    pdata[i][tList[key + 1]][tname[minind]][0] += pdata[i][tList[key]][tname[minind]][0]
                    pdata[i][tList[key + 1]][tname[minind]][1] += pdata[i][tList[key]][tname[minind]][1]
                    del pdata[i][tList[key]][tname[minind]]
                    ktimes[i][tList[key]] -= 1
                
                key += 1  
       
        ''' 重新分配客户时间单元 '''
        if self.isFlag:
            psum = [{} for _ in range(len(pdata))] #存储每个棚面每个时间单元取货总数
            newpdata = [{} for _ in range(len(pdata))] #存储每个棚面重新定义时间的客户取货数据
            newtlist = [[] for _ in range(len(pdata))] #存储每个棚面新时间单元
            
            for i in range(len(pdata)):
                ptList = list(pdata[i].keys())
                for tkey in ptList:
                    tdata = list(pdata[i][tkey].values())
                    psum[i][tkey] = sum(tdata[i][1] for i in range(len(tdata))) #每个客户的各自取鸡总数
                tList = list(psum[i].keys())
                if len(tList)>=1: newtlist[i].append(tList[0])
                for j in range(1,len(psum[i])):
                    newtlist[i].append(self.transtime(newtlist[i][-1],math.ceil(psum[i][tList[j-1]]*self.Nlen/(self.pbgNum[i]*self.bgEff))))
                for j in range(len(ptList)):
                    newpdata[i][newtlist[i][j]] = pdata[i][ptList[j]]
            print("请注意，客户已重排时间！")
        else:
            newpdata = pdata
            print("请注意，客户未重排时间！")

        return kname, newpdata

    def saveKh(self):
        kname, pdata = self.getKh()
        rb = xlrd.open_workbook(self.path, formatting_info=True)
        lacktable = xlrd.open_workbook(self.lackpath)  # 打开此地址下的exl文档
        sheet_lack = lacktable.sheet_by_index(
            lacktable.sheet_names().index("客户缺货表"))

        sheetnames = rb.sheet_names()
        table_info = xl_copy(rb)
        sheet_khinfo = table_info.add_sheet("最终客户表")
        title_khinfo = ['客户名', '服务站名', '棚面名', '时间段', '品种', '品级', '数量']
        i = 0
        for header in title_khinfo:
            sheet_khinfo.write(0, i, header)
            i += 1
        sheet_lackinfo = table_info.add_sheet("客户缺货表")
        row_kh = 1
        for i in range(len(pdata)):
            for curt in pdata[i].keys():
                for curr_kh in pdata[i][curt].keys():
                    for curr_data in pdata[i][curt][curr_kh][0]:
                        for d in range(len(curr_data)):
                            if d == 3:
                                sheet_khinfo.write(row_kh, d, curt)
                            else:
                                sheet_khinfo.write(row_kh, d, curr_data[d])
                        row_kh += 1
        row_lack = 0
        for i in range(sheet_lack.nrows):
            valList = sheet_lack.row_values(i)
            for j in range(len(valList)):
                sheet_lackinfo.write(row_lack, j, valList[j])
            row_lack += 1

        if self.output_path == '':
            self.output_path = r'.\wenshi210701\output_tabel\最终调配结果信息表.xlsx'
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        table_info.save(self.output_path)
        print("最终调配结果信息表导出成功！")


if __name__ == "__main__":
    path = r"D:\VSCode\Wenshi2020\wenshi210701\output_table\调配结果信息表.xlsx"
    lackpath = r"D:\VSCode\Wenshi2020\wenshi210701\output_table\调配信息表.xlsx"
    output_path = r"D:\VSCode\Wenshi2020\wenshi210701\output_table\最终调配结果信息表.xlsx"
    finalDealKh(path, lackpath, output_path,[4,4],2000,60,11).saveKh()

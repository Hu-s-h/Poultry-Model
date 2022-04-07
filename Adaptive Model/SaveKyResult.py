import os
import re
import xlwt
import math
import xlrd
import numpy as np

from logging import error
from functools import reduce
from wenshi210701.TimeTrans import TimeTrans
from wenshi210701.fwzPmIndOfName import fwzPmIndOfName


class SaveKyResult():
    def __init__(self, args_ky, args_path, fpb_arg):
        self.args_ky = args_ky
        self.args_path = args_path
        self.fpb_arg = fpb_arg

    def preRes(self, ynpp_res, knpp_res, ky_res, pz, pj):
        # ynpp_res-每个棚面每个时间单元每辆车次送品种品级鸡数
        # knpp_res-每个棚面每个时间单元每个客户取品种品级鸡数
        # fktYn-每个服务站每个养户已经开始卸货车辆卸货所属时间单元
        # fktYse-每个服务站每个养户已知的最早开始卸货时间和最晚卸货时间单元
        # ky_res-每个棚面每个时间单元每个客户从每辆车取品种品级鸡数
        # ky_path-调配结果表存储位置
        # pkhName-每个棚面每个客户名
        # use_yhAllname-养户名列表
        # pz-品种数 pj-品级数
        # pjlist-品级名列表
        # pzlist-品级名列表
        t = float(60) / self.Nlen  #每小时时间单元个数
        # pz, pj, use_yhAllname, pzlist, pjlist,pkhName,ynpp_res, knpp_res, fktYn, fktYse , ky_res, ky_path= self.args_ky
        new_ynpp_res = [[[[[0 for e in range(pj)] for d in range(pz)]
                          for c in range(len(ynpp_res[a][0]))]
                         for b in range(math.ceil(len(ynpp_res[a]) / t))]
                        for a in range(len(ynpp_res))]
        new_knpp_res = [[[[[0 for e in range(pj)] for d in range(pz)]
                          for c in range(len(knpp_res[a][0]))]
                         for b in range(math.ceil(len(knpp_res[a]) / t))]
                        for a in range(len(knpp_res))]
        new_ky_res = [[[[[[0 for f in range(pj)] for e in range(pz)]
                         for d in range(len(ky_res[a][0][c]))]
                        for c in range(len(ky_res[a][0]))]
                       for b in range(math.ceil(len(ky_res[a]) / t))]
                      for a in range(len(ky_res))]
        for a in range(len(ky_res)):  #棚面
            for b in range(len(ky_res[a])):  #时间单元
                for c in range(len(ky_res[a][b])):  #客户
                    for d in range(len(ky_res[a][b][c])):  #车次
                        for e in range(len(ky_res[a][b][c][d])):  #品种
                            for f in range(len(ky_res[a][b][c][d][e])):  #品级
                                new_ky_res[a][int(
                                    b /
                                    t)][c][d][e][f] += ky_res[a][b][c][d][e][f]
                    for e in range(pz):  #品种
                        for f in range(pj):  #品级
                            new_knpp_res[a][int(
                                b / t)][c][e][f] += knpp_res[a][b][c][e][f]
                for c in range(len(ynpp_res[a][b])):  #车次
                    for e in range(pz):  #品种
                        for f in range(pj):  #品级
                            new_ynpp_res[a][int(
                                b / t)][c][e][f] += ynpp_res[a][b][c][e][f]
        return new_knpp_res, new_ynpp_res, new_ky_res

    def timetrans(self, timestyle1, timestyle2):
        if timestyle1 == '':
            return timestyle2
        else:
            time1 = []
            time2 = []
            t1 = timestyle1.split('-')
            for i in range(len(t1)):
                t2 = t1[i].split(':')
                time1.append(int(t2[0]) * 60 + int(t2[1]))
            s1 = timestyle2.split('-')
            for i in range(len(s1)):
                s2 = s1[i].split(':')
                time2.append(int(s2[0]) * 60 + int(s2[1]))
            at = time1[1] - time1[0] + time2[1]
            return s1[0] + '-' + TimeTrans(at, 'h').trans()

    def save_ky_excel(self, ynpp_res, knpp_res, ky_res, vir_ky, pkhName,
                      carpYhInd, use_yhAllname, pz, pj):
        # ynpp_res-每个棚面每个时间单元每辆车次送品种品级鸡数
        # knpp_res-每个棚面每个时间单元每个客户取品种品级鸡数
        # ky_res-每个棚面每个时间单元每个客户从每辆车取品种品级鸡数
        # pz-品种数 pj-品级数
        # pkhName-每个棚面每个客户名
        # carpYhInd-每个棚面中每个车次对应养户索引
        # use_yhAllname-养户名列表 use_yhAllname[carpYhInd
        new_knpp_res, new_ynpp_res, new_ky_res = self.preRes(
            ynpp_res, knpp_res, ky_res, pz, pj)
        # 导出成为excel表-------------------------------------------------------------------------------------------------------
        table_info = xlwt.Workbook()  # 创建一个excel
        sheet_yhinfo = table_info.add_sheet("养户表")
        title_yhinfo = ['养户名', '服务站名', '棚面名', '时间段', '品种', '品级', '数量']
        i = 0
        for header in title_yhinfo:
            sheet_yhinfo.write(0, i, header)
            i += 1
        sheet_khinfo = table_info.add_sheet("客户表")
        title_khinfo = ['客户名', '服务站名', '棚面名', '时间段', '品种', '品级', '数量']
        i = 0
        for header in title_khinfo:
            sheet_khinfo.write(0, i, header)
            i += 1
        sheet_kyinfo = table_info.add_sheet("客户与养户车次对应表")
        title_kyinfo = [
            '客户名', '车次', '养户名（车次所属养户）', '时间段', '服务站名', '棚面名', '品种', '品级', '数量'
        ]
        i = 0
        for header in title_kyinfo:
            sheet_kyinfo.write(0, i, header)
            i += 1
        sheet_virinfo = table_info.add_sheet("客户缺货表")
        title_virinfo = ['客户名', '服务站名', '棚面名', '品种', '品级', '数量']
        i = 0
        for header in title_virinfo:
            sheet_virinfo.write(0, i, header)
            i += 1
        row_kh = 1
        for i in range(len(new_knpp_res)):  #棚面
            for j in range(len(new_knpp_res[i])):  #时间段
                for k in range(len(new_knpp_res[i][j])):  #客户
                    for p in range(len(new_knpp_res[i][j][k])):  #品种
                        for d in range(len(new_knpp_res[i][j][k][p])):  #品级
                            if new_knpp_res[i][j][k][p][d] != 0:
                                sheet_khinfo.write(row_kh, 0, pkhName[i][k])
                                sheet_khinfo.write(
                                    row_kh, 1,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmOffwzName())
                                sheet_khinfo.write(
                                    row_kh, 2,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmIndofName())
                                sheet_khinfo.write(row_kh, 3, j)

                                sheet_khinfo.write(row_kh, 4,
                                                   self.pzAllname[p])
                                sheet_khinfo.write(row_kh, 5,
                                                   self.pjAllname[d])
                                sheet_khinfo.write(
                                    row_kh, 6,
                                    int(new_knpp_res[i][j][k][p][d]))

                                row_kh += 1
        row_yh = 1
        for i in range(len(new_ynpp_res)):  #棚面
            for j in range(len(new_ynpp_res[i])):  #时间段
                for k in range(len(new_ynpp_res[i][j])):  #车次
                    for p in range(len(new_ynpp_res[i][j][k])):
                        for d in range(len(new_ynpp_res[i][j][k][p])):
                            if new_ynpp_res[i][j][k][p][d] != 0:
                                sheet_yhinfo.write(
                                    row_yh, 0, use_yhAllname[carpYhInd[i][k]])
                                sheet_yhinfo.write(
                                    row_yh, 1,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmOffwzName())
                                sheet_yhinfo.write(
                                    row_yh, 2,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmIndofName())
                                sheet_yhinfo.write(row_yh, 3, j)
                                sheet_yhinfo.write(row_yh, 4,
                                                   self.pzAllname[p])
                                sheet_yhinfo.write(row_yh, 5,
                                                   self.pjAllname[d])
                                sheet_yhinfo.write(
                                    row_yh, 6,
                                    int(new_ynpp_res[i][j][k][p][d]))
                                row_yh += 1
        row_ky = 1
        for i in range(len(new_ky_res)):  #棚面
            for j in range(len(new_ky_res[i])):  #时间段
                for k in range(len(new_ky_res[i][j])):  #客户名
                    for c in range(len(new_ky_res[i][j][k])):  #车次
                        for p in range(len(new_ky_res[i][j][k][c])):  #品种
                            for d in range(len(
                                    new_ky_res[i][j][k][c][p])):  #品级
                                if new_ky_res[i][j][k][c][p][d] != 0:
                                    sheet_kyinfo.write(row_ky, 0,
                                                       pkhName[i][k])  #客户名
                                    sheet_kyinfo.write(row_ky, 1, c + 1)  #车次
                                    sheet_kyinfo.write(
                                        row_ky, 2, use_yhAllname[
                                            carpYhInd[i][c]])  #养户名（车次所属养户）
                                    sheet_kyinfo.write(row_ky, 3, j)  #时间段
                                    sheet_kyinfo.write(
                                        row_ky, 4,
                                        fwzPmIndOfName(
                                            self.fpb_arg, i,
                                            0).getpmOffwzName())  #服务站名
                                    sheet_kyinfo.write(
                                        row_ky, 5,
                                        fwzPmIndOfName(
                                            self.fpb_arg, i,
                                            0).getpmIndofName())  #棚面名
                                    sheet_kyinfo.write(row_ky, 6,
                                                       self.pzAllname[p])  #品种
                                    sheet_kyinfo.write(row_ky, 7,
                                                       self.pjAllname[d])  #品级
                                    sheet_kyinfo.write(
                                        row_ky, 8,
                                        int(new_ky_res[i][j][k][c][p][d]))  #数量
                                    row_ky += 1
        row_vir = 1
        for i in range(len(vir_ky)):  #棚面
            for j in range(len(vir_ky[i])):
                sheet_virinfo.write(row_vir, 0,
                                    pkhName[i][vir_ky[i][j][1]])  #客户名
                sheet_virinfo.write(row_vir, 1,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmOffwzName())  #服务站名
                sheet_virinfo.write(row_vir, 2,
                                    fwzPmIndOfName(self.fpb_arg, i,
                                                   0).getpmIndofName())  #棚面名
                sheet_virinfo.write(row_vir, 3,
                                    self.pzAllname[vir_ky[i][j][3]])  #品种
                sheet_virinfo.write(row_vir, 4,
                                    self.pjAllname[vir_ky[i][j][4]])  #品级
                sheet_virinfo.write(row_vir, 5, vir_ky[i][j][5])  #数量
                row_vir += 1

        if self.kyinfo_path == '':
            self.kyinfo_path = r'.\wenshi210701\output_tabel\调配信息表.xlsx'
        if os.path.exists(self.kyinfo_path):
            os.remove(self.kyinfo_path)
        table_info.save(self.kyinfo_path)
        print("调配信息表导出成功！")

    def readYhInfo(self):
        # kyinfo_path-调配信息表
        # 打开文件
        workbook = xlrd.open_workbook(self.kyinfo_path)
        # 根据sheet索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)  # sheet索引从0开始
        # sheet的名称，行数，列数
        # print(sheet1.name,sheet1.nrows,sheet1.ncols)
        row_num = sheet1.nrows
        func = lambda x, y: x if y in x else x + [y]
        #获取棚面名并去重
        self.pm_name = reduce(func, [
            [],
        ] + sheet1.col_values(2)[1:])
        pm_num = len(self.pm_name)
        pm_yh = [[] for i in range(pm_num)]
        for i in range(1, row_num):
            rows = sheet1.row_values(i)
            pm_yh[self.pm_name.index(rows[2])].append(rows)
        # deltai 每个棚面每个时间段养户配送情况
        deltai = []
        # n_detial 每个棚面的时间段区间
        n_detial = []
        for i in range(len(pm_yh)):
            n = [pm_yh[i][j][3] for j in range(len(pm_yh[i]))]
            n = reduce(func, [
                [],
            ] + n)
            n_detial.append(n)
            d_n = [{} for c in range(len(n))]
            for j in range(len(pm_yh[i])):
                if pm_yh[i][j][0] not in d_n[n.index(pm_yh[i][j][3])].keys():
                    d_n[n.index(pm_yh[i][j][3])][pm_yh[i][j][0]] = {}  # 养户名
                if pm_yh[i][j][4] not in d_n[n.index(
                        pm_yh[i][j][3])][pm_yh[i][j][0]].keys():  #
                    d_n[n.index(
                        pm_yh[i][j][3])][pm_yh[i][j][0]][pm_yh[i][j][4]] = {
                        }  # 品种名
                if pm_yh[i][j][5] not in d_n[n.index(pm_yh[i][j][3])][
                        pm_yh[i][j][0]][pm_yh[i][j][4]].keys():
                    d_n[n.index(pm_yh[i][j][3])][pm_yh[i][j][0]][
                        pm_yh[i][j][4]][pm_yh[i][j][5]] = 0  # 品级名
                d_n[n.index(pm_yh[i][j][3])][pm_yh[i][j][0]][pm_yh[i][j][4]][
                    pm_yh[i][j][5]] += int(pm_yh[i][j][6])  #数量
            deltai.append(d_n)
        return deltai, n_detial

    def deal_yh(self):
        # yh_detail 五重嵌套list 【棚面，养户，时间单元，品种，品级】
        # yhAllname 索引对应的养户名
        # yh_temp 棚面、养户、时间单元养户是否送货标志
        # pm_n 每个棚面的时间单元个数
        # yh_detail, yhAllname, yh_temp,pm_n = self.args
        # detail_value 每个棚面每个时间单元中养户送的品种品级数量
        # detail_name 每个棚面每个时间单元中养户的姓名
        # yh_name, yh_value, pz, pj = self.args
        yh_detail, n_detail = self.readYhInfo()
        # 存放排序后养户数据
        order_yh = [[[] for j in range(len(n_detail[i]))]
                    for i in range(len(n_detail))]
        use_info = [[[] for j in range(len(n_detail[i]))]
                    for i in range(len(n_detail))]
        for i in range(len(yh_detail)):  #棚面
            # temp用于存放每个时间单元上一时间单元合并该时间段的养户品种品级数量
            # {}内部存储形式如下-->
            # {养户名y1:[[品种a1,品级b1,数量],[品种a2,品级b2,数量],...],养户名y2:[[品种a1,品级b1,数量],[品种a2,品级b2,数量],...],..}
            temp = [{} for j in range(len(yh_detail[i]))]
            for j in range(len(yh_detail[i])):
                # yh1 = yh_detail[i][j] #该时间点的养户配送情况
                # {'罗居泉': {'麻黄鸡3号阉割': {'标准': 1000}}, '李爱枝': {'黄鸡2号阉割': {'标准': 400}},
                # '4罗耀辉1-06': {'玉香鸡母': {'标准': 1750}}, '苏玉燕': {'新矮脚黄鸡A公': {'标准': 0}},
                # '陈庆玲': {'天露草鸡公': {'标准': 400}},'梁文岳': {'玉香鸡公': {'标准': 50}},
                # '敖宝清（需还贷）': {'勒竹土鸡母': {'标准': 400},
                # '817（订单笼养）公': {'标准': 300}}, '莫癸庆': {'矮脚黄鸡D阉割': {'标准': 300}},
                # '陆海勇Y-120': {'勒竹土鸡公': {'标准': 800}}, '宋桂芬': {'优土2公': {'标准': 3000}}}
                yh1 = {}  #该时间点的养户配送情况
                ykey = list(yh_detail[i][j].keys())
                for yk in range(len(ykey)):
                    if ykey[yk] not in list(yh1.keys()):
                        yh1[ykey[yk]] = {}
                    pkey = list(yh_detail[i][j][ykey[yk]].keys())
                    for pk in range(len(pkey)):
                        if pkey[pk] not in list(yh1[ykey[yk]].keys()):
                            yh1[ykey[yk]][pkey[pk]] = {}
                        dkey = list(yh_detail[i][j][ykey[yk]][pkey[pk]].keys())
                        for dk in range(len(dkey)):
                            if dkey[dk] not in list(
                                    yh1[ykey[yk]][pkey[pk]].keys()):
                                yh1[ykey[yk]][pkey[pk]][dkey[dk]] = {}
                            yh1[ykey[yk]][pkey[pk]][dkey[dk]] = yh_detail[i][
                                j][ykey[yk]][pkey[pk]][dkey[dk]]
                yh2 = {}  #下一时间点的养户配送情况
                if j != len(yh_detail[i]) - 1:
                    # yh2 = yh_detail[i][j+1]
                    ykey = list(yh_detail[i][j + 1].keys())
                    for yk in range(len(ykey)):
                        if ykey[yk] not in list(yh2.keys()):
                            yh2[ykey[yk]] = {}
                        pkey = list(yh_detail[i][j + 1][ykey[yk]].keys())
                        for pk in range(len(pkey)):
                            if pkey[pk] not in list(yh2[ykey[yk]].keys()):
                                yh2[ykey[yk]][pkey[pk]] = {}
                            dkey = list(
                                yh_detail[i][j + 1][ykey[yk]][pkey[pk]].keys())
                            for dk in range(len(dkey)):
                                if dkey[dk] not in list(
                                        yh2[ykey[yk]][pkey[pk]].keys()):
                                    yh2[ykey[yk]][pkey[pk]][dkey[dk]] = {}
                                yh2[ykey[yk]][pkey[pk]][dkey[dk]] = yh_detail[
                                    i][j + 1][ykey[yk]][pkey[pk]][dkey[dk]]
                yh_name = []
                yh_value = []
                key_name = list(yh1.keys())
                use_name = list(temp[j].keys())
                use_name1 = []  #上一时间单元使用该时间段的养户名及其品种品级
                use_value1 = []  #上一时间单元使用该时间段的养户名及其品种品级的数量
                for ui in range(len(use_name)):
                    use_name1.append([use_name[ui],[temp[j][use_name[ui]][uj][0] for uj in range(len(temp[j][use_name[ui]]))],\
                        [temp[j][use_name[ui]][uj][1] for uj in range(len(temp[j][use_name[ui]]))]])
                    use_value1.append([
                        temp[j][use_name[ui]][uj][2]
                        for uj in range(len(temp[j][use_name[ui]]))
                    ])

                #去除该时间点可以与上一时间点并车的数据
                for k in range(len(key_name)):
                    pz_name = list(yh1[key_name[k]].keys())
                    for p in range(len(pz_name)):
                        pj_name = list(yh1[key_name[k]][pz_name[p]].keys())
                        for d in range(len(pj_name)):
                            if key_name[k] in use_name:
                                use_ind = use_name.index(key_name[k])
                                for t in range(len(
                                        temp[j][use_name[use_ind]])):
                                    if temp[j][use_name[use_ind]][t][0] == pz_name[p] and temp[j][use_name[use_ind]][t][1] == pj_name[d]\
                                         and yh1[key_name[k]][pz_name[p]][pj_name[d]] >= temp[j][use_name[use_ind]][t][2]:
                                        yh1[key_name[k]][pz_name[p]][
                                            pj_name[d]] -= temp[j][
                                                use_name[use_ind]][t][2]
                # 切分
                for k in range(len(key_name)):
                    pz_name = list(yh1[key_name[k]].keys())
                    t_name = [key_name[k], [], []]
                    t_value = []
                    for p in range(len(pz_name)):
                        pj_name = list(yh1[key_name[k]][pz_name[p]].keys())
                        for d in range(len(pj_name)):
                            t_name[1].append(pz_name[p])
                            t_name[2].append(pj_name[d])
                            t_value.append(
                                yh1[key_name[k]][pz_name[p]][pj_name[d]])
                    while sum(t_value) > self.carMaxNum:
                        sum_val = self.carMaxNum
                        val_dict = {}
                        for val in range(len(t_value)):
                            if t_value[val] > 0:
                                sum_val -= t_value[val]
                                if sum_val > 0:
                                    val_dict[val] = t_value[val]
                                    t_value[val] = 0
                                else:
                                    val_dict[val] = t_value[val] + sum_val
                                    t_value[val] = abs(sum_val)
                                    break
                        val_ind = list(val_dict.keys())
                        val_val = list(val_dict.values())
                        yh_name.append([
                            t_name[0], [t_name[1][n] for n in val_ind],
                            [t_name[2][n] for n in val_ind]
                        ])
                        yh_value.append(val_val)
                    if sum(t_value) > 0:
                        val_ind = list(np.where(np.array(t_value) > 0)[0])
                        yh_name.append([
                            t_name[0], [t_name[1][n] for n in val_ind],
                            [t_name[2][n] for n in val_ind]
                        ])
                        yh_value.append([t_value[n] for n in val_ind])
                        for n in val_ind:
                            t_value[n] = 0

                same_ind = []
                diff_ind = []
                key_name_next = list(yh2.keys())
                for n in range(len(yh_name)):
                    if (yh_name[n][0] in key_name_next) and sum(
                            yh_value[n]) < self.carMaxNum:
                        same_ind.append(n)
                        name_id = key_name_next.index(yh_name[n][0])
                        temp_num = sum(yh_value[n])
                        pz_name_next = list(yh2[key_name_next[name_id]].keys())
                        for p in range(len(pz_name_next)):
                            pj_name_next = list(yh2[key_name_next[name_id]][
                                pz_name_next[p]].keys())
                            for d in range(len(pj_name_next)):
                                if temp_num + yh2[key_name_next[name_id]][
                                        pz_name_next[p]][
                                            pj_name_next[d]] <= self.carMaxNum:
                                    temp_num += yh2[key_name_next[name_id]][
                                        pz_name_next[p]][pj_name_next[d]]
                                    if key_name_next[name_id] not in list(
                                            temp[j + 1].keys()):
                                        temp[j +
                                             1][key_name_next[name_id]] = []
                                    temp[j + 1][key_name_next[name_id]].append(
                                        [
                                            pz_name_next[p], pj_name_next[d],
                                            yh2[key_name_next[name_id]]
                                            [pz_name_next[p]][pj_name_next[d]]
                                        ])
                                    yh2[key_name_next[name_id]][
                                        pz_name_next[p]][pj_name_next[d]] = 0
                                else:
                                    cha = self.carMaxNum - temp_num
                                    temp_num = self.carMaxNum
                                    if key_name_next[name_id] not in list(
                                            temp[j + 1].keys()):
                                        temp[j +
                                             1][key_name_next[name_id]] = []
                                    temp[j + 1][key_name_next[name_id]].append(
                                        [
                                            pz_name_next[p], pj_name_next[d],
                                            cha
                                        ])
                                    yh2[key_name_next[name_id]][pz_name_next[
                                        p]][pj_name_next[d]] -= cha
                                if temp_num == self.carMaxNum:
                                    break
                            if temp_num == self.carMaxNum:
                                break
                    else:
                        diff_ind.append(n)

                if len(use_name) > 0:
                    #获取从小到大排序后索引相较于原来的位置
                    sort_ind0 = list(
                        np.argsort(
                            np.array([
                                sum(use_value1[nv])
                                for nv in range(len(use_value1))
                            ])))
                    #排序
                    uyh_name = [use_name1[ind] for ind in sort_ind0]
                    uyh_value = [use_value1[ind] for ind in sort_ind0]
                    for g in range(len(uyh_name)):
                        use_info[i][j].append([
                            uyh_name[g][0], uyh_name[g][1], uyh_name[g][2],
                            uyh_value[g]
                        ])
                        order_yh[i][j].append([
                            uyh_name[g][0], uyh_name[g][1], uyh_name[g][2],
                            uyh_value[g]
                        ])
                if len(diff_ind) > 0:
                    # 获取与下一时间段没有交集的养户名及其品种品级
                    nyh_name = [yh_name[ind] for ind in diff_ind]
                    # 获取与下一时间段没有交集的养户名及其品种品级对应的数量
                    nyh_value = [yh_value[ind] for ind in diff_ind]

                    #获取从大到小排序后索引相较于原来的位置
                    sort_ind1 = list(
                        np.argsort(-np.array([
                            sum(nyh_value[nv]) for nv in range(len(nyh_value))
                        ])))
                    #排序
                    nyh_name = [nyh_name[ind] for ind in sort_ind1]
                    nyh_value = [nyh_value[ind] for ind in sort_ind1]
                    for g in range(len(nyh_name)):
                        order_yh[i][j].append([
                            nyh_name[g][0], nyh_name[g][1], nyh_name[g][2],
                            nyh_value[g]
                        ])
                if len(same_ind) > 0:
                    # 获取与下一时间段有交集的养户名及其品种品级
                    yyh_name = [yh_name[ind] for ind in same_ind]
                    # 获取与下一时间段有交集的养户名及其品种品级对应的数量
                    yyh_value = [yh_value[ind] for ind in same_ind]
                    #获取从大到小排序后索引相较于原来的位置
                    sort_ind2 = list(
                        np.argsort(-np.array([
                            sum(yyh_value[nv]) for nv in range(len(yyh_value))
                        ])))
                    #排序
                    yyh_name = [yyh_name[ind] for ind in sort_ind2]
                    yyh_value = [yyh_value[ind] for ind in sort_ind2]
                    for g in range(len(yyh_name)):
                        order_yh[i][j].append([
                            yyh_name[g][0], yyh_name[g][1], yyh_name[g][2],
                            yyh_value[g]
                        ])
        return order_yh, use_info

    def deal_time(self):
        order_yh, use_info = self.deal_yh()
        # pm_st 用于存储每个棚面的每个时间段的开始时间
        pm_st = [['' for j in range(len(order_yh[i]))]
                 for i in range(len(order_yh))]
        for i in range(len(order_yh)):
            start_time = self.stList[i]
            for j in range(len(order_yh[i])):
                tbg = [start_time for u in range(self.pbgNum[i])]

                pm_st[i][j] = TimeTrans(start_time, 'h').trans()
                for n in range(len(order_yh[i][j])):  # 养户
                    index = tbg.index(min(tbg))
                    utime = math.ceil(
                        int(sum(order_yh[i][j][n][3])) / self.maxNum * 60)
                    ulen = len(use_info[i][j])
                    if n < ulen:  #TimeTrans(tbg[index]+utime,'h').trans()
                        use_info[i][j][n].append([
                            index + 1,
                            TimeTrans(tbg[index], 'h').trans() + "-" +
                            TimeTrans(tbg[index] + utime, 'h').trans()
                        ])
                    order_yh[i][j][n].append([
                        index + 1,
                        TimeTrans(tbg[index], 'h').trans() + "-" +
                        TimeTrans(tbg[index] + utime, 'h').trans()
                    ])
                    tbg[index] += utime
                tmax = max(tbg)
                start_time = tmax

        for i in range(len(use_info)):
            for j in range(len(use_info[i])):

                bg1 = [0 for u in range(self.pbgNum[i])]
                tnum = len(use_info[i][j])
                if j != 0:
                    num_list = []
                    oyh = []
                    for n in range(tnum):
                        if order_yh[i][j - 1][-(n + 1)][4][0] not in num_list:
                            num_list.append(order_yh[i][j - 1][-(n + 1)][4][0])
                            oyh.append(order_yh[i][j - 1][-(n + 1)])
                            if len(num_list) >= 4:
                                break
                    oyh.reverse()

                    use_name = [use_info[i][j][c][0] for c in range(tnum)]
                    oyh_name = [oyh[c][0] for c in range(len(oyh))]
                    for c in range(len(oyh_name)):
                        ind1 = use_name.index(oyh_name[c])
                        bg1[use_info[i][j][ind1][4][0] - 1] = oyh[c][4][0]

                for u in range(len(bg1)):
                    # print(bg1,i,j)
                    if u + 1 not in bg1:
                        ind_bg = bg1.index(0)
                        bg1[ind_bg] = u + 1

                for n in range(len(order_yh[i][j])):
                    order_yh[i][j][n][4][0] = bg1[order_yh[i][j][n][4][0] - 1]
                    ulen = len(use_info[i][j])
                    if n < ulen:
                        use_info[i][j][n][4][0] = bg1[use_info[i][j][n][4][0] -
                                                      1]
        return order_yh, use_info, pm_st

    def saveInfoExcel(self):
        order_yh, use_info, pm_st = self.deal_time()
        # print(order_yh[0][1][0:3])
        # ['勒竹1号棚面', '勒竹2号棚面', '新大地1号棚面', '稔村1号棚面', '稔村2号棚面', '车岗1号棚面', '车岗2号棚面', '新增服务站1号棚面']
        # 导出成为excel表-------------------------------------------------------------------------------------------------------
        table1 = xlwt.Workbook()  # 创建一个excel

        sheet1 = table1.add_sheet("养户调度表", cell_overwrite_ok=True)
        title1 = [
            '养户名', '服务站名', '棚面名', '时间段开始时间', '抵达时间', '装车总数量', '磅位1', '卸货时间区间1',
            '卸货品种1', '卸货品级1', '卸货数量1', '磅位2', '卸货时间区间2', '卸货品种2', '卸货品级2',
            '卸货数量2'
        ]
        i = 0
        for header in title1:
            sheet1.write(0, i, header)
            i += 1

        sheet2 = table1.add_sheet("养户调度表备用")
        title2 = [
            '养户名', '服务站名', '棚面名', '时间段开始时间', '抵达时间', '品种', '品级', '磅位',
            '卸货时间区间', '卸货数量'
        ]
        i = 0
        for header in title2:
            sheet2.write(0, i, header)
            i += 1

        # 设置样式
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour pink')
        style1_1 = xlwt.easyxf(
            'pattern: pattern solid, fore_colour pink; font: bold on')
        style2 = xlwt.easyxf(
            'pattern: pattern solid, fore_colour yellow; font: bold on')
        style3 = xlwt.easyxf('pattern: pattern solid, fore_colour ice_blue')
        style3_1 = xlwt.easyxf(
            'pattern: pattern solid, fore_colour ice_blue; font: bold on')

        # # 为指定单元格设置样式 --示例
        # sheets.write(0, 0, "hello girl", style)
        # 写入数据
        row_num = 1
        r1_num = 1
        for i in range(len(order_yh)):
            for j in range(len(order_yh[i])):
                ulen = len(use_info[i][j])
                if j != len(order_yh[i]) - 1:
                    next_yh = order_yh[i][j + 1][0:len(use_info[i][j + 1])]
                    next_name = [
                        next_yh[n][0] for n in range(len(use_info[i][j + 1]))
                    ]
                else:
                    next_yh = []
                    next_name = []
                n_sum = []
                n_num = 0  #每个棚面每个时间段计数
                if j % 2 == 0:
                    style = style1
                else:
                    style = style3
                for n in range(ulen, len(order_yh[i][j])):
                    # '0养户名','1服务站名','2棚面名','3时间段开始时间','4抵达时间','5装车总数量','6磅位1','7卸货时间区间1',
                    # '8卸货品种1','9卸货品级1','10卸货数量1','11磅位2','12卸货时间区间2','13卸货品种2','14卸货品级2',
                    # '15卸货数量2'
                    sheet1.write(row_num, 0, order_yh[i][j][n][0],
                                 style)  # 养户名
                    sheet1.write(row_num, 1,
                                 fwzPmIndOfName(self.fpb_arg, i,
                                                0).getpmOffwzName(),
                                 style)  # 服务站名
                    sheet1.write(row_num, 2,
                                 fwzPmIndOfName(self.fpb_arg, i,
                                                0).getpmIndofName(),
                                 style)  # 棚面名
                    sheet1.write(row_num, 3, pm_st[i][j], style)  # 时间段开始时间
                    sheet1.write(row_num, 4,
                                 order_yh[i][j][n][4][1].split("-")[0],
                                 style)  # 抵达时间
                    sheet1.write(row_num, 5, sum(order_yh[i][j][n][3]),
                                 style)  # 装车总数量
                    n_sum.append(sum(order_yh[i][j][n][3]))
                    sheet1.write(row_num, 6, order_yh[i][j][n][4][0],
                                 style)  # 磅位1
                    sheet1.write(row_num, 7, order_yh[i][j][n][4][1],
                                 style)  # 卸货时间区间1
                    sheet1.write(row_num, 8, str(order_yh[i][j][n][1]),
                                 style)  # 卸货品种1
                    sheet1.write(row_num, 9, str(order_yh[i][j][n][2]),
                                 style)  # 卸货品级1
                    sheet1.write(row_num, 10, str(order_yh[i][j][n][3]),
                                 style)  # 卸货数量1
                    sheet1.write(row_num, 11, None, style)  # 磅位2
                    sheet1.write(row_num, 12, None, style)  # 卸货时间区间2
                    sheet1.write(row_num, 13, None, style)  # 卸货品种2
                    sheet1.write(row_num, 14, None, style)  # 卸货品级2
                    sheet1.write(row_num, 15, None, style)  # 卸货数量2
                    row_num = row_num + 1
                    n_num = n_num + 1
                if j % 2 == 0:
                    style = style1_1
                else:
                    style = style3_1
                r1_num = row_num - 1
                # r_oyh = reversed((order_yh[i][j][ulen:len(order_yh[i][j])]))
                for n in range(
                        len(order_yh[i][j][ulen:len(order_yh[i][j])]) - 1, -1,
                        -1):
                    if len(next_name) == 0 and len(next_yh) == 0:
                        break
                    r_oyh = order_yh[i][j][ulen:len(order_yh[i][j])][n]
                    if r_oyh[0] in next_name and sum(
                            r_oyh[3]) < self.carMaxNum:
                        # data = ['a', 'b', 'c', 'd', 'b', 'b']
                        # print([i for i, x in enumerate(data) if x is "b"])
                        sum_1 = sum(r_oyh[3])
                        indlist = [
                            a for a, b in enumerate(next_name) if b is r_oyh[0]
                        ]
                        kv = {}
                        for ind in indlist:
                            if sum(next_yh[ind][3]) + sum(
                                    r_oyh[3]) <= self.carMaxNum:
                                kv[ind] = sum(next_yh[ind][3])
                        ind = max(kv, key=kv.get)
                        sum_1 += sum(next_yh[ind][3])
                        info_two = ['' for nu in range(6)]
                        while sum_1 <= self.carMaxNum:
                            n_sum[n] += sum(next_yh[ind][3])
                            if len(kv) > 0:
                                info_two[0] = n_sum[n]
                                info_two[1] += str(
                                    next_yh[ind][4][0]) + ','  # 磅位2
                                info_two[2] = self.timetrans(
                                    info_two[2],
                                    str(next_yh[ind][4][1]))  # 卸货时间区间2
                                info_two[3] += str(
                                    next_yh[ind][1]) + ','  # 卸货品种2
                                info_two[4] += str(
                                    next_yh[ind][2]) + ','  # 卸货品级2
                                info_two[5] += str(
                                    next_yh[ind][3]) + ','  # 卸货数量2

                            del kv[
                                ind]  # TimeTrans(info_two[1][:-1]).is_number()
                            if len(kv) == 0 or sum_1 >= self.carMaxNum:
                                sheet1.write(r1_num + n - n_num + 1, 5,
                                             info_two[0], style)
                                sheet1.write(
                                    r1_num + n - n_num + 1, 11,
                                    int(float(info_two[1][:-1]))
                                    if TimeTrans(info_two[1][:-1]).is_number()
                                    else info_two[1][:-1], style)  # 磅位2
                                sheet1.write(r1_num + n - n_num + 1, 12,
                                             info_two[2], style)  # 卸货时间区间2
                                sheet1.write(r1_num + n - n_num + 1, 13,
                                             info_two[3][:-1], style)  # 卸货品种2
                                sheet1.write(r1_num + n - n_num + 1, 14,
                                             info_two[4][:-1], style)  # 卸货品级2
                                sheet1.write(r1_num + n - n_num + 1, 15,
                                             info_two[5][:-1], style)  # 卸货数量2
                                del next_name[ind]
                                del next_yh[ind]
                                break
                            if len(kv) > 0:
                                ind = max(kv, key=kv.get)
                                sum_1 += sum(next_yh[ind][3])
                                if sum_1 > self.carMaxNum:
                                    # sum_1 -= next_yh[ind][3]
                                    sheet1.write(r1_num + n - n_num + 1, 5,
                                                 info_two[0], style)
                                    sheet1.write(r1_num + n - n_num + 1, 11,
                                                 info_two[1][:-1],
                                                 style)  # 磅位2
                                    sheet1.write(r1_num + n - n_num + 1, 12,
                                                 info_two[2], style)  # 卸货时间区间2
                                    sheet1.write(r1_num + n - n_num + 1, 13,
                                                 info_two[3][:-1],
                                                 style)  # 卸货品种2
                                    sheet1.write(r1_num + n - n_num + 1, 14,
                                                 info_two[4][:-1],
                                                 style)  # 卸货品级2
                                    sheet1.write(r1_num + n - n_num + 1, 15,
                                                 info_two[5][:-1],
                                                 style)  # 卸货数量2
                                    del next_name[ind]
                                    del next_yh[ind]
        #养户运送信息
        yhpInfo = []
        # 写入数据
        row_num = 1
        for i in range(len(order_yh)):
            for j in range(len(order_yh[i])):
                for n in range(len(order_yh[i][j])):
                    if j % 2 == 0:
                        style = style1
                    else:
                        style = style3
                    ulen = len(use_info[i][j])
                    if n < ulen:
                        style = style2
                    # '养户名','服务站名','棚面名','时间段开始时间','抵达时间','品种','品级','磅位','卸货时间区间','卸货数量'
                    sheet2.write(row_num, 0, order_yh[i][j][n][0], style)
                    sheet2.write(
                        row_num, 1,
                        fwzPmIndOfName(self.fpb_arg, i, 0).getpmOffwzName(),
                        style)
                    sheet2.write(
                        row_num, 2,
                        fwzPmIndOfName(self.fpb_arg, i, 0).getpmIndofName(),
                        style)
                    sheet2.write(row_num, 3, pm_st[i][j], style)
                    sheet2.write(row_num, 4,
                                 order_yh[i][j][n][4][1].split("-")[0], style)

                    sheet2.write(row_num, 5, str(order_yh[i][j][n][1]), style)
                    sheet2.write(row_num, 6, str(order_yh[i][j][n][2]), style)
                    sheet2.write(row_num, 7, order_yh[i][j][n][4][0], style)
                    sheet2.write(row_num, 8, order_yh[i][j][n][4][1], style)
                    sheet2.write(row_num, 9, str(order_yh[i][j][n][3]), style)
                    # 养户名 服务站名 棚面名 时间段开始时间 品种 品级 磅位
                    yhpInfo.append([order_yh[i][j][n][0],fwzPmIndOfName(self.fpb_arg,i,0).getpmOffwzName(),\
                        fwzPmIndOfName(self.fpb_arg,i,0).getpmIndofName(),pm_st[i][j],order_yh[i][j][n][1],\
                            order_yh[i][j][n][2],order_yh[i][j][n][4][0]])

                    row_num = row_num + 1

        if self.yh_path == '':
            self.yh_path = r'.\wenshi210701\output_table\养户调度表.xlsx'
        if os.path.exists(self.yh_path):
            os.remove(self.yh_path)
        table1.save(self.yh_path)
        print("养户调度表导出成功！")

        sheet_kh = table1.add_sheet("客户调度表")
        title3 = ['客户名', '服务站名', '棚面名', '抵达时间', '品种', '品级', '数量']
        i = 0
        for header in title3:
            sheet_kh.write(0, i, header)
            i += 1

        sheet_ky = table1.add_sheet("客户与养户匹配调度表")
        title4 = [
            '客户名', '车次', '养户名（车次所属养户）', '时间段开始时间', '服务站名', '棚面名', '磅位', '品种',
            '品级', '数量'
        ]
        i = 0
        for header in title4:
            sheet_ky.write(0, i, header)
            i += 1

        # 打开文件
        workbook1 = xlrd.open_workbook(self.yh_path)  # 养户调度表
        workbook2 = xlrd.open_workbook(self.kyinfo_path)  # 调配信息表
        # 获取所有sheet
        sheetnames1 = workbook1.sheet_names()
        func = lambda x, y: x if y in x else x + [y]
        sname = '养户调度表备用'
        n_time_new = []
        if sname not in sheetnames1:
            error("养户调度表中不存在'" + sname + "'部分")
        ind = sheetnames1.index(sname)
        sheet1 = workbook1.sheet_by_index(ind)
        row_num = sheet1.nrows
        col_num = sheet1.ncols
        pm_name = reduce(func, [
            [],
        ] + sheet1.col_values(2)[1:])
        n_time_new = [[] for i in range(len(pm_name))]
        for i in range(1, row_num):
            pmind = pm_name.index(sheet1.row_values(i)[2])
            n_time_new[pmind].append(sheet1.row_values(i)[3])
        for i in range(len(n_time_new)):
            n_time_new[i] = reduce(func, [
                [],
            ] + n_time_new[i])

        kname = '客户表'
        kyname = '客户与养户车次对应表'
        sheetnames2 = workbook2.sheet_names()
        if kname not in sheetnames2:
            error("调配信息表表中不存在'" + kname + "'部分")
        if kyname not in sheetnames2:
            error("调配信息表表中不存在'" + kyname + "'部分")
        ind = sheetnames2.index(kname)
        sheet2 = workbook2.sheet_by_index(ind)
        row_num = sheet2.nrows
        n_time_old = [[] for j in range(len(pm_name))]
        for i in range(1, row_num):
            pmind = pm_name.index(sheet2.row_values(i)[2])
            n_time_old[pmind].append(sheet2.row_values(i)[3])
        for i in range(len(n_time_old)):
            n_time_old[i] = reduce(func, [
                [],
            ] + n_time_old[i])
        for i in range(1, row_num):
            vallist = sheet2.row_values(i)
            row_val = [vallist[k] for k in range(len(vallist))]
            row_val[3] = n_time_new[pm_name.index(
                row_val[2])][n_time_old[pm_name.index(row_val[2])].index(
                    row_val[3])]
            for j in range(len(row_val)):
                sheet_kh.write(i, j, row_val[j])
        kyind = sheetnames2.index(kyname)
        kysheet = workbook2.sheet_by_index(kyind)
        row_num = kysheet.nrows

        for i in range(1, row_num):
            vallist = kysheet.row_values(i)
            row_val = [vallist[k] for k in range(len(vallist))]
            row_val[3] = n_time_new[pm_name.index(
                row_val[5])][n_time_old[pm_name.index(row_val[5])].index(
                    row_val[3])]
            for j in range(len(row_val)):
                # yhpInfo
                if j < 6:
                    sheet_ky.write(i, j, row_val[j])
                    if j == 5:
                        # 养户名 服务站名 棚面名 时间段开始时间 品种 品级 磅位
                        ind_curr = [1 if yhpInfo[a][0] == row_val[2] and yhpInfo[a][1] == row_val[4]\
                             and  yhpInfo[a][2] == row_val[5]  and  yhpInfo[a][3] == row_val[3]\
                                  and  row_val[6] in yhpInfo[a][4] and  str(row_val[7]) in yhpInfo[a][5] else 0 for a in range(len(yhpInfo))]

                        sheet_ky.write(i, j + 1, yhpInfo[ind_curr.index(1)][6])
                else:
                    sheet_ky.write(i, j + 1, row_val[j])

        if self.ky_path == '':
            self.ky_path = r'.\wenshi210701\output_table\调配结果信息表.xlsx'
        if os.path.exists(self.ky_path):
            os.remove(self.ky_path)
        table1.save(self.ky_path)
        print("调配结果信息表导出成功！")

    def saveKhExcel(self):
        # 打开文件
        workbook1 = xlrd.open_workbook(self.yh_path)  # 养户调度表
        workbook2 = xlrd.open_workbook(self.kyinfo_path)  # 调配信息表
        # 获取所有sheet
        sheetnames1 = workbook1.sheet_names()
        func = lambda x, y: x if y in x else x + [y]
        sname = '养户调度表备用'
        n_time_new = []
        if sname not in sheetnames1:
            error("养户调度表中不存在'" + sname + "'部分")
        ind = sheetnames1.index(sname)
        sheet1 = workbook1.sheet_by_index(ind)
        row_num = sheet1.nrows
        col_num = sheet1.ncols
        pm_name = reduce(func, [
            [],
        ] + sheet1.col_values(2)[1:])
        n_time_new = [[] for i in range(len(pm_name))]
        for i in range(1, row_num):
            pmind = pm_name.index(sheet1.row_values(i)[2])
            n_time_new[pmind].append(sheet1.row_values(i)[3])
        for i in range(len(n_time_new)):
            n_time_new[i] = reduce(func, [
                [],
            ] + n_time_new[i])

        table1 = xlwt.Workbook()  # 创建一个excel
        sheet_kh = table1.add_sheet("客户调度表")
        title1 = ['客户名', '服务站名', '棚面名', '抵达时间', '品种', '品级', '数量']
        i = 0
        for header in title1:
            sheet_kh.write(0, i, header)
            i += 1
        table2 = xlwt.Workbook()  # 创建一个excel
        sheet_ky = table2.add_sheet("客户与养户匹配调度表")
        title2 = [
            '客户名', '车次', '养户名（车次所属养户）', '时间段开始时间', '服务站名', '棚面名', '品种', '品级',
            '数量'
        ]
        i = 0
        for header in title2:
            sheet_ky.write(0, i, header)
            i += 1
        kname = '客户表'
        kyname = '客户与养户车次对应表'
        sheetnames2 = workbook2.sheet_names()  # [u'sheet1', u'sheet2']
        if kname not in sheetnames2:
            error("调配信息表表中不存在'" + kname + "'部分")
        if kyname not in sheetnames2:
            error("调配信息表表中不存在'" + kyname + "'部分")
        ind = sheetnames2.index(kname)
        sheet2 = workbook2.sheet_by_index(ind)
        row_num = sheet2.nrows
        n_time_old = [[] for j in range(len(pm_name))]
        for i in range(1, row_num):
            pmind = pm_name.index(sheet2.row_values(i)[2])
            n_time_old[pmind].append(sheet2.row_values(i)[3])
        for i in range(len(n_time_old)):
            n_time_old[i] = reduce(func, [
                [],
            ] + n_time_old[i])
        for i in range(1, row_num):
            vallist = sheet2.row_values(i)
            row_val = [vallist[k] for k in range(len(vallist))]
            row_val[3] = n_time_new[pm_name.index(
                row_val[2])][n_time_old[pm_name.index(row_val[2])].index(
                    row_val[3])]
            for j in range(len(row_val)):
                sheet_kh.write(i, j, row_val[j])
        kyind = sheetnames2.index(kyname)
        kysheet = workbook2.sheet_by_index(kyind)
        row_num = kysheet.nrows

        for i in range(1, row_num):
            vallist = kysheet.row_values(i)
            row_val = [vallist[k] for k in range(len(vallist))]
            row_val[3] = n_time_new[pm_name.index(
                row_val[5])][n_time_old[pm_name.index(row_val[5])].index(
                    row_val[3])]
            for j in range(len(row_val)):
                sheet_ky.write(i, j, row_val[j])
        if self.kh_path == '':
            self.kh_path = r'.\wenshi210701\output_tabel\客户调度表.xls'
        if os.path.exists(self.kh_path):
            os.remove(self.kh_path)
        table1.save(self.kh_path)
        print("客户调度表导出成功！")
        if self.ky_path == '':
            self.ky_path = r'.\wenshi210701\output_tabel\客户与养户匹配调度表.xls'
        if os.path.exists(self.ky_path):
            os.remove(self.ky_path)
        table2.save(self.ky_path)
        print("客户与养户匹配调度表导出成功！")

    def dealky(self):
        # 打开文件
        wk = xlrd.open_workbook(self.yh_path)
        sheet_yhname = wk.sheet_names()
        table_name = '养户调度表'
        if table_name not in sheet_yhname:
            error('选择的excel表中不存在\'养户调度表\'部分')
        yhind = sheet_yhname.index(table_name)
        curr_sheet = wk.sheet_by_index(yhind)
        row_num = curr_sheet.nrows
        col_num = curr_sheet.ncols

        func = lambda x, y: x if y in x else x + [y]
        #获取棚面名并去重
        curr_pm_name = reduce(func, [
            [],
        ] + curr_sheet.col_values(2)[1:])
        pm_tn1 = [[] for i in range(len(curr_pm_name))]  #每个棚面时间段原开始时间
        pttable = [{} for i in range(len(curr_pm_name))]
        for i in range(1, row_num):
            curr_row = curr_sheet.row_values(i)
            if curr_row[2] not in curr_pm_name:
                error('无此棚面')
            pid = curr_pm_name.index(curr_row[2])

            if curr_row[3] not in pm_tn1[curr_pm_name.index(curr_row[2])]:
                pm_tn1[curr_pm_name.index(curr_row[2])].append(curr_row[3])
            if curr_row[3] not in list(pttable[pid].keys()):
                pttable[pid][curr_row[3]] = []
            pttable[pid][curr_row[3]].append(curr_row)
        # pm_st 用于存储每个棚面的每个时间段的开始时间
        pm_st = [['' for j in range(len(list(pttable[i].keys())))]
                 for i in range(len(pttable))]
        new_row = []
        for i in range(len(pttable)):
            stime = self.stList[i]
            tbg = [stime for u in range(self.pbgNum[i])]
            pkey = list(pttable[i].keys())
            for p in range(len(pkey)):  # TimeTrans(stime,'h').trans()
                pm_st[i][p] = TimeTrans(stime, 'h').trans()
                curr_kv = pttable[i][pkey[p]]
                curr_kv.sort(key=lambda data: (-int(data[5])), reverse=False)
                for j in range(len(curr_kv)):
                    curr_row = curr_kv[j]
                    index = tbg.index(min(tbg))
                    utime = math.ceil(int(curr_row[5]) / self.maxNum * 60)
                    curr_row[10] = re.split(r'[\[\],]', curr_row[10])
                    curr_row[10] = [
                        item
                        for item in filter(lambda x: x != '', curr_row[10])
                    ]
                    # print(curr_row[10])
                    # curr_num_list = curr_row[10][0].split(',')
                    curr_num_list = [int(item) for item in curr_row[10]]
                    curr_row[8] = list(
                        filter(None, re.split(r'[\[\'\,\]]', curr_row[8])))
                    curr_row[9] = list(
                        filter(None, re.split(r'[\[\'\,\]]', curr_row[9])))
                    # print(sum(curr_num_list),int(curr_row[5]))
                    if sum(curr_num_list) == int(
                            curr_row[5]
                    ):  # TimeTrans(tbg[index]+utime,'h').trans()
                        new_row.append([curr_row[0],curr_row[1],curr_row[2],pm_st[i][p],TimeTrans(tbg[index],'h').trans(),int(curr_row[5]),\
                            index+1,TimeTrans(tbg[index],'h').trans()+"-"+TimeTrans(tbg[index]+utime,'h').trans(),curr_row[8],curr_row[9],\
                                curr_row[10][0],curr_row[12],curr_row[13],curr_row[14],curr_row[15]])
                    else:
                        u1time = math.ceil(
                            int(sum(curr_num_list)) / self.maxNum * 60)
                        curr_row[15] = re.split(r'[\[\],]', curr_row[15])
                        curr_row[15] = [
                            item
                            for item in filter(lambda x: x != '', curr_row[15])
                        ]
                        # print(curr_row[15])
                        curr_num_list1 = curr_row[15][0].split(',')
                        curr_num_list1 = [int(item) for item in curr_num_list1]
                        u2time = math.ceil(
                            int(sum(curr_num_list1)) / self.maxNum * 60)
                        utime = u1time + u2time
                        curr_row[13] = re.split(r'[\[\]]', curr_row[13])
                        curr_row[14] = re.split(
                            r'[\[\]]',
                            curr_row[14])  #TimeTrans(tbg[index],'h').trans()
                        new_row.append([curr_row[0],curr_row[1],curr_row[2],pm_st[i][p],TimeTrans(tbg[index],'h').trans(),int(curr_row[5]),\
                            index+1,TimeTrans(tbg[index],'h').trans()+"-"+TimeTrans(tbg[index]+u1time,'h').trans(),curr_row[8],curr_row[9],\
                                curr_row[10][0],TimeTrans(tbg[index]+u1time,'h').trans()+"-"+TimeTrans(tbg[index]+utime,'h').trans(),curr_row[13],\
                                    curr_row[14],curr_row[15][0]])
                    tbg[index] += utime
                tmin = min(tbg)
                stime = tmin

        return new_row, curr_pm_name, pm_st, pm_tn1

    def save_new_table(self):
        new_yh_row, curr_pm_name, pm_st, pm_tn1 = self.dealky()
        for i in range(len(curr_pm_name)):  #TimeTrans(data).trans()
            pm_st[i].sort(key=lambda data: (TimeTrans(data).trans()),
                          reverse=False)
            pm_tn1[i].sort(key=lambda data: (TimeTrans(data).trans()),
                           reverse=False)
        # 打开文件
        wk = xlrd.open_workbook(self.ky_path)  #调度结果信息表
        print(wk.sheet_names())
        sheet_name = wk.sheet_names()
        kh_name_ind = sheet_name.index('客户调度表')
        ky_name_ind = sheet_name.index('客户与养户匹配调度表')
        curr_kh_sheet = wk.sheet_by_index(kh_name_ind)
        curr_ky_sheet = wk.sheet_by_index(ky_name_ind)

        row_num_kh = curr_kh_sheet.nrows
        row_num_ky = curr_ky_sheet.nrows
        # 导出成为excel表-------------------------------------------------------------------------------------------------------
        new_table = xlwt.Workbook()  # 创建一个excel

        new_yh_sheet = new_table.add_sheet("新养户调度表", cell_overwrite_ok=True)
        new_yh_title = [
            '养户名', '服务站名', '棚面名', '时间段开始时间', '抵达时间', '装车总数量', '磅位', '卸货时间区间1',
            '卸货品种1', '卸货品级1', '卸货数量1', '卸货时间区间2', '卸货品种2', '卸货品级2', '卸货数量2'
        ]
        i = 0
        for header in new_yh_title:
            new_yh_sheet.write(0, i, header)
            i += 1
        new_kh_sheet = new_table.add_sheet("新客户调度表", cell_overwrite_ok=True)
        new_kh_title = ['客户名', '服务站名', '棚面名', '抵达时间', '品种', '品级', '数量']
        i = 0
        for header in new_kh_title:
            new_kh_sheet.write(0, i, header)
            i += 1
        new_ky_sheet = new_table.add_sheet("新客户与养户匹配调度表",
                                           cell_overwrite_ok=True)
        new_ky_title = [
            '客户名', '车次', '养户名（车次所属养户）', '时间段开始时间', '服务站名', '棚面名', '磅位', '品种',
            '品级', '数量'
        ]
        i = 0
        for header in new_ky_title:
            new_ky_sheet.write(0, i, header)
            i += 1
        #养户运送信息
        yhpInfo = []
        row_yh_num = 1
        for i in range(len(new_yh_row)):
            for j in range(len(new_yh_row[i])):
                new_yh_sheet.write(row_yh_num, j, new_yh_row[i][j])
            row_yh_num += 1
        row_kh_num = 1
        for i in range(1, row_num_kh):
            curr_row = curr_kh_sheet.row_values(i)
            for j in range(len(curr_row)):
                if j == 3:
                    if curr_row[j] not in pm_tn1[curr_pm_name.index(
                            curr_row[2])]:
                        curr_row[j] = pm_tn1[curr_pm_name.index(
                            curr_row[2])][-1]
                    curr_row[j] = pm_st[curr_pm_name.index(
                        curr_row[2])][pm_tn1[curr_pm_name.index(
                            curr_row[2])].index(curr_row[j])]
                new_kh_sheet.write(row_kh_num, j, curr_row[j])
            row_kh_num += 1
        ky_data = []
        for i in range(1, row_num_ky):
            curr_row = curr_ky_sheet.row_values(i)
            for j in range(len(curr_row)):
                if j == 3:
                    if curr_row[j] not in pm_tn1[curr_pm_name.index(
                            curr_row[5])]:
                        curr_row[j] = pm_tn1[curr_pm_name.index(
                            curr_row[5])][-1]
                    curr_row[j] = pm_st[curr_pm_name.index(
                        curr_row[5])][pm_tn1[curr_pm_name.index(
                            curr_row[5])].index(curr_row[j])]
            ky_data.append(curr_row)
        row_ky_num = 1
        for i in range(len(ky_data)):
            for j in range(len(ky_data[i])):
                if j == 6:
                    # 养户名 服务站名 棚面名 时间段开始时间 品种 品级 磅位
                    ind_curr = [1 if new_yh_row[a][0] == ky_data[i][2] and new_yh_row[a][1] == ky_data[i][4]\
                        and  new_yh_row[a][2] == ky_data[i][5]  and  new_yh_row[a][3] == ky_data[i][3]\
                            and  (ky_data[i][7] in new_yh_row[a][8] or ky_data[i][7] in new_yh_row[a][12])\
                                 and  (str(ky_data[i][8]) in new_yh_row[a][9] or str(ky_data[i][8]) in new_yh_row[a][13])\
                                      else 0 for a in range(len(new_yh_row))]
                    ky_data[i][j] = new_yh_row[ind_curr.index(1)][6]
                new_ky_sheet.write(row_ky_num, j, ky_data[i][j])
            row_ky_num += 1

        if os.path.exists(self.new_path):
            os.remove(self.new_path)
        new_table.save(self.new_path)
        print("新调度结果表导出成功！")

    def dealVirInfo(self, ynpp_res, knpp_res, vir_ky):
        # ynpp_res-每个棚面每个时间单元每辆车次送品种品级鸡数
        # knpp_res-每个棚面每个时间单元每个客户取品种品级鸡数
        for i in range(len(vir_ky)):  #棚面
            for j in range(len(vir_ky[i])):
                vir_list = vir_ky[i][j]  # 时间单元 客户索引 车次索引 品种 品级 数量
                knpp_res[i][vir_list[0]][vir_list[1]][vir_list[3]][
                    vir_list[4]] = knpp_res[i][vir_list[0]][vir_list[1]][
                        vir_list[3]][vir_list[4]] - vir_list[5]
                ynpp_res[i][vir_list[0]][vir_list[2]][vir_list[3]][
                    vir_list[4]] = ynpp_res[i][vir_list[0]][vir_list[2]][
                        vir_list[3]][vir_list[4]] - vir_list[5]
        return ynpp_res, knpp_res

    def saveResult(self):
        # ynpp_res-每个棚面每个时间单元每辆车次送品种品级鸡数
        # knpp_res-每个棚面每个时间单元每个客户取品种品级鸡数
        # fktYn-每个服务站每个养户已经开始卸货车辆卸货所属时间单元
        # fktYse-每个服务站每个养户已知的最早开始卸货时间和最晚卸货时间单元
        # ky_res-每个棚面每个时间单元每个客户从每辆车取品种品级鸡数
        # ky_path-调配结果表存储位置
        # stList-每个棚面开始时间
        pkhName, carpYhInd, use_yhAllname, pz, pj, pzlist, pjlist, ynpp_res, knpp_res, fktYn, fktYse, ky_res, vir_ky, stList, pbgNum, carMaxNum, maxNum, Nlen = self.args_ky
        #处理虚拟订单
        ynpp_res, knpp_res = self.dealVirInfo(ynpp_res, knpp_res, vir_ky)

        self.yh_path, self.ky_path, self.new_path, self.kyinfo_path = self.args_path
        self.pzAllname = pzlist
        self.pjAllname = pjlist
        self.stList = stList
        self.pbgNum = pbgNum
        self.maxNum = maxNum
        self.carMaxNum = carMaxNum
        self.Nlen = Nlen
        self.save_ky_excel(ynpp_res, knpp_res, ky_res, vir_ky, pkhName,
                           carpYhInd, use_yhAllname, pz, pj)
        self.saveInfoExcel()
        try:
            self.save_new_table()
        except:
            print("新调度结果表导出失败！")

        # table_ky = xlwt.Workbook()  # 创建一个excel

        # sheet_kh = table_ky.add_sheet("客户结果信息表")
        # title_kh = ['客户名', '服务站名', '棚面名', '开始取货时间', '品种', '品级', '数量']
        # i = 0
        # for header in title_kh:
        #     sheet_kh.write(0, i, header)
        #     i += 1
        # sheet_yh = table_ky.add_sheet("养户结果信息表")
        # title_yh = ['养户名', '服务站名', '棚面名', '磅位','抵达时间','卸货区间','品种', '品级', '数量']
        # i = 0
        # for header in title_yh:
        #     sheet_yh.write(0, i, header)
        #     i += 1
        # sheet_ky = table_ky.add_sheet("客户与养户结果信息匹配表")
        # title_ky = ['客户名', '服务站名', '棚面名', '养户名','品种', '品级', '数量']
        # i = 0
        # for header in title_ky:
        #     sheet_ky.write(0, i, header)
        #     i += 1

        # row_kh = 1
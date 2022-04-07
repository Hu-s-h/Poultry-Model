# 小时转分钟  分钟转时分

from logging import error


class TimeTrans():
    def __init__(self,contents,format='m'):
        # orgfm-原格式 format-转换格式 
        # m-转分钟 h-转几时几分
        self.format = format 
        if self.format not in ['m','h']:
            self.format = 'm'
        self.contents = contents
    def is_number(self):
        try:
            float(self.contents)
            return True
        except ValueError:
            pass
        # 把一个表示数字的字符串转换为浮点数返回
        # try:
        #     import unicodedata
        #     unicodedata.numeric(s)
        #     return True
        # except (TypeError, ValueError):
        #     pass
        return False
    def trans(self):
        #预计时间为纯数字
        if self.is_number():
            if self.format == 'm':
                return int(self.contents)*60
            else:
                h = int(self.contents)//60
                m = int(self.contents)%60
                if h<10:
                    sh = "0"+str(h)
                else:
                    sh = str(h)
                if m<10:
                    sm = "0"+str(m)
                else:
                    sm = str(m)
                ts = sh+":"+sm
                return ts
        try:
            times = self.contents.strip().split('~')[0]
            if self.format == 'm':
                hm = times.split(':')
                ss = 0
                if len(hm)==2:
                    h = hm[0]
                    m = hm[1]
                elif len(hm)==3:
                    h = hm[0]
                    m = hm[1]
                    t = hm[2]
                    if int(t)>0:
                        ss = 1
                else:
                    error('格式不支持')
                return int(h) * 60 + int(m) + ss
            else:
                h = int(times)//60
                m = int(times)%60
                return str(h)+':'+str(m)
        except:
            pass

        return 'error'   

# -*- coding: utf-8 -*-
# @Author: jmx
# @Date:   2019-04-22 16:38:29
# @Last Modified by:   jmx
# @Last Modified time: 2019-04-22 16:38:35
# -*- coding: utf-8 -*-
# @Author: root
# @Date:   2019-04-22 11:17:30
# @Last Modified by:   root
# @Last Modified time: 2019-04-22 16:36:10
import platform
import os


def prmsg(str):
    print(''.center(len(str)+40, '*')+'\n')
    print(str.center(40, ' ')+'\n')
    print(''.center(len(str)+40, '*')+'\n')


class liunxCron():
    """docstring for addcrontab"""
    cycleTyle = ['每月', '每星期', '每天', '每小时', 'N天', 'N小时', 'N分钟']
    weeks = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    def __init__(self):
        cycleTyle = ''
        for i in range(len(self.cycleTyle)):
            cycleTyle += str(i+1)+'.'+self.cycleTyle[i]+'\n'
        try:
            cycle = int(input('请选择执行周期：（默认1）\n%s' % cycleTyle))
            if(cycle >= 1 & cycle <= len(self.cycleTyle) & isinstance(cycle, int)):
                pass
            else:
                cycle = 1
        except:
            cycle = 1
        prmsg('您选择的是：%s' % self.cycleTyle[cycle-1])
        self.config = self.GetCrondCycle(cycle)

    def getDays(self):
        try:
            days = int(input('请输入每月1到31号（默认1日）：'))
            if(days < 1 | days > 31 | isinstance(days, int) == False):
                days = 1
        except:
            days = 1
        prmsg('您输入的是：%s日' % str(days))
        return str(days)

    def getWeek(self):
        weekStr = ''
        for i in range(len(self.weeks)):
            weekStr += str(i+1)+'.'+self.weeks[i]+'\n'
        try:
            week = int(input('请选择下面选项（默认周一）：\n'+weekStr))
            if(week < 1 | week > 7 | isinstance(week, int) == False):
                week = 1
        except:
            week = 1
        prmsg('您输入的是：%s' % self.weeks[week-1])
        return str(week)

    def getHour(self):
        try:
            hour = int(input('请输入0到23时（默认0时）：'))
            if(hour < 0 | hour > 23 | isinstance(hour, int) == False):
                hour = 0
        except:
            hour = 0
        prmsg('您输入的是：%s时' % str(hour))
        return str(hour)

    def getMinute(self):
        try:
            minute = int(input('请输入0到59分钟（默认0分钟）：'))
            if(minute < 0 | minute > 59 | isinstance(minute, int) == False):
                minute = 0
        except:
            minute = 0
        prmsg('您输入的是：%s分钟' % str(minute))
        return str(minute)

    def getScript(self):
        script = input('请输出sh脚本路径：')
        if not os.path.exists(script):
            prmsg('sh脚本路径不存在')
            return False
        prmsg('您输入的路径是：%s' % script)
        return script

    def GetCrondCycle(self, param):
        params = {}
        cuonConfig = ""
        if param == 3:
            params['hour'] = self.getHour()
            params['minute'] = self.getMinute()
            cuonConfig = self.Day(params)
        elif param == 5:
            params['days'] = self.getDays()
            params['hour'] = self.getHour()
            params['minute'] = self.getMinute()
            cuonConfig = self.Day_N(params)
        elif param == 4:
            params['minute'] = self.getMinute()
            cuonConfig = self.Hour(params)
        elif param == 6:
            params['hour'] = self.getHour()
            params['minute'] = self.getMinute()
            cuonConfig = self.Hour_N(params)
        elif param == 7:
            params['minute'] = self.getMinute()
            cuonConfig = self.Minute_N(params)
        elif param == 2:
            params['week'] = self.getWeek()
            params['hour'] = self.getHour()
            params['minute'] = self.getMinute()
            cuonConfig = self.Week(params)
        elif param == 1:
            params['days'] = self.getDays()
            params['hour'] = self.getHour()
            params['minute'] = self.getMinute()
            cuonConfig = self.Month(params)
        script = self.getScript()
        if(script == False):
            exit()
        return cuonConfig+' '+script+' >> ' + script + '.log 2>&1'

    # 取任务构造Day
    def Day(self, param):
        cuonConfig = "{0} {1} * * * ".format(param['minute'], param['hour'])
        return cuonConfig
    # 取任务构造Day_n

    def Day_N(self, param):
        cuonConfig = "{0} {1} */{2} * * ".format(
            param['minute'], param['hour'], param['days'])
        return cuonConfig

    # 取任务构造Hour
    def Hour(self, param):
        cuonConfig = "{0} * * * * ".format(param['minute'])
        return cuonConfig

    # 取任务构造Hour-N
    def Hour_N(self, param):
        cuonConfig = "{0} */{1} * * * ".format(
            param['minute'], param['hour'])
        return cuonConfig

    # 取任务构造Minute-N
    def Minute_N(self, param):
        cuonConfig = "*/{0} * * * * ".format(param['minute'])
        return cuonConfig

    # 取任务构造week
    def Week(self, param):
        cuonConfig = "{0} {1} * * {2}".format(
            param['minute'], param['hour'], param['week'])
        return cuonConfig

    # 取任务构造Month
    def Month(self, param):
        cuonConfig = "{0} {1} {2} * * ".format(
            param['minute'], param['hour'], param['days'])
        return cuonConfig

    def CrondReload(self):
        prmsg('开始重置配置')
        if os.path.exists('/etc/init.d/crond'):
            os.system('/etc/init.d/crond reload')
        elif os.path.exists('/etc/init.d/cron'):
            os.system('service cron restart')
        else:
            os.system("systemctl reload crond")

    def WriteShell(self):
        u_file = '/var/spool/cron/crontabs'
        if not os.path.exists(u_file):
            file = '/var/spool/cron/root'
        else:
            file = u_file+'/root'

        if not os.path.exists(file):
            open(file, 'w').close()

        prmsg('开始写入shell')
        cron = open(file).read()+self.config+'\n'
        open(file, 'w').write(cron)
        prmsg('开始修改文件权限')
        if not os.path.exists(u_file):
            os.system("chmod 600 '" + file + "' && chown root.root " + file)
        else:
            os.system("chmod 600 '" + file + "' && chown root.crontab " + file)
        self.CrondReload()

    def __del__(self):
        prmsg('定时任务设置完成')


if __name__ == '__main__':
    if(platform.system() == 'Windows'):
        print('Windows系统')
    elif(platform.system() == 'Linux'):
        print('Linux系统')
        cron = liunxCron().WriteShell()
    else:
        print('暂不支持')

import subprocess
import re
import time
from apm.conf_oprate import confLoad
conf = confLoad()


class AdbException(Exception):

    def __init__(self, *args):
        self.args = args


def get_name_from_device(device):
    """

    :param device: 1.2.3.4:5555
    :return: xiaomi8
    """
    return [i.get("device_info") for i in conf.devices if i.get("device_ip") == device.split(":")[0]][0]


class AdbPackage(object):

    def __init__(self, device):
        self.device = device

    def _get_pid(self, package):
        cmd = "{} -s {} shell \"ps |grep -e \\\"{}$\\\"\"".format(conf.adb_path, self.device, package)
        result = subprocess.getoutput(cmd).rstrip().split("\n")
        if len(result[0]) == 0:
            print("{} can not find the pid of {}".format(get_name_from_device(self.device), package))
            raise AdbException("can not find pid of {}".format(package))
        for ps_info in result:
            if ps_info.split()[-1] == package:
                return ps_info.split()[1]
        raise AdbException("can not find pid of {}".format(package))

    def get_ip(self):
        cmd = "{} -s {} shell \"ifconfig|grep -oe 'addr:172\.[0-9]*\.[0-9]*\.[0-9]*'\"".format(conf.adb_path, self.device)
        result = subprocess.getoutput(cmd)
        if len(result) == 0:
            raise AdbException("The phone NOT connected to WIFI")
        else:
            return result.split(":")[1]

    def get_cpu(self, package):
        return self._get_cpu_rate(package)

    def get_fps(self, package):
        cmd = "{} -s {} shell dumpsys gfxinfo {}".format(conf.adb_path, self.device, package)
        results = subprocess.getoutput(cmd)
        frames = [x for x in results.split('\n')]
        jank_count = 0
        vsync_overtime = 0
        render_time = 0
        fra = []
        try:
            for frame in frames:
                if re.findall("\d+\.\d+.*\d+\.\d+.*\d+\.\d+", frame):  # math pattern like 1.11\t2.22\t3.33\t4.44
                    fra.append(frame)
            frame_count = len(fra)
            for frame in fra:
                time_block = re.split(r'\s+', frame.strip())
                render_time = sum([float(x) for x in time_block])
                '''
                当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
                那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
                如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

                最后的计算方法思路：
                执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
                需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

                所以FPS的算法可以变为：
                m / （m + 额外的垂直同步脉冲） * 60
                '''
                if render_time > 16.67:
                    jank_count += 1
                    if render_time % 16.67 == 0:
                        vsync_overtime += int(render_time / 16.67) - 1
                    else:
                        vsync_overtime += int(render_time / 16.67)
            # print("-----fps------")
            if frame_count == 0:
                _fps = 60
            else:
                _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
            return _fps
        except Exception:
            raise AdbException("{} 请打开开发者模式中的GPU显示".format(self.device))

    def get_mem(self, package):
        cmd = "{} -s {} shell dumpsys meminfo {}".format(conf.adb_path, self.device, package)
        meminfo = subprocess.getoutput(cmd).split()
        data = ""
        for i in range(len(meminfo)):
            if meminfo[i] == "TOTAL":
                data = meminfo[i + 1]
                break
        if data:
            mem = round(int(data) / 1024, 2)
            return mem
        else:
            raise AdbException("can not get meminfo of {} from {}".format(package, self.device))

    def _get_cpu_jiff(self, pid):
        '''
                utime   该任务在用户态运行的时间，单位为jiffies
            　　stime   该任务在核心态运行的时间，单位为jiffies
            　　cutime  累计的该任务的所有的waited-for进程曾经在用户态运行的时间，单位为jiffies
            　　cstime= 累计的该任务的所有的waited-for进程曾经在核心态运行的时间，单位为jiffies
                '''
        utime = stime = cutime = cstime = 0
        try:
            cmd = "{} -s {} shell cat /proc/{}/stat".format(conf.adb_path, self.device, pid)
            res = subprocess.getoutput(cmd).split()
            utime = res[13]
            stime = res[14]
            cutime = res[15]
            cstime = res[16]
            result = int(utime) + int(stime) + int(cutime) + int(cstime)
        except IndexError:
            raise
        return result

    def _get_cpu_rate(self, package):
        pid = self._get_pid(package)
        process_cpu_time1 = self._get_cpu_jiff(pid)
        total_cpu_time1 = self._total_cpu_time()
        time.sleep(1)
        process_cpu_time2 = self._get_cpu_jiff(pid)
        total_cpu_time2 = self._total_cpu_time()
        process_cpu_time3 = process_cpu_time2 - process_cpu_time1
        total_cpu_time3 = (total_cpu_time2 - total_cpu_time1)
        return round(100 * process_cpu_time3 / total_cpu_time3, 1)

    def _total_cpu_time(self):

        '''
        user    从系统启动开始累计到当前时刻，用户态的CPU时间（单位：jiffies） ，不包含 nice值为负进程。1jiffies=0.01秒
        nice    从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间（单位：jiffies）
        system  从系统启动开始累计到当前时刻，核心时间（单位：jiffies）
        idle    从系统启动开始累计到当前时刻，除硬盘IO等待时间以外其它等待时间（单位：jiffies）
        iowait  从系统启动开始累计到当前时刻，硬盘IO等待时间（单位：jiffies） ，
        irq     从系统启动开始累计到当前时刻，硬中断时间（单位：jiffies）
        softirq 从系统启动开始累计到当前时刻，软中断时间（单位：jiffies）
        '''
        user = nice = system = idle = iowait = irq = softirq = 0
        try:
            cmd = "{} -s {} shell cat /proc/stat".format(conf.adb_path, self.device)
            res = subprocess.getoutput(cmd).split()
            for info in res:
                if info == "cpu":
                    user = res[1]
                    nice = res[2]
                    system = res[3]
                    idle = res[4]
                    iowait = res[5]
                    irq = res[6]
                    softirq = res[7]
                    result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
                    return result
        except IndexError:
            raise AdbException("can not get totalCpuInfo from {}".format(get_name_from_device(self.device)))

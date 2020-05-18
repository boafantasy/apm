# coding: utf-8

import os
import time
from concurrent.futures import ThreadPoolExecutor
from apm.adbpackage import AdbPackage
from apm.conf_oprate import confLoad
from apm.data import OperatePick
import queue
conf = confLoad()


def get_device_cpu_info(device):
    adb = AdbPackage(device)
    cpu = adb.get_cpu(conf.package)
    return cpu


def get_device_mem_info(device):
    adb = AdbPackage(device)
    mem = adb.get_mem(conf.package)
    return mem


def get_device_fps_info(device):
    adb = AdbPackage(device)
    fps = adb.get_fps(conf.package)
    return fps


def write_data(data, file_name):
    op = OperatePick()
    if conf.info_path.endswith("\\"):
        file = conf.info_path + file_name
    else:
        file = conf.info_path + os.sep + file_name
    op.write(data, file)


def get_device_info(device, device_name, q):
    op = OperatePick()
    time_str = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    info_floder_name = conf.info_path + os.sep + time_str
    data_file_name = device_name + ".pickle"
    op.create_floder(info_floder_name)
    print("grabbing from {}...\n".format(device_name))
    while True:
        if q.empty():
            timestamp = time.time()
            if int(timestamp) % 5 == 0:
                # print(time.strftime("%H:%M:%S", time.localtime()))
                cpu = get_device_cpu_info(device)
                mem = get_device_mem_info(device)
                fps = get_device_fps_info(device)
                # print(time.strftime("%H:%M:%S", time.localtime()))
                info_dict = dict(
                    time=time.strftime("%H:%M:%S", time.localtime(timestamp)),
                    device=device_name,
                    cpu=cpu,
                    mem=mem,
                    fps=fps,
                )
                print(info_dict)
                op.write([info_dict], info_floder_name + os.sep + data_file_name, "aw")
            time.sleep(0.5)
        else:
            flag = q.get()
            if flag == -1:
                print("device {} stopped".format(device_name))
                break


def multi_main():
    if len(conf.devices) == 0:
        print("no device configuration in config.json")
        exit(1)
    process_num = len(conf.devices) + 1
    q = queue.Queue()
    try:
        p = ThreadPoolExecutor(max_workers=process_num)

        for device in conf.devices:
            device_ip_port = "{}:{}".format(device.get("device_ip"), device.get("device_port"))
            device_name = device.get("device_info")
            p.submit(get_device_info, device_ip_port, device_name, q)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("stop grabbing from devices...")
        for i in range(len(conf.devices)):
            q.put(-1)


if __name__ == "__main__":
    multi_main()

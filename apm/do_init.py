import subprocess
from apm.conf_oprate import confLoad
from apm.adbpackage import AdbPackage
conf = confLoad()


def device_init(device, device_info, port=5555):
    connect_flag = False
    device_ip = AdbPackage(device).get_ip()
    if device_ip.endswith("\n"):
        device_ip = device_ip.split("\n")[0]
    out = subprocess.getoutput("{} -s {} tcpip {}".format(conf.adb_path, device, port))
    if out == "restarting in TCP mode port: {}".format(port):
        tcpip_flag = True
    else:
        print(out)
        tcpip_flag = False
    if tcpip_flag:
        out = subprocess.getoutput("{} connect {}:{}".format(conf.adb_path, device_ip, port))
        if out == "connected to {}:{}".format(device_ip, port) or out == "already connected to {}:{}".format(device_ip, port):
            connect_flag = True
        else:
            print(out)
            connect_flag = False
    device_dict = dict(
        device_ip=device_ip,
        device_port=port,
        device_info=device_info
    )
    if tcpip_flag and connect_flag:
        conf.update_devices(device_dict)
        return True
    else:
        return False




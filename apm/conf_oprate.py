import json
import os
from apm.env_init import env_init
config_file = "./config.json"


class confLoad(object):

    def __init__(self):

        if not os.path.isfile(config_file):
            env_init()
        with open(config_file, "r") as f:
            config_content = f.read()
            self.config_json = json.loads(config_content)

    @property
    def devices(self):
        return self.config_json.get("devices")

    @property
    def adb_path(self):
        return self.config_json.get("adb_path")

    @property
    def report_path(self):
        return self.config_json.get("report_path")

    @property
    def package(self):
        return self.config_json.get("package")

    @property
    def info_path(self):
        return self.config_json.get("info_path")

    def update_devices(self, device):
        """
        :param device:
        {
         "device_ip": "172.21.25.27",
         "device_port": 5555,
         "device_info": "Oneplus 6p"
         }
        """
        devices_info = self.config_json.get("devices")
        if len(devices_info) == 0:
            devices_info.append(device)
        else:
            if device.get("device_ip") not in [device.get("device_ip") for device in devices_info]:
                devices_info.append(device)
            else:
                for k, v in enumerate(devices_info):
                    if device.get("device_ip") == devices_info[k].get("device_ip"):
                        devices_info[k]["device_info"] = device.get("device_info")
                        break
        self.config_json.update(dict(devices=devices_info))
        with open(config_file, "w") as f:
            f.write(json.dumps(self.config_json, ensure_ascii=False, indent=3))


if __name__ == "__main__":
    conf = confLoad()
    print(conf.devices)

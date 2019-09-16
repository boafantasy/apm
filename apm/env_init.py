# coding:utf-8

import os
import json


def env_init():
    try:
        os.mkdir("report")
        print("create folder report")
    except FileExistsError:
        print("report folder exists, ignore")

    try:
        os.mkdir("info")
        print("create folder info")
    except FileExistsError:
        print("info folder exists, ignore")

    init_config = {
        "report_path": "report",
        "adb_path": "D:\\your_adb_path\\adb.exe",
        "package": "com.baidu.homework",
        "info_path": "info",
        "devices": [
        ]
    }
    if os.path.isfile("config.json"):
        print("config.json exists ,ignore")
    else:
        with open("config.json", "w") as f:
            f.write(json.dumps(init_config, ensure_ascii=False, indent=3))
        print("create config file success")
    print("init complete")

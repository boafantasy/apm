# coding:utf-8

import os
import pickle
from apm.conf_oprate import confLoad
conf = confLoad()


class OperatePick(object):
    """
    保存和读取性能数据
    """

    def create_file(self, path):
        with open(path, "wb") as f:
            pass

    def create_floder(self, path):
        if os.path.isdir(path):
            print("{} is exists".format(path))
        else:
            os.mkdir(path)
            print("{} created".format(path))

    def read(self, path):
        # print("read pickle " + path)
        data=[]
        if not os.path.isfile(path):
            self.create_file(path)
        with open(path, 'rb') as f:
            try:
                data = pickle.load(f)
                # print(data)
            except EOFError:
                return []
        return data

    def write(self, data, path, mode="w"):
        _read = self.read(path)
        # print("write pickle")
        result = []
        if mode == "aw":
            if isinstance(data, dict):
                _read.append(data)
                result = _read
            if isinstance(data, list):
                result = _read + data
        elif mode == "w":
            if isinstance(data, dict):
                result.append(data)
            if isinstance(data, list):
                result += data
        with open(path, 'wb') as f:
            pickle.dump(result, f)

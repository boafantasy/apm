# coding: utf-8

import os
from apm.conf_oprate import confLoad
from apm.data import OperatePick
from pyecharts.charts import Line, Page
from pyecharts import options as opts
from pyecharts.globals import ThemeType

op = OperatePick()
conf = confLoad()


def generate_csv(folder_path):
    pickle_folder_path = conf.info_path + os.sep + folder_path
    total_data = {}
    device_name_list = []
    src_title = []
    if os.listdir(pickle_folder_path):
        pass
    else:
        print("该目录下没有任何性能数据")
        exit(1)
    for file in os.listdir(pickle_folder_path):
        device_name = file.split(".")[0]
        total_data[device_name] = op.read(pickle_folder_path + os.sep + file)
        device_name_list.append(device_name)
    longest_result = sorted([(len(total_data.get(k)), k) for k in total_data.keys()])[-1]  # get the longest result
    longest_count, longest_device = longest_result
    device_count = len(total_data)
    title = ["time", ["CPU"] * device_count, ["MEM"] * device_count, ["FPS"] * device_count]
    for i in title:
        if isinstance(i, str):
            src_title += [i]
        elif isinstance(i, list):
            src_title += i
    second_title = [""] + device_name_list * 3
    data = []
    for i in range(longest_count):
        time = total_data.get(longest_device)[i].get("time")
        cpu_list = []
        mem_list = []
        fps_list = []
        for device_name in device_name_list:
            try:
                cpu = total_data.get(device_name)[i].get("cpu")
                mem = total_data.get(device_name)[i].get("mem")
                fps = total_data.get(device_name)[i].get("fps")
                cpu_list.append(str(cpu))
                mem_list.append(str(mem))
                fps_list.append(str(fps))
            except IndexError:
                cpu_list.append("")
                mem_list.append("")
                fps_list.append("")
        data.append([time] + cpu_list + mem_list + fps_list)
    with open(conf.report_path + os.sep + folder_path + ".csv", "w", encoding="utf-8") as f:
        f.write(",".join(src_title) + "\n")
        f.write(",".join(second_title) + "\n")
        f.writelines([",".join(i) + "\n" for i in data])
    print("csv文件生成在report目录下")


def generate_html(folder_path):
    """
    info_dict = dict(
                    time=time.strftime("%H:%M:%S", time.localtime(timestamp)),
                    device=device_name,
                    cpu=cpu,
                    mem=mem,
                    fps=fps,
                )
    """
    pickle_folder_path = conf.info_path + os.sep + folder_path
    if os.listdir(pickle_folder_path):
        pass
    else:
        print("该目录下没有任何性能数据")
        exit(1)
    total_data = {}
    page = Page(page_title="移动端性能图表")
    cpu_line = Line(init_opts=opts.InitOpts(width="1200px", height="600px", theme=ThemeType.DARK))
    mem_line = Line(init_opts=opts.InitOpts(width="1200px", height="600px", theme=ThemeType.DARK))
    fps_line = Line(init_opts=opts.InitOpts(width="1200px", height="600px", theme=ThemeType.DARK))
    # 给所有折线图增加title和工具栏
    cpu_line.set_global_opts(title_opts=opts.TitleOpts(title="CPU", subtitle="所有设备CPU数据(%)"),
                             toolbox_opts=opts.ToolboxOpts())
    mem_line.set_global_opts(title_opts=opts.TitleOpts(title="内存", subtitle="所有设备内存数据(Mb)"),
                             toolbox_opts=opts.ToolboxOpts())
    fps_line.set_global_opts(title_opts=opts.TitleOpts(title="FPS", subtitle="所有设备FPS数据(帧)"),
                             toolbox_opts=opts.ToolboxOpts())
    file_list = os.listdir(pickle_folder_path)
    for file in file_list:
        device_name = file.split(".")[0]
        total_data[device_name] = op.read(pickle_folder_path + os.sep + file)
    longest_result = sorted([(len(total_data.get(k)), k) for k in total_data.keys()])[-1][1]  # get the longest result
    x_coordinate = [i.get("time") for i in total_data.get(longest_result)]
    cpu_line.add_xaxis(x_coordinate)

    mem_line.add_xaxis(x_coordinate)
    fps_line.add_xaxis(x_coordinate)
    for k in total_data.keys():  # 按设备加折线数据
        data = total_data.get(k)
        cpu_line.add_yaxis(data[0].get("device"), [i.get("cpu") for i in data], )
        mem_line.add_yaxis(data[0].get("device"), [i.get("mem") for i in data], )
        fps_line.add_yaxis(data[0].get("device"), [i.get("fps") for i in data], )

    for line in (cpu_line, mem_line, fps_line):  # 给所有折线图添加最大，最小，平均值
        (
            line.set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 markpoint_opts=opts.MarkPointOpts(
                                     data=[
                                         opts.MarkPointItem(type_="max", name="最大值"),
                                         opts.MarkPointItem(type_="min", name="最小值")
                                     ], symbol_size=40),
                                 markline_opts=opts.MarkLineOpts(
                                     data=[
                                         opts.MarkLineItem(type_="average", name="平均值", )
                                     ],
                                     symbol="none"
                                 ))
        )
    page.add(cpu_line, mem_line, fps_line)
    file_time = folder_path.split("_")[1:-1]
    file_time_str = "{}月{}日_{}点{}分_".format(*file_time)
    report_name = conf.report_path + os.sep + file_time_str + ".".join([i.split(".")[0] for i in file_list]) + ".html"
    page.render(report_name)
    print("\"{}\" 文件生成在report目录下".format(file_time_str + ".".join([i.split(".")[0] for i in file_list]) + ".html"))

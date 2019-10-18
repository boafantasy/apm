import argparse


def cli():
    epilog_message = """
    使用方法：
    1. 使用-e参数先初始化工作环境，生成info，report，config.json文件
    2. 填写config.json中的info_path(默认当前目录), report_path(默认当前目录), adb_path(adb命令的目录), 
       package(需要监控app的名字，例如com.baidu.homework)信息
    3. 使用"-t device_id -n device_name" 注册设备，device_id可以通过adb devices获取
    4. 使用-r 参数开始获取对应package的性能数据，想停止时，直接键盘输入Ctrl + C
    5. 使用"-c 文件名",在report目录生成同名csv文件，内容为测试性能结果数据(数据为每5秒一个)
    6. 使用"-p 文件名",在report目录生成同名html文件，内容为测试性能结果图表(数据为每5秒一个)
    """
    config = argparse.ArgumentParser(description="安卓设备性能日志收集工具",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,  # epilog_message保留换行
                                     epilog=epilog_message)
    config.add_argument(
        "-e",
        dest="env_init",
        default=False,
        action="store_true",
        help="初始化工作环境，在当前目录下创建config.json文件，data、report和data目录"
    )
    config.add_argument(
        "-t",
        dest="init_device",
        default=None,
        action="store",
        help="初始化设备，通过adb tcpip使用socket连接手机，初始化完成后即使手机没有USB连接电脑也能继续使用adb命令,并将设备信息写入config.json"
    )
    config.add_argument(
        "-n",
        dest="device_name",
        default=None,
        action="store",
        help="初始化设备，标记设备名称，和-t配合使用"
    )
    config.add_argument(
        "-r",
        dest="run",
        default=False,
        action="store_true",
        help="开始获取config.json配置文件中devices内的设备，并获取所有设备的CPU, MEM, FPS信息，最后记录到info文件中"
    )
    config.add_argument(
        "-c",
        dest="csv_file",
        default=None,
        action="store",
        help="输入info下对应时间文件夹的名字，在report目录输出结果csv文件"
    )
    config.add_argument(
        "-p",
        dest="report_file",
        default=None,
        action="store",
        help="输入pickle文件的名字，在report目录输出结果html文件"
    )
    args = config.parse_args()
    init_device = args.init_device
    device_name = args.device_name
    env = args.env_init
    run = args.run
    pickle_file_csv = args.csv_file
    pickle_file_report = args.report_file
    if init_device:
        from apm.do_init import device_init
        if device_name:
            flag = device_init(init_device, device_name)
            if flag:
                print("{}--{} 初始化设备成功".format(init_device, device_name))
        else:
            print("请使用-n输入设备名称，例如'mi8'、'mate20'")
        return
    if env:
        from apm.env_init import env_init
        env_init()
        return
    if run:
        from apm.pref_grab import multi_main
        multi_main()
        return
    if pickle_file_csv:
        from apm.outputGenerator import generate_csv
        generate_csv(pickle_file_csv)
        return
    if pickle_file_report:
        from apm.outputGenerator import generate_html
        generate_html(pickle_file_report)
        return
    config.print_help()


if __name__ == "__main__":
    cli()

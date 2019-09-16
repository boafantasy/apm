## 使用方法：
 1. 使用-e参数先初始化工作环境，生成info，report，config.json文件
 2. 填写config.json中的info_path(默认当前目录), report_path(默认当前目录), adb_path(adb命令的目录), 
       package(需要监控app的名字，例如com.baidu.homework)信息，数据为每5秒一个采集一次
 3. 使用"-t device_id -n device_name" 注册设备，device_id可以通过adb devices获取
 4. 使用-r 参数开始获取对应package的性能数据，想停止时，直接键盘输入Ctrl + C
 5. 使用"-c 文件名",在report目录生成同名csv文件，内容为测试性能结果数据
 6. 使用"-p 文件名",在report目录生成同名html文件，内容为测试性能结果图表
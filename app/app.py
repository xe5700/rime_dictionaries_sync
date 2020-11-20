from subprocess import run, Popen
import subprocess
from os import path
from crontab import CronTab
import os
import rime_update
from utils import *
from time import sleep
import datetime
import shutil

time_format = "%Y年-%m月-%d日 %M：%S"


def main():
    env = os.environ
    once = str2bool(env.get("RUN_ONCE", "False"))
    baidu = env.get("USE_BAIDU", "False")
    sogou = env.get("USE_SOGOU", "True")
    cron_dict_update = env.get("CRON_DICT_UPDATE", "0 3 */7 * *")
    dict_type = env.get("DICT_TYPE", "clover")
    sogou_dir_re = env["SOGOU_DIR_RE"]
    sogou_file_re = env["SOGOU_FILE_RE"]
    baidu_dir_re = env["BAIDU_DIR_RE"]
    baidu_file_re = env["BAIDU_FILE_RE"]
    rclone = str2bool(env["USE_RCLONE"])
    remote_config = env["REMOTE_CONFIG"]
    remote_path = env["REMOTE_SYNC_PATH"]

    def sync_dir_to_local():
        print("同步文件夹到本地")
        run(["rclone", "sync", f"{remote_config}:{remote_path}", "--create-empty-src-dirs", "/remote", "-v"])

    def sync_dir_to_remote():
        print("同步文件夹到远程")
        run(["rclone", "sync", "/remote", f"{remote_config}:{remote_path}", "--create-empty-src-dirs", "--checksum",
             "-v", "--exclude", "*.txt"])

    def dl_and_sync():
        print("开始下载并生成词库")
        if rclone:
            sync_dir_to_local()
        rime_update.main()
        if rclone:
            for user in os.listdir("/remote"):
                if user == "generic":
                    continue
                fn = path.join("/remote", user)
                if path.isdir(fn):
                    print("开始复制字典")
                    os.system(f"cp -rf /dicts/* {fn}")
            sync_dir_to_remote()

    print("你的设置为............")
    print(f"字典更新类型：{dict_type}")
    print(f"词库更新时间：{cron_dict_update}")
    print(f"搜狗词库：{sogou}")
    print(f"百度词库：{baidu}")
    print(f"搜狗词库类型正则：{sogou_dir_re}")
    print(f"搜狗词库名称正则：{sogou_file_re}")
    print(f"百度词库类型正则：{baidu_dir_re}")
    print(f"百度词库名称正则：{baidu_file_re}")
    print(f"RCLONE远程同步：{rclone}")
    print(f"远程文件夹：{remote_path}")
    if once:
        print("你添加了ONCE变量，将不使用计划任务只运行一次任务。")
    if rclone:
        print("RCLONE需要使用配置文件，检测是否存在配置文件，不存在配置文件本程序将终止工作。")
        if not os.path.exists("/config/rclone/rclone.conf"):
            print("你未配置RCLONE的配置文件，程序停止工作。")
            exit(-1)
    dl_and_sync()
    while not once:
        cron = CronTab(cron_dict_update, loop=True, random_seconds=True)
        nt = datetime.datetime.now().strftime(time_format)
        delayt = cron.next(default_utc=False)
        nextrun = datetime.datetime.now() + datetime.timedelta(seconds=delayt)
        nextruntime = nextrun.strftime(time_format)
        print(f"当前时间 {nt}")
        print(f"下一次执行时间 {nextruntime}")
        sleep(delayt)
        dl_and_sync()


if __name__ == "__main__":
    print('''	
______ ________  ___ _____  ______ _____ _____ _____   _   _____________  ___ _____ _____ 
| ___ \_   _|  \/  ||  ___| |  _  \_   _/  __ \_   _| | | | | ___ \  _  \/ _ \_   _|  ___|
| |_/ / | | | .  . || |__   | | | | | | | /  \/ | |   | | | | |_/ / | | / /_\ \| | | |__  
|    /  | | | |\/| ||  __|  | | | | | | | |     | |   | | | |  __/| | | |  _  || | |  __| 
| |\ \ _| |_| |  | || |___  | |/ / _| |_| \__/\ | |   | |_| | |   | |/ /| | | || | | |___ 
\_| \_|\___/\_|  |_/\____/  |___/  \___/ \____/ \_/    \___/\_|   |___/ \_| |_/\_/ \____/ 
                                              
	''')

    print("欢迎使用 中州韵 拼音词库自动更新系统")
    print("本系统可以下载搜狗和百度的拼音的词库来为你的中州韵提供最新的词库")
    print("并且通过同步软件将更新同步到所有的设备。")
    print("支援朙月拼音并且支持四叶草拼音")
    print("本脚本设计为DOCKER或者GITHUB ACTION 环境运行")
    main()

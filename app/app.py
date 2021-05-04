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
    once = str2bool(os.getenv("RUN_ONCE", "False"))
    baidu = os.getenv("USE_BAIDU", "False")
    sogou = os.getenv("USE_SOGOU", "True")
    cron_dict_update = os.getenv("CRON_DICT_UPDATE", "0 3 */7 * *")
    dict_type = os.getenv("DICT_TYPE", "clover")
    sogou_dir_re = os.getenv("SOGOU_DIR_RE")
    sogou_file_re = os.getenv("SOGOU_FILE_RE")
    baidu_dir_re = os.getenv("BAIDU_DIR_RE")
    baidu_file_re = os.getenv("BAIDU_FILE_RE")
    use_rclone = str2bool(os.getenv("USE_RCLONE"))
    use_git = str2bool(os.getenv("USE_GIT"))
    remote_config = os.getenv("REMOTE_CONFIG")
    remote_path = os.getenv("REMOTE_SYNC_PATH")

    def sync_dir_to_local():
        print("同步文件夹到本地")
        run(["rclone", "sync", f"{remote_config}:{remote_path}", "--create-empty-src-dirs", "/dicts", "-v",
             "--include-from", "rime_dict_update_sync_filelist.txt"])

    def sync_dir_to_remote():
        print("同步文件夹到远程")
        run(["rclone", "sync", "/dicts", f"{remote_config}:{remote_path}", "--create-empty-src-dirs", "--checksum",
             "-v", "--include-from", "rime_dict_update_sync_filelist.txt"])

    def pull_dir_to_local():
        print("从git拖取文件夹到本地")
        run(["git", "pull"], cwd="/dicts")

    def push_dir_to_local():
        print("从git提交文件夹到远程git服务器")
        ut = datetime.datetime.now().isoformat("YYYY-MM-DD HH:MM:SS")
        run(["git", "add", "."], cwd="/dicts")
        run(["git", "commit", "-m", "使用rime_dictionaries_update更新\n"
                                    f"更新日期{ut}"], cwd="/dicts")
        run(["git", "push"], cwd="/dicts")

    def dl_and_sync():
        print("开始下载并生成词库")
        if use_rclone:
            sync_dir_to_local()
        if use_git:
            pull_dir_to_local()
        rime_update.main()
        if use_rclone:
            # os.system(f"cp -rf /dicts/* /remote/")
            sync_dir_to_remote()
        if use_git:
            push_dir_to_local()

    print("你的设置为............")
    print(f"字典更新类型：{dict_type}")
    print(f"词库更新时间：{cron_dict_update}")
    print(f"搜狗词库：{sogou}")
    print(f"百度词库：{baidu}")
    print(f"搜狗词库类型正则：{sogou_dir_re}")
    print(f"搜狗词库名称正则：{sogou_file_re}")
    print(f"百度词库类型正则：{baidu_dir_re}")
    print(f"百度词库名称正则：{baidu_file_re}")
    print(f"RCLONE远程同步：{use_rclone}")
    print(f"GIT远程同步：{use_git}")
    print(f"远程文件夹：{remote_path}")
    if once:
        print("你添加了ONCE变量，将不使用计划任务只运行一次任务。")
    if use_rclone:
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

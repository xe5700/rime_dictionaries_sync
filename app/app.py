
from crontab import CronTab
import os
def main():
	env = os.environ
	baidu = env.get("USE_BAIDU","False")
	sogou = env.get("USE_SOGOU","True")
	cron_dict_update = env.get("CRON_DICT_UPDATE", "0 3 */7 * *")
	print("你的设置为............")
	print(f"词库更新时间：{cron_dict_update}")
	print(f"百度词库：{baidu}")
	print(f"百度词库：{sogou}")
	print(f"搜狗词库类型正则：{sogou_re}")
if __name__ == "__main__":
	print('''	
______ _                 ______ _      _         _____                  
| ___ (_)                |  _  (_)    | |       /  ___|                 
| |_/ /_ _ __ ___   ___  | | | |_  ___| |_ ___  \ `--. _   _ _ __   ___ 
|    /| | '_ ` _ \ / _ \ | | | | |/ __| __/ __|  `--. \ | | | '_ \ / __|
| |\ \| | | | | | |  __/ | |/ /| | (__| |_\__ \ /\__/ / |_| | | | | (__ 
\_| \_|_|_| |_| |_|\___| |___/ |_|\___|\__|___/ \____/ \__, |_| |_|\___|
                                                        __/ |           
                                                       |___/            
	''')

	print("欢迎使用 中州韵 拼音词库自动同步系统")
	print("本系统将自动根据你的设置从服务器生成最新版本的词库")
	print("支援朙月拼音并且支持四叶草拼音")
	print("")
	main()
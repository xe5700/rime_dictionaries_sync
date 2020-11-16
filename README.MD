# 中州韵词库自动更新 (rime auto update)

## 简介
本工具能够使用商业词库自动更新中州韵输入法的网络词库。

## 功能
- 可以通过正则匹配下载指定的搜狗百度的细胞词库 (使用ThesaurusSpider实现)
- 支持网盘网路同步 (通过RCLONE实现)
- 支持朙月拼音和四叶草拼音

## 使用项目
	ThesaurusSpider
	Rclone
	Opencc
	crontab(python)
## 使用方法
	docker pull xe5700/rime-dict-update(只支持LINUX X64平台)
	然后根据DOCKERFILE里的变量，设置完以后运行容器即可。
	可以使用计划任务功能运行也可以使用脚本自带的计划任务功能。
	通过挂载本地硬盘可以直接同步，也可以不挂载使用网盘进行全设备同步

## 未来开发
	目前只支持使用DOCKER容器，未来可能允许使用GITHUB ACTION功能来同步词库。
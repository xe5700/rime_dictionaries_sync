import os
from os import environ, path
from subprocess import run,Popen
import subprocess
from typing import List
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
import re
import io
import datetime

DICT_TYPE: str
def getfiles(p: str) -> List[str]:
	files = []
	for f in os.listdir(p):
		nf = path.join(p,f)
		if path.isdir(nf):
			files.extend(getfiles(nf))
		else:
			files.append(nf)
	return files

def findDirs(p: str) -> List[str]:
	files = []
	for f in os.listdir(p):
		nf = path.join(p,f)
		if path.isdir(nf):
			files.append(nf)
			files.extend(findDirs(nf))
	return files

def getnametype(p: str):
	p = p[:p.rfind(".")]
	t = "/tmp/dicts/"
	if p.startswith(t):
		return p[len(t):]
	
yaml_header_group = '''# Rime dictionary
# encoding: utf-8
#
# 自动生成词库{name}
#
# 部署位置：
# ~/.config/ibus/rime  (Linux)
# ~/Library/Rime  (Mac OS)
# %APPDATA%\Rime  (Windows)
#
# 於重新部署後生效
#

---
name: {name}
version: "{ver}"
   import_tables:
{imports}
...
'''

yaml_header = '''# Rime dictionary
# encoding: utf-8
#
# 自动生成词库{name}
#
# 部署位置：
# ~/.config/ibus/rime  (Linux)
# ~/Library/Rime  (Mac OS)
# %APPDATA%\Rime  (Windows)
#
# 於重新部署後生效
#

---
name: {name}
version: "{ver}"
...

# 自定义词语

'''
invalidfns = re.compile('【|】|（|）|！|※|《|》')
def convert_file(file_name: str):
		cv2 = convert.format(i=file_name, type="{type}")
		if file_name.endswith(".scel"):
			cv2 = cv2.format(type="scel")
		elif file_name.endswith(".qpyd"):
			cv2 = cv2.format(type="qpyd")
		elif file_name.endswith(".qcel"):
			cv2 = cv2.format(type="qcel")
		elif file_name.endswith(".bdict"):
			cv2 = cv2.format(type="bdict")
		elif file_name.endswith(".sgpy"):
			cv2 = cv2.format(type="sgpy")
		elif file_name.endswith(".sgpybin"):
			cv2 = cv2.format(type="sgpybin")
		elif file_name.endswith(".bdpy"):
			cv2 = cv2.format(type="bdpy")
		run(cv2, shell=True, stdout=subprocess.DEVNULL)
		ndire_name = ""
		# 朙月拼音
		if DICT_TYPE == "luna":
			dire_type = "luna."+getnametype(file_name).replace('/','.')
			dire_type = invalidfns.sub('_',dire_type)
			ndire_name = dire_type+".dict.yaml"
			# 朙月拼音需要转换为繁体才可以使用
			run(["opencc","-i","/tmp/rime.txt","-o","/tmp/rime2.txt","-c","s2t.json"])
			with open("/tmp/rime2.txt", "r") as f:
				dict_info = f.read()
				with open("/tmp/dicts_out/"+ndire_name, "w+") as f2:
					data = yaml_header.format(name=dire_type, ver=datetime.datetime.fromtimestamp(os.path.getmtime(file_name)).isoformat())
					data += dict_info
					f2.write(data)
					pass
		# 四叶草拼音
		elif DICT_TYPE == "clover":
			dire_type = getnametype(file_name).replace('/','.')
			dire_type = invalidfns.sub('_',dire_type)
			ndire_name = dire_type+".dict.yaml"
			with open("/tmp/rime.txt", "r") as f:
				dict_info = f.read()
				with open("/tmp/dicts_out/"+ndire_name, "w+") as f2:
					data = yaml_header.format(name=dire_type, ver=datetime.datetime.fromtimestamp(os.path.getmtime(file_name)).isoformat())
					data += dict_info
					f2.write(data)
					pass
		print("成功转换 "+ ndire_name)

def main():
	DICT_TYPE = os.environ.get("DICT_TYPE","clover")
	os.environ['PATH'] = f"{os.environ['PATH']}:/root/.dotnet"
	print("正在下载搜狗词库")
	d_sogou = Popen(["python2", "ThesaurusSpider/SougouThesaurusSpider/multiThreadDownload.py", "--dir_re", os.environ["DIR_RE"], "--file_re", os.environ["FILE_RE"]])
	#print("正在下载百度词库")
	#d_baidu = Popen(["python2", "ThesaurusSpider/BaiduTheaurusSpider/multiThreadDownload.py"])
	#print("正在下载QQ词库")
	#d_qq = Popen(["python2", "ThesaurusSpider/QQTheaurusSpider/multiThreadDownload.py"])
	d_sogou.wait()
	#d_baidu.wait()
	#d_qq.wait()
	print("查找词库")
	alldires = getfiles("/tmp/dicts/")
	#alldires_type = findDirs("/tmp/dicts/")
	convert = "dotnet ./imewlconverter/ImeWlConverterCmd.dll -i:{type} '{i}' -o:rime /tmp/rime.txt"
	print("开始转换词库 为 中州韵格式")
	os.mkdir('/tmp/dicts_out/')
	pool = ThreadPoolExecutor(max_workers=4)
	for dire in alldires:
		pool.submit(convert_file, dire)
	pool.shutdown()
	alldicts = os.listdir("/tmp/dicts_out")
	with open("/tmp/dicts_out/{}.autoupdate.dict.yaml".format(DICT_TYPE), "w+") as of:
		groupsx = io.StringIO()
		for f in alldicts:
			f=f[:f.find(".dict.yaml")]
			groupsx.write("   - {}\n".format(f))
		out = yaml_header_group.format(name="{}.autoupdate".format(DICT_TYPE),imports=groupsx.getvalue(), ver=datetime.datetime.now().isoformat())
		of.write(out)
		print(out)
		print("成功输出词库集 "+of.name)
	os.system('mv /tmp/dicts_out/* /dicts/')

if __name__ == "__main__":
	main()
import datetime
import io
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from os import path
from subprocess import run, Popen
from typing import List

from utils import *

dict_type: str


def getfiles(p: str) -> List[str]:
    files = []
    for f in os.listdir(p):
        nf = path.join(p, f)
        if path.isdir(nf):
            files.extend(getfiles(nf))
        else:
            files.append(nf)
    return files


def findDirs(p: str) -> List[str]:
    files = []
    for f in os.listdir(p):
        nf = path.join(p, f)
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
#d
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
convert: str
invalidfns = re.compile('【|】|（|）|！|※|《|》| ')


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

    def process_default():
        os.rename("/tmp/rime.txt", "/tmp/rime2.txt")

    # noinspection PyGlobalUndefined
    def process_1(typen: str, func):
        global ndire_name
        fn_pipe = Popen(f"echo {file_name} | opencc -c s2t.json", shell=True, stdout=subprocess.PIPE)
        fn_pipe.wait()
        fn_name = fn_pipe.stdout.read().decode()
        dire_type = f"{typen}." + getnametype(fn_name).replace('/', '.')
        dire_type = invalidfns.sub('_', dire_type)
        ndire_name = dire_type + ".dict.yaml"
        func()
        with open("/tmp/rime2.txt", "r") as f:
            dict_info = f.read()
            with open("/tmp/dicts_out/" + ndire_name, "w+") as f2:
                data = yaml_header.format(name=dire_type,
                                          ver=datetime.datetime.fromtimestamp(os.path.getmtime(file_name)).isoformat())
                data += dict_info
                f2.write(data)
                pass
        os.remove("/tmp/rime.txt")
        os.remove("/tmp/rime2.txt")

    # noinspection PyTypeChecker
    def luna():
        process_1("luna", lambda: run(["opencc", "-i", "/tmp/rime.txt", "-o", "/tmp/rime2.txt", "-c", "s2t.json"]))
        # 朙月拼音需要转换为繁体才可以使用

    def clover():
        process_1("clover", process_default)

    # 朙月拼音
    if dict_type == "luna":
        luna()
    # 四叶草拼音
    elif dict_type == "clover":
        clover()
    elif dict_type == "all":
        luna()
        clover()
    print("成功转换 " + ndire_name)


def main():
    global convert, dict_type
    dict_type = os.environ.get("DICT_TYPE", "clover")
    d_baidu: Popen = None
    d_sogou: Popen = None
    if str2bool(os.environ["USE_SOGOU"]):
        print("正在下载搜狗词库")
        d_sogou = Popen(["python2", "ThesaurusSpider/SougouThesaurusSpider/multiThreadDownload.py"])
    if str2bool(os.environ["USE_BAIDU"]):
        print("正在下载百度词库")
        d_baidu = Popen(["python2", "ThesaurusSpider/BaiduTheaurusSpider/multiThreadDownload.py"])
    # print("正在下载QQ词库")
    # d_qq = Popen(["python2", "ThesaurusSpider/QQTheaurusSpider/multiThreadDownload.py"])
    d_sogou: subprocess.Popen
    d_baidu: subprocess.Popen
    if d_sogou != None:
        d_sogou.wait()

    if d_baidu != None:
        d_baidu.wait()

    # d_qq.wait()
    print("查找词库")
    alldires = getfiles("/tmp/dicts/")
    # alldires_type = findDirs("/tmp/dicts/")
    convert = "dotnet ./imewlconverter/ImeWlConverterCmd.dll -i:{type} '{i}' -o:rime /tmp/rime.txt"
    print("开始转换词库 为 中州韵格式")
    os.mkdir('/tmp/dicts_out/')
    pool = ThreadPoolExecutor(max_workers=4)
    for dire in alldires:
        pool.submit(convert_file, dire)
    pool.shutdown()

    def mk_all(alldicts: List[str], type: str):
        with open(f"/tmp/dicts_out/{type}.autoupdate.dict.yaml", "w+") as of:
            groupsx = io.StringIO()
            for f in alldicts:
                fl = f.rfind(".dict.yaml")
                f = f[:fl]
                groupsx.write(f"   - {f}\n")
            out = yaml_header_group.format(name=f"{type}.autoupdate", imports=groupsx.getvalue(),
                                           ver=datetime.datetime.now().isoformat())
            of.write(out)
            print(out)
            print("成功输出词库集 " + of.name)
        os.system('mv /tmp/dicts_out/* /dicts/')

    alldicts = os.listdir("/tmp/dicts_out")
    dicts_luna = []
    dicts_clover = []
    for i in alldicts:
        if i.startswith("clover."):
            dicts_clover.append(i)
        elif i.startswith("luna."):
            dicts_luna.append(i)
    if len(dicts_luna) > 0:
        mk_all(dicts_luna, "luna")
    if len(dicts_clover) > 0:
        mk_all(dicts_clover, "clover")
    print("执行清理")
    for f in os.listdir("/tmp/"):
        fn = f"/tmp/{f}"
        print(f"清理 {fn}")
        if path.isdir(fn):
            shutil.rmtree(fn)
        else:
            os.remove(fn)


if __name__ == "__main__":
    main()

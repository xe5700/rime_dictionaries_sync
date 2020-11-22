import datetime
import io
import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from os import path
from subprocess import run, Popen
from typing import List, Callable, Set
from utils import *
import tempfile
import pypinyin
import json
import logging
from threading import Semaphore

dict_types: str

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
sort: by_weight
...
'''

yaml_header = '''# Rime dictionary
# encoding: utf-8
#
# 自动生成词库集 {name}
#
# 部署位置：
# ~/.config/ibus/rime  (Linux)
# ~/Library/Rime  (Mac OS)
# %APPDATA%\Rime  (Windows)
#
# 於重新部署後生效
#
{include}
---
name: {name}
version: "{ver}"
sort: by_weight
...
'''
convert: str
invalidfns = re.compile('[【】（）！※《》 -]')
all_dicts: Set[str] = set()
tmp_dir: tempfile.TemporaryDirectory
dicts_sync = Semaphore(1)

def convert_file(file_name: str):
    global all_dicts
    tmpf = tempfile.mktemp(dir= tmp_dir.name, prefix="rime_tmp_dict", suffix=".txt")
    cv2 = convert.format(i=file_name, type="{type}", tmp=tmpf)
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
    print(f"执行 {cv2}")
    ret = run(cv2, shell=True, stdout=subprocess.DEVNULL)
    if ret.returncode != 0:
        print(f"文件{file_name}转换失败！这个词库将不会被添加到词库集。")
        return

    with dicts_sync:
        with open(tmpf, "r") as f:
            for line in f.readlines():
                all_dicts.add(line)
    os.remove(tmpf)
    print("成功转换 " + file_name)


def main():
    global convert, dict_types, tmp_dir, all_dicts
    dict_types = json.loads(os.environ["DICT_TYPES"])
    d_baidu: Popen = None
    d_sogou: Popen = None

    tmp_dir = tempfile.TemporaryDirectory(prefix="rime-dict-update")
    tmp_dicts_dir = tempfile.TemporaryDirectory(dir=tmp_dir.name)
    os.environ["TMP_DL_PATH"] = tmp_dicts_dir.name
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

    if d_sogou is not None:
        d_sogou.wait()

    if d_baidu is not None:
        d_baidu.wait()

    # d_qq.wait()
    print("查找词库")
    alldires = getfiles(tmp_dicts_dir.name)
    # alldires_type = findDirs("/tmp/dicts/")
    convert = 'dotnet ./imewlconverter/ImeWlConverterCmd.dll -i:{type} "{i}" -o:rime "{tmp}"'
    print("开始转换词库 为 中州韵格式")
    pool = ThreadPoolExecutor(max_workers=4)
    includes = io.StringIO()
    tmpdictdirlen = len(tmp_dicts_dir.name)+1
    for dire in alldires:
        _dire = dire[tmpdictdirlen:]
        includes.write(f"#{_dire}\n")
        pool.submit(convert_file, dire)
    pool.shutdown()

    def mkdict(dtype: str, _dicts: str):
        with open(f"/dicts/{dtype}.autoupdate.dict.yaml", "w+") as of:
            out = yaml_header.format(name=f"{dtype}.autoupdate",
                                     ver=datetime.datetime.now().isoformat(),
                                     include=includes.getvalue())
            of.write(out)
            of.write(_dicts)
            print("成功输出词库集 " + of.name)

    tc_dicts: str
    sc_dicts: str
    with io.StringIO() as dicts:
        for d in all_dicts:
            dicts.write(d)
            dicts.write("\n")
        sc_dicts = dicts.getvalue()
        tc_dicts = s2t(sc_dicts)

    for t in dict_types:
        # 朙月拼音
        if t == "luna":
            mkdict("luna", tc_dicts)
        # 四叶草拼音
        elif t == "clover":
            mkdict("clover", sc_dicts)
    print(f"执行清理 {tmp_dir.name}")
    tmp_dir.cleanup()
    all_dicts.clear()


if __name__ == "__main__":
    main()

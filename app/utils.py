import subprocess
from subprocess import Popen
import signal

def str2bool(s: str):
	s = s.lower()
	if s == "true" or s == "1":
		return True
	else:
		return False


def s2t(s: str) -> str:
	popen = Popen(["opencc", "-c", "s2t.json"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	result, err = popen.communicate(s.encode())
	if popen.returncode:
		raise RuntimeError('Call opencc failed!')
	return result.decode()

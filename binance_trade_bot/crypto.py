# pip install cryptography
from cryptography.fernet import Fernet

def co():
	return res[1:]

def gitr():
	return res_git[1:]
keys = []

f = open("ca.cfg", "rb")
for line in f:
	keys.append(line)
f.close()

cipher_key = keys[2]
git = keys[1][:-2]
info = keys[0][:-2]

cipher = Fernet(cipher_key)
res = str(cipher.decrypt(info))
res_git = str(cipher.decrypt(git))
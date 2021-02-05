import sys
import os

print("argv was",sys.argv)
print("sys.executable was", sys.executable)
       
cwd = os.path.dirname(os.path.abspath(__file__))
if sys.platform.startswith('win'):
   separador="\\"
else:
   separador="/"
cfile=cwd + separador + "xnoppo_web.py"

while True:
    command = sys.executable + ' "' + cfile + '"'
    print(command)
    #print("restart now")
    os.system(command)

import subprocess
result = subprocess.Popen('date', stdout=subprocess.PIPE,shell=True)
out = result.stdout
print(out)
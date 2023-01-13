import os

cur_dir = os.getcwd()
print(cur_dir)
if os.path.isfile('WAVECAR'):
	filesize = os.path.getsize('WAVECAR')
	if filesize == 0:
		print("WAVECAR is empty")
	else:
		os.system('qsub /home01/x2431a03/run_lobster.sh')
else:
	print("There is no WAVECAR")




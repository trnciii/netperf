import subprocess
import re, functools
import argparse

def readline(proc):
	line = proc.stdout.readline().rstrip('\n')
	return [i[1:-1] for i in line.split(',')] if len(line) else False

def update_indices(table, t):
	i, l = t
	name = re.search(r'\((.+?)\)', l).group(1)
	ma = re.search(r'(Received|Sent)/sec', l)
	if ma:
		table[name] = table.get(name, {}) | {ma.group(1): i}
	return table

def format_bps(i, w=11, p=4):
	bps = float(i)*8

	if bps > 1024 ** 2:
		return f'{bps/1024**2: {w}.{p}f} Mbps'
	elif bps > 1024:
		return f'{bps/1024: {w}.{p}f} Kbps'
	else:
		return f'{bps: {w}.{p}f}  bps'


def kernel(count = None):
	cmd = 'typeperf "Network Interface(*)\\Bytes Received/sec" "Network Interface(*)\\Bytes Sent/sec"'
	if count:
		cmd += f' -sc {count}'

	proc = subprocess.Popen(cmd, text=True, shell=True, stdout=subprocess.PIPE)
	proc.stdout.readline()

	indices = functools.reduce(update_indices, enumerate(readline(proc)), {})

	rows = len(indices)
	end = '\n' if count else f'\033[{rows}A'

	wkeys = max(len(i) for i in indices.keys())
	wbps, pbps = 11,4
	fm = functools.partial(format_bps, w=wbps, p=pbps)

	print('interface'.ljust(wkeys), 'received'.rjust(wbps + 5), 'sent'.rjust(wbps + 5))
	print('-'*(wkeys + (wbps+5)*2 + 2))

	while True:
		line = readline(proc)
		if not line:
			break

		for k, v in indices.items():
			print(k.ljust(wkeys), fm(line[v["Received"]]), fm(line[v["Sent"]]))
		print(end, end='')


def main():
	try:
		parser = argparse.ArgumentParser()
		parser.add_argument('count', nargs='?', type=int, const=None)
		args = parser.parse_args()
		kernel(args.count)

	except KeyboardInterrupt:
		print()

	except IndexError:
		pass

	except Exception as e:
		import traceback
		traceback.print_exception(e)

if __name__ == '__main__':
	main()
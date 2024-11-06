from os import system
from tkinter import filedialog as fd
from json import load
from pathlib import Path
import subprocess
from sys import argv

def get_length(filepath):
	result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
							"format=duration", "-of",
							"default=noprint_wrappers=1:nokey=1", filepath],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT)
	return float(result.stdout)

try:
	with open("HSR_folderpath.txt", 'r') as file:
		initdir = file.read()
except FileNotFoundError:
	initdir = '../'
	
file = fd.askopenfilename(initialdir=initdir,
						filetypes=(("Cutscene files", "{*.usm}"), ("All files", "{*.*}")),
						title="Select cutscene file")
if file[-4:] != ".usm":
	raise ValueError("Selected file type is not supported")

with open(file, 'rb') as tempfile:
	data = tempfile.read()
	if data[:4] != b'CRID':
		raise ValueError("Selected file type is not a .usm file or is corrupted")
	
	start = data.find(b'\00', data.find(b'avbps') + 6) + 1
	end = data.find(b'\00', start)
	filenames = []
	c = 0
	for i in range(6):
		if i == 0:
			filename = data[start : end].split(b'\\')[-1].decode()[:-4]
			continue
		filenames.append(data[start : end].split(b'\\')[-1].decode())
		start = end + 1
		end = data.find(b'\00', start)
		videopath = str(Path(f'./output/{filename.lower()}.usm/videos/{filenames[0].lower()}')
						.absolute()
						).replace('\\', '/')
		
with open('./HSR_folderpath.txt', 'w+') as folderpath:
	folderpath.write('/'.join(file.split('\\')[:-1]))
	
audiopaths = {}
langdict = {"CN" : "00", "EN" : "01", "JP" : "02", "KR" : "03"}
audio_ext = '.' + filenames[1].split('.')[-1]
for j in range(4):
	audiopaths[list(langdict.keys())[j]] = str(Path(f'./output/{filename.lower()}.usm/audios/{filenames[j+1][:-9]}').absolute()).replace('\\', '/')


with open("./keys.json", 'r') as keys:
	versionlist = list(dict(dict(load(keys))["StarRail"]["KeyMap"]).values())
	for version in versionlist:
		try:
			key = dict(version)[filename]
			
		except KeyError:
			pass
		
try:
	print("Key found! Key: ", key)
	
except NameError:
	print("Key not found! Exiting...")
	exit()
	
system(f'wannacri extractusm "{file}" --key {key}')

while True:
	lang = input("Choose perferred language(cn, en, jp, kr): ").upper()
	
	try:
		langdict[lang]
		break
		
	except KeyError:
		pass

audiopath = (audiopaths[lang] + lang + langdict[lang] + audio_ext).lower()

subprocess.call(f'ffmpeg -i "{videopath}" -i "{audiopath}" -c:v copy -c:a aac ./{filename}.mp4')

system(f'ffplay -i {str(Path('./').absolute()).replace('\\', '/')}/{filename}.mp4 -t {get_length(filename+".mp4")} -autoexit')

system(f'rmdir ".\\output\\" /S /Q')

try:
	if argv[1] != "-kv":
		system(f'del /Q .\\{filename}.mp4')
	
except IndexError:
	system(f'del /Q .\\{filename}.mp4')
	

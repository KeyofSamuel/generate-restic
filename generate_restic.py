#!/usr/bin/env python

#### -- Generate Restic Backup Script -- #### 

# -- Imports -- #

import subprocess
import os
import pwd
import yaml
import time
import socket

# -- Variables Section -- #

TIMESTAMP = time.strftime( '%Y-%m-%d_%H:%M:%S' )
HOST = socket.gethostname()
USERNAME = pwd.getpwuid(os.getuid()).pw_name

# -- Load config from .yml file -- #

config_path = "/home/" + USERNAME + "/.config/restic-backup/config.yml"

try:	
	config = yaml.safe_load(open(config_path))
except:	
	print("Configuration file at: \n\n\t" + config_path + "\n\ndoes not exist!  \n\nExiting gracefully...\n")
	exit()

# -- Set global variables from config file -- #

LOGFILE = config['global']['logpath']
 
os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
exists = os.path.isfile(LOGFILE)
if not exists:
	f = open(LOGFILE, "w")
	f.close
	
# -- Function to end the script -- #
def end():
	exit()

# -- Function to create and display the menu -- #
def menu():

	# Title Display #
	print()
	print('{:^80}'.format('#'*46))
	print('{:^80}'.format('#' + ' '*4 + 'The Restic Backup Script Generator' + ' '*4 + '#'))	#make sure center words are even number of characters
	print('{:^80}'.format('#'*46))
	print()
	print()

	# Menu options and display #
	menu_options = ["1 - Generate a new Restic backup job",
					"2 - Generate a consecutive executable script",
					"0 - Quit"]

	for i in menu_options:
		print(" "*20 + i)
	print()

# -- Function to generate the Restic backup job -- #
def generate():

	## Loop over all backup sections in config ##
	for BACKUP in config:
		if BACKUP != "global": # ignore the global config section

			## Create the initial basic file ##
			BackupName = BACKUP
			FileName = HOST + "-" + BackupName + "-backup"
			FilePath = "/home/" + USERNAME + "/.config/restic-backup"

			## Variable assignments ##
			JobFile = os.path.join(FilePath,FileName)
			Repository = config[BACKUP]['repository']
			BackupSource = config[BACKUP]['bkup_source']
			GroupBy = config[BACKUP]['group_by']
			
			Exclusions = ''
			if config[BACKUP]['bkup_exclusions']:
				set_exclusions = config[BACKUP]['bkup_exclusions']
				for AddExclusion in set_exclusions:
					AddExclusion = " --exclude=" + AddExclusion
					Exclusions = Exclusions + AddExclusion

			Tags = ''
			if config[BACKUP]['bkup_tags']:
				set_tags = config[BACKUP]['bkup_tags']
				for AddTag in set_tags:
					AddTag = " --tag " + AddTag
					Tags = Tags + AddTag

			PruningOptions = ''
			set_prunings = config[BACKUP]['pruning_options']
			for TimeFrame in set_prunings:
				for i in TimeFrame:
					P = i
					T = str(TimeFrame[i])
					if T != "None":
						P = " --keep-" + P + " " + T
						PruningOptions = PruningOptions + P

			if config[BACKUP]['pruning_options_tags']:
				set_pruning_options_tags = config[BACKUP]['pruning_options_tags']
				for KeepTags in set_pruning_options_tags:
					KeepTags = " --keep-tag " + KeepTags
					PruningOptions = PruningOptions + KeepTags

			PruningTags = ''
			if config[BACKUP]['pruning_tags']:
				set_pruningtags = config[BACKUP]['pruning_tags']
				for AddPruningTag in set_pruningtags:
					AddPruningTag = " --tag " + AddPruningTag
					PruningTags = PruningTags + AddPruningTag
			
			set_HostName = config[BACKUP]['hostname']
			if set_HostName == "DEFAULT":
				HostName = socket.gethostname()
				HostName = "--host " + HostName
			elif set_HostName:
				HostName = set_HostName
				HostName = "--host " + HostName
			elif not set_HostName:
				HostName = ''
			else:
				HostName = ''

			## Write imports to backup script ##
			with open(JobFile, 'w') as f:
				f.write('#!/usr/bin/python\n\n')
				f.write(f'## -- Host: {HOST} Offsite Backup Script -- ##\n\n')
				f.write('# -- Imports -- #\n\n')
				f.write('import time\n')
				f.write('import subprocess\n')
				f.write('import logging\n')
				f.write('import logging.handlers\n')
				f.write('import socket\n\n')
				f.closed
			
			## Write options to backup script ##
			with open(JobFile, 'a') as f:
				f.write("# -- Source and Repository Section -- #\n\n")
				f.write("REPOSITORY = '" + Repository +"'\n")
				f.write("BackupSource = '" + BackupSource + "'\n")
				f.write("BackupExclusions = '" + Exclusions + "'\n")
				f.write("BackupTags = '" + Tags + "'\n")
				f.write("PruningOptions = '" + PruningOptions + "'\n")
				f.write("PruningTags = '" + PruningTags + "'\n")
				f.write("HostName = '" + HostName + "'\n")
				f.write("GroupBy = '--group-by " + GroupBy + "'\n\n")
				
				f.write("# -- Variables Section -- #\n\n")
				f.write("TIMESTAMP = time.strftime( '%Y-%m-%d_%H:%M:%S' )\n")
				f.write("HOST = socket.gethostname()\n")
				f.write("HOST = HOST.upper()\n\n")
				f.write(f"LogFile = '{LOGFILE}'\n")
				
				f.write("# -- Log File Section -- #\n\n")
				f.write(f"logger = logging.getLogger('{BackupName}')\n")
				f.write("logger.setLevel(logging.INFO)\n")
				f.write("log_handler = logging.handlers.TimedRotatingFileHandler(LogFile, when='D', interval=1, backupCount=90)\n")
				f.write("log_format = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s: %(message)s')\n")
				f.write("log_handler.setFormatter(log_format)\n")
				f.write("logger.addHandler(log_handler)\n")
				f.write("LogOut = ' | tee -a ' + LogFile\n\n")

				f.write("logger.info(\"*** HOST: \" + HOST + \" ***\")\n")

				f.closed

			## Write backup section to script ##
			with open(JobFile, 'a') as f:
				f.write("# -- Backup Section -- #\n\n")
				
				f.write("try:\n")
				f.write("\tlogger.info('Host ' + HOST + ' backups started')\n")
				f.write("\tRESTIC = (f'restic -r {REPOSITORY} backup {BackupSource} {BackupExclusions} {BackupTags}')\n")
				f.write("\tsubprocess.call(RESTIC + LogOut, shell=True)\n")
				f.write("\tlogger.info('Host ' + HOST + ' backups completed at ' + TIMESTAMP)\n")
				f.write("except:\n")
				f.write("\tlogger.info('!!! Host ' + HOST + ' backups failed at ' + TIMESTAMP + ' !!!')\n\n")
				
			## Write pruning section to script ##
				Pruning = config[BACKUP]['pruning']
				if Pruning:
					f.write("# -- Pruning Section -- #\n\n")
					
					f.write("try:\n")
					f.write("\tlogger.info('Host ' + HOST + ' pruning started')\n")
					f.write("\tRESTIC = (f'restic -r {REPOSITORY} forget {PruningOptions} --prune {PruningTags} {GroupBy} {HostName}')\n")
					f.write("\tsubprocess.call(RESTIC + LogOut, shell=True)\n")
					f.write("\tlogger.info('Host ' + HOST + ' pruning completed at ' + TIMESTAMP)\n")
					f.write("except:\n")
					f.write("\tlogger.info('!!! Host ' + HOST + ' pruning failed at ' + TIMESTAMP + ' !!!')\n")

				f.closed
			
			subprocess.call("chmod +x " + JobFile,shell=True)

def consecutive():
	
	'''
	Scan the config folder for backups
	display backups
	Allow for the selection of specific backups
	write out an executable script
	'''
	
	subprocess.call("clear",shell=True)
	print('{:^80}'.format('#' + ' '*4 + 'Generate a consecutive executable script ' + ' '*4 + '#'))
	print()
	
	FilePath = "/home/" + USERNAME + "/.config/restic-backup/"
	(_, _, filenames) = next(os.walk(FilePath))
	
	# Null lists values #
	file_dict = {}		# null dictionary for files and names
	sort_dict = {}		# null dictionary for files sort directories
	sort_list = []		# null list for files sort directories
	backupList = []		# null list for files sort directories
	increment = 0

	for i in filenames:
		if i[-6:] == "backup":
			FullPath = os.path.join(FilePath,i)
			file_dict.update({i:FullPath})	# Create dictionary of file and directory
	
	for i in file_dict:
		sort_list.append(i)

	sort_list.sort()
	
	for i in sort_list:
		increment += 1
		x = file_dict[i]
		sort_dict.update({increment:i})
	
	print()
	print(" "*20 + "Below is the list of backup files.  Choose a file by number to add to the consecutive execution script.")
	print(" "*20 + "Add as many files as desired.  Press \"q\" when you are finished adding files.")
	print()
	
	pick = ""
	while pick != 0:
		for m in sort_dict:
			print(" "*23, m, "->", sort_dict[m]) 	# Prints the sorted file list

		print()
		pick = input(" "*20 + "Pick a file by number!\n" + " "*20 + "-> ")
		if pick == "q":
			pick = 0
		pick = int(pick)
		
		for m in sort_dict:
			if m == pick:
				x = sort_dict[m]
				backupList.append(file_dict[x])
	
	print()
	BackupScript = input(" "*20 + "Enter the name of the consecutive execution script\n" + " "*20 + "-> ")
	BackupScript = os.path.join(FilePath,BackupScript)
	
	## Write backup files to consecutive script ##
	with open(BackupScript, 'w') as f:
		f.write('#!/bin/bash\n\n')
		f.write('# -- Backup Scripts to Execute -- #\n')
		
		for i in backupList:
			f.write(i + "\n")
			
		f.closed

	subprocess.call("chmod +x " + BackupScript,shell=True)
	
		  
## -- Start the Application Here -- ##

# -- Clear the screen -- #
subprocess.call("clear",shell=True)
print()
print('{:^^80}'.format(''))

# -- Menu loop, display and choice selection -- #
choice = None
while choice != "0":

	menu()

	choice = input(" "*20 + "Please choose a menu option\n" + " "*20 + "-> ")
	
	menu_options = {'0':end, '1':generate, '2':consecutive}
	
	try:
		menu_options[choice]()
	except KeyError:
			print("Oops!  That was not a valid option.  Try again...")

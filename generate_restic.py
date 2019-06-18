#!/usr/bin/env python

#### -- Generate Restic Backup Script -- #### 

# -- Imports -- #

import subprocess
import os
import yaml
import time
import socket

# -- Load config from .yml file -- #

config = yaml.safe_load(open("config.yml"))

# -- Variables Section -- #

TIMESTAMP = time.strftime( '%Y-%m-%d_%H:%M:%S' )
HOST = socket.gethostname()

## -- Menu Function Definition Area -- ##

# -- Function to exit the application -- #
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
					"0 - Quit"]

	for i in menu_options:
		print(" "*20 + i)
	print()

# -- Function to set subsequent working directory -- #
def generate():

	## Loop over all backup sections in config ##
	for BACKUP in config:
		if BACKUP != "global": # ignore the global config section

			## Create the initial basic file ##
			#BackupName = config[BACKUP]['backup_name']
			BackupName = BACKUP
			FileName = HOST + "-" + BackupName + "-backup"
			
			FilePath = "Default"
			if FilePath == "Default":
				FilePath = os.getcwd()

			## Variable assignments ##
			JobFile = os.path.join(FilePath,FileName)
			LogPath = config['global']['logpath']
			Repository = config[BACKUP]['repository']
			BackupSource = config[BACKUP]['bkup_source']
			GroupBy = config[BACKUP]['group_by']
			
			Exclusions = ''
			set_exclusions = config[BACKUP]['bkup_exclusions']
			for AddExclusion in set_exclusions:
				AddExclusion = " --exclude=" + AddExclusion
				Exclusions = Exclusions + AddExclusion

			Tags = ''
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
				HostName = "--hostname " + HostName
			elif set_HostName:
				HostName = set_HostName
				HostName = "--hostname " + HostName
			elif not set_HostName:
				HostName = ''
			else:
				HostName = ''

			## Write imports to backup script ##
			with open(JobFile, 'w') as f:
				f.write('#!/usr/bin/python\n\n')
				f.write(f'## -- Host: {HOST} Offsite Backup Script -- ##\n\n')
				f.write('# -- Imports -- #\n\n')
				f.write('import log\n')
				f.write('import utility\n')
				f.write('import time\n')
				f.write('import subprocess\n')
				f.write('import logging\n')
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
				f.write("GroupBy = '" + GroupBy + "'\n\n")
				
				f.write("# -- Variables Section -- #\n\n")
				f.write("TIMESTAMP = time.strftime( '%Y-%m-%d_%H:%M:%S' )\n")
				f.write("HOST = socket.gethostname()\n\n")
				
				f.write("# -- Log File Section -- #\n\n")
				f.write("LOGPATH = '/home/samuel/coffeecup/.log'\n")
				f.write("logfile = log.Logging(LOGPATH)\n")
				f.write("CURRENT_LOG = logfile.find()\n")
				f.write("logging.basicConfig(filename=CURRENT_LOG, format='%(asctime)s :: %(levelname)s: %(message)s', level=logging.INFO)\n")
				f.write("LogOut = ' | tee -a ' + CURRENT_LOG\n\n")

				f.write("logging.info(\"\\n*** HOST: \" + HOST + \" ***\")\n\n")

				f.closed

			## Write backup section to script ##
			with open(JobFile, 'a') as f:
				f.write("# -- Backup Section -- #\n\n")
				
				f.write("try:\n")
				f.write("\tRESTIC = (f'restic -r {REPOSITORY} backup {BackupSource} {BackupExclusions} {BackupTags}')\n")
				f.write("\tlogging.info('Host ' + HOST + ' backups completed')\n")
				f.write("\tsubprocess.call(RESTIC + LogOut, shell=True)\n")
				f.write("except:\n")
				f.write("\tlogging.info('!!! Host ' + HOST + ' backups failed !!!')\n\n")
				
			## Write pruning section to script ##
				Pruning = config[BACKUP]['pruning']
				if Pruning:
					f.write("# -- Pruning Section -- #\n\n")
					
					f.write("try:\n")
					f.write("\tRESTIC = (f'restic -r {REPOSITORY} forget {PruningOptions} --prune {PruningTags} {GroupBy} {HostName}')\n")
					f.write("\tsubprocess.call(RESTIC + LogOut, shell=True)\n")
					f.write("\tlogging.info('Host ' + HOST + ' pruning completed')\n")
					f.write("except:\n")
					f.write("\tlogging.info('!!! Host ' + HOST + ' pruning failed !!!')\n")

				f.closed
			
			subprocess.call("chmod +x " + JobFile,shell=True)
		  
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
	
	menu_options = {'0':end, '1':generate}
	
	try:
		menu_options[choice]()
	except KeyError:
			print("Oops!  That was not a valid option.  Try again...")

# README for the Restic script generator

__Version 0.9.4__

The script seems to be functional and has been tested for creating valid backup scripts, but has not been fully vetted.  Verify all backup scripts and use at your own risk.

## About

  This is a script generator for restic backups.  It uses a YAML configuration file to set general options and the output is a restic script(s) that can be scheduled with CRON or run manually.

## Installation

### Install the application
  
  The application does not care where it is installed to.  It can be run by the 'generate_restic.py' script from any location, providing the configuration file is accessible (see below).  The script can also be placed in a location such as '/usr/local/src' and then the 'generate_restic' shell script (without an extension) placed in '/usr/local/bin' so that it can be called from anywhere as part of the $PATH.  The shell script specifically calls '/usr/local/src/generate_restic/generate_restic.py'.  If you place the source files in another location, modify the shell script appropriately.

#### Arch PKGBUILD

  While this application has not been added to the Arch Linux AUR, a PKGBUILD file for Arch Linux does exist and can be obtained by sending an email to the project creator.
  
### Install the configuration file

  The application is configured to look for a YAML configuration file in '~/.config/restic-backup/' called 'config.yml'.  In the Git repository is a 'config.yml.sample' file that provides a template for how to set up backups and configure the options.
  
#### Setting up the configuration file

  Many of the options are self-explanatory.  Below are some notes on options that may be slightly confusing.

  * Multiple backups can be set up by copying entire contents of 'Sample_Backup:' and creating another instance.  Backups will use the top part of the YAML tree as the backup name (eg. Sample_Backup:)
  * 'bkup_exclusions:', 'bakup_tags:', 'pruning_options_tags:' and 'pruning_tags:' are lists (sub-items start with a dash (-) and do not end with a colon (:)).  They can have as many items in the list as desired.  If no items are desired for a specific option, then either comment out the list, or remove the list items.  Do not remove the list's name (eg. 'bkup_tags:').  The script can handle lists with no items.
  * 'pruning_options:' set the time frames that will be kept/pruned.  Remove the number completely after each list item where you do not want to use that specific pruning option.  See the Restic manual for more specific information about how pruning works.
  * 'pruning_options_tags:' are part of Restic's "keep" options.  Tags set here will be kept.  See the Restic manual for more specific information on how pruning works.
  * 'pruning_tags:' are part of Restic's "remove" options.  Tags set here are used to include/exclude specific tags during the pruning process.  A list of individual tags are considered as an OR list (eg. tag1 OR tag2).  Tags set together with a comma (eg. tag1,tag2) are kept together as an AND list (tag1 AND tag2).  The lists can be mixed together (eg. tag1 OR (tag2 AND tag3)).
  * Keeping the hostname as DEFAULT will set pruning to occur only for snapshots taken from the host where the script was generated.  A different host can be specified, or leave the option blank to specify all host's snapshots.
  * 'group_by:' will group the snapshots together for a more controlled pruning.  Any of the three options (paths,tags,hosts) can be used and separated by a comma if more than one is used.  See the Restic manual for more specific inforamtion on how pruning and tags work.

## Things To Know

### Logging

  The backup scripts do log some of what occurs to a rotated log file.  The location of the log file is set in the 'config.yml' under the _global_ options.  While the logging does technically work, it is in need of plenty of work.  It is definitely on the future roadmap.

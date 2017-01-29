#!/usr/bin/env python

import os 
import json
import subprocess
current_dir = os.path.dirname(os.path.realpath(__file__))

def list_services():
	required_fields = ["name", "description", "project_dir", "git_remote", "subdomain", "daemon_run"]
	services_dir = os.path.join(current_dir, "services")
	for filename in os.listdir(services_dir):
		config_path = os.path.join(services_dir, filename)
		with open(config_path) as f:
			try:
				config = json.loads(f.read())
				for required_field in required_fields:
					if required_field not in config:
						raise Exception("Failed to load config for {}, missing required field {}".format(filename, required_field))
			except:
				raise Exception("Failed to load config for {}".format(filename))
			yield filename, config

for filename, config in list_services():
	print filename
	project_dir = os.path.expandvars(config['project_dir'])
	daemon_run = os.path.expandvars(config['daemon_run'])
	project_description = os.path.expandvars(config['description'])

	# GIT
	if not os.path.exists(project_dir):
		git_clone_cmd = ["git", "clone", config['git_remote'], project_dir]
		subprocess.call(git_clone_cmd)
	
	# SERVICE
	daemon_name = config['name'].replace(" ","_").lower()
	daemon_path = "/etc/init.d/{name}".format(name=daemon_name)
	if os.path.exists(daemon_path):
		os.remove(daemon_path)
	if not os.path.exists(daemon_path):
		template = ""
		with open("template_configs/daemon", "r") as f:
			template = f.read()
		with open(daemon_path, "w") as f:
			content = template.format(
				daemon_name=daemon_name,
				daemon_run=daemon_run,
				project_name=config['name'],
				project_dir=project_dir,
				project_description=project_description,
			)
			f.write(content)
	
	start_daemon_cmd = ["chmod", "755", daemon_path]
	subprocess.call(start_daemon_cmd)
	start_daemon_cmd = ["systemctl", "daemon-reload"]
	subprocess.call(start_daemon_cmd)
	start_daemon_cmd = ["service", daemon_name, "start"]
	subprocess.call(start_daemon_cmd)


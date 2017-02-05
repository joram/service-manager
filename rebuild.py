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

def write_config(template_filename, config_path, config, override=False):
	if override and os.path.exists(config_path):
		os.remove(config_path)
	with open("template_configs/{}".format(template_filename), "r") as f:
		template = f.read()
	with open(config_path, "w") as f:
		content = template.format(**config)


def update_git(config):
	if os.path.exists(config['project_dir']):
                os.chdir(project)dir)
		subprocess.call(["git", "pull", "origin", "master"])
        else:
		subprocess.call(["git", "clone", config['git_remote'], config['project_dir']])


def update_daemon(config):
	daemon_name = config['name'].replace(" ","_").lower()
	daemon_path = "/etc/init.d/{name}".format(name=daemon_name)
	daemon_port = config["port"]

	daemon_config = {
		"daemon_name": daemon_name,
		"daemon_run": daemon_run,
		"project_name": config['name'],
		"project_dir": config['project_dir'],
		"project_description": config['description'],
	}
	write_config("daemon", daemon_path, daemon_config, True)

	subprocess.call(["chmod", "755", daemon_path])
	subprocess.call(["systemctl", "daemon-reload"])
	subprocess.call(["service", daemon_name, "start"])


def update_nginx(config):
	daemon_name = config['name'].replace(" ","_").lower()
	nginx_path = "/etc/nginx/sites-available/{name}".format(name=daemon_name)

	if "custom_config" in config.get("nginx", {}):
		with open(nginx_path, "w") as f:
			f.write(nginx_path, config['custom_nginx_config')

	else:
        	nginx_config = {
			"port": config['port'],
			"project_name": config['name'],
			"subdomain": config['subdomain'],
			"auth": config.get('nginx', {}).get('auth', False)
		}
		write_config("nginx", nginx_path, nginx_config, True)

	subprocess.call(["service", "nginx", "restart"])


def rebuild():
	for filename, config in list_services():
		print filename
		config['project_dir'] = os.path.expandvars(config['project_dir'])
		config['daemon_run'] = os.path.expandvars(config['daemon_run'])
		config['description'] = os.path.expandvars(config['description'])
		update_git(config)
	        update_daemon(config)
		update_nginx(config)

if __name__ == "__main__":
	rebuild()


venv2:
	virtualenv2 venv ; . venv/bin/activate && pip install -r requirements.txt

venv:
	virtualenv venv ; . venv/bin/activate && pip install -r requirements.txt

up:
	vagrant up

clean:
	vagrant destroy -f ; rm -rf venv

list:
	venv/bin/fab -f tasks/fabfile.py -l

it:
	venv/bin/fab -f tasks/fabfile.py it

step01:
	venv/bin/fab -f tasks/fabfile.py step_01_create_hosts

step02:
	venv/bin/fab -f tasks/fabfile.py step_02_deploy_tinc_cluster

step03:
	venv/bin/fab -f tasks/fabfile.py step_03_deploy_consul_cluster

step04:
	venv/bin/fab -f tasks/fabfile.py step_04_deploy_git2consul_tinc_client

step05:
	venv/bin/fab -f tasks/fabfile.py step_05_deploy_git2consul

step06:
	venv/bin/fab -f tasks/fabfile.py step_06_deploy_fsconsul

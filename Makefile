venv2:
	virtualenv2 venv ; . venv/bin/activate && pip install -r requirements.txt

venv:
	virtualenv venv ; . venv/bin/activate && pip install -r requirements.txt

up:
	vagrant up core01
	vagrant up core02
	vagrant up core03
	vagrant up git2consul

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

acceptance_tests:
	fab -f tasks/fabfile.py acceptance_tests

laptop_acceptance_tests:
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.1
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.2
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.3

up_laptop:
	vagrant up laptop

vagrant_test_cycle: clean venv up it acceptance_tests up_laptop laptop_acceptance_tests

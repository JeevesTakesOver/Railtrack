clean: ## cleanup VMs and virtualenv
	echo "running make clean..."
	vagrant destroy -f ; rm -rf venv

venv2: ## for archlinux: Creates a python2 virtualenv and installs python modules
	echo "running make venv2 ..."
	virtualenv2 venv ; . venv/bin/activate && pip install -r requirements.txt

venv: ## Creates a python virtualenv and installs python modules
	echo "running make venv ..."
	virtualenv venv ; . venv/bin/activate && pip install -r requirements.txt

up: ## vagrant up for the core vagrant boxes
	echo "running make up ..."
	vagrant up core01
	vagrant up core02
	vagrant up core03
	vagrant up git2consul

list: ## list available fabric tasks
	echo "running make list ..."
	venv/bin/fab -f tasks/fabfile.py -l

it: ## provisions the core nodes
	echo "running make it ..."
	venv/bin/fab -f tasks/fabfile.py it

step01: ## create AWS VMs
	echo "running make step01 ..."
	venv/bin/fab -f tasks/fabfile.py step_01_create_hosts

step02: ## deploys the Tinc Cluster
	echo "running make step02 ..."
	venv/bin/fab -f tasks/fabfile.py step_02_deploy_tinc_cluster

step03: ## deploys the Consul Cluster
	echo "running make step03 ..."
	venv/bin/fab -f tasks/fabfile.py step_03_deploy_consul_cluster

step04: ## Deploys the Tinc Client on the git2consul node
	echo "running make step04 ..."
	venv/bin/fab -f tasks/fabfile.py step_04_deploy_git2consul_tinc_client

step05: ## Deploys the git2Consul service
	echo "running make step05 ..."
	venv/bin/fab -f tasks/fabfile.py step_05_deploy_git2consul

step06: ## Deploys the fsconsul service
	echo "running make step06 ..."
	venv/bin/fab -f tasks/fabfile.py step_06_deploy_fsconsul

acceptance_tests: ## runs acceptance tests against the core nodes
	echo "running make acceptance_tests ..."
	venv/bin/fab -f tasks/fabfile.py acceptance_tests

up_laptop: ## vagrant up the 'laptop' VM
	echo "running make up_laptop ..."
	vagrant up laptop

vagrant_acceptance_tests: ## runs acceptance tests on the 'laptop' box
	echo "running make vagrant_acceptance_tests ..."
	sleep 60
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.1
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.2
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.3
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.10
	vagrant ssh core01 -- sudo systemctl status tinc
	vagrant ssh core01 -- sudo systemctl status consul-server
	vagrant ssh core01 -- sudo systemctl status fsconsul
	vagrant ssh core02 -- sudo systemctl status tinc
	vagrant ssh core02 -- sudo systemctl status consul-server
	vagrant ssh core02 -- sudo systemctl status fsconsul
	vagrant ssh core03 -- sudo systemctl status tinc
	vagrant ssh core03 -- sudo systemctl status consul-server
	vagrant ssh core03 -- sudo systemctl status fsconsul
	vagrant ssh git2consul -- sudo systemctl status tinc
	vagrant ssh git2consul -- sudo systemctl status consul-client
	vagrant ssh git2consul -- sudo systemctl status git2consul

vagrant_reload: ## reloads all vagrant VMs
	echo "running make vagrant_reload ..."
	vagrant reload core01
	sleep 60
	vagrant reload core02
	sleep 60
	vagrant reload core03
	sleep 60
	vagrant reload git2consul
	sleep 60

vagrant_test_cycle: ## runs a full acceptance test cycle using Vagrant
	echo "running make vagrant_test_cycle ..."
	make clean
	make venv
	make up
	echo "waiting for first-boot apt-get update to finish ..."
	sleep 300
	make it
	make acceptance_tests
	make up_laptop
	make vagrant_reload
	make vagrant_acceptance_tests


.PHONY: help

help:
		@grep -E '^[A-Za-z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

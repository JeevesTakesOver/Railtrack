clean: ## cleanup VMs and virtualenv
	vagrant destroy -f ; rm -rf venv

venv2: ## for archlinux: Creates a python2 virtualenv and installs python modules
	virtualenv2 venv ; . venv/bin/activate && pip install -r requirements.txt

venv: ## Creates a python virtualenv and installs python modules
	virtualenv venv ; . venv/bin/activate && pip install -r requirements.txt

up: ## vagrant up for the core vagrant boxes
	vagrant up core01
	vagrant up core02
	vagrant up core03
	vagrant up git2consul

list: ## list available fabric tasks
	venv/bin/fab -f tasks/fabfile.py -l

it: ## provisions the core nodes
	venv/bin/fab -f tasks/fabfile.py it

step01: ## create AWS VMs
	venv/bin/fab -f tasks/fabfile.py step_01_create_hosts

step02: ## deploys the Tinc Cluster
	venv/bin/fab -f tasks/fabfile.py step_02_deploy_tinc_cluster

step03: ## deploys the Consul Cluster
	venv/bin/fab -f tasks/fabfile.py step_03_deploy_consul_cluster

step04: ## Deploys the Tinc Client on the git2consul node
	venv/bin/fab -f tasks/fabfile.py step_04_deploy_git2consul_tinc_client

step05: ## Deploys the git2Consul service
	venv/bin/fab -f tasks/fabfile.py step_05_deploy_git2consul

step06: ## Deploys the fsconsul service
	venv/bin/fab -f tasks/fabfile.py step_06_deploy_fsconsul

acceptance_tests: ## runs acceptance tests against the core nodes
	fab -f tasks/fabfile.py acceptance_tests

up_laptop: ## vagrant up the 'laptop' VM
	vagrant up laptop

laptop_acceptance_tests: ## runs acceptance tests on the 'laptop' box
	sleep 60
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.1
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.2
	vagrant ssh laptop -- ping -c 1 -t 1 169.254.0.3

vagrant_test_cycle: ## runs a full acceptance test cycle using Vagrant
	@make clean venv up it acceptance_tests up_laptop laptop_acceptance_tests

.PHONY: help

help:
		@grep -E '^[A-Za-z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

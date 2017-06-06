clean: ## cleanup VMs and virtualenv
	echo "running make clean..."
	vagrant destroy -f 
	# don't clean the virtualenv on nixos, we use nix-shell
	grep -i nixos /etc/os-release >/dev/null 2>&1 || rm -rf venv

.ONESHELL:
venv: ## Creates a python virtualenv and installs python modules
	echo "running make venv ..."
	PID=$$$$
	python -m virtualenv --python python2.7 /tmp/$$PID/venv 
	. /tmp/$$PID/venv/bin/activate 
	pip install -r requirements.txt
	ln -s /tmp/$$PID/venv venv

up: ## vagrant up for the core vagrant boxes
	echo "running make up ..."
	vagrant up core01 --no-provision
	vagrant ssh core01 -- sudo systemctl disable apt-daily.service
	vagrant ssh core01 -- sudo systemctl disable apt-daily.timer
	vagrant halt core01 
	vagrant up core01 --no-provision
	vagrant provision core01
	vagrant up core02 --no-provision
	vagrant ssh core02 -- sudo systemctl disable apt-daily.service
	vagrant ssh core02 -- sudo systemctl disable apt-daily.timer
	vagrant halt core02 
	vagrant up core02 --no-provision
	vagrant provision core02 
	vagrant up core03 --no-provision
	vagrant ssh core03 -- sudo systemctl disable apt-daily.service
	vagrant ssh core03 -- sudo systemctl disable apt-daily.timer
	vagrant halt core03 
	vagrant up core03 --no-provision
	vagrant provision core03 
	vagrant up git2consul --no-provision
	vagrant ssh git2consul -- sudo systemctl disable apt-daily.service
	vagrant ssh git2consul -- sudo systemctl disable apt-daily.timer
	vagrant halt git2consul
	vagrant up git2consul --no-provision
	vagrant provision git2consul
	echo "waiting for first-boot apt-get update to finish ..."

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

step07: ## Deploys the DHCPd service
	echo "running make step07 ..."
	venv/bin/fab -f tasks/fabfile.py step_07_deploy_dhcpd

step08: ## Deploys the DNS service
	echo "running make step08 ..."
	venv/bin/fab -f tasks/fabfile.py step_08_deploy_dnsserver

acceptance_tests: ## runs acceptance tests against the core nodes
	echo "running make acceptance_tests ..."
	venv/bin/fab -f tasks/fabfile.py acceptance_tests

up_laptop: ## vagrant up the 'laptop' VM
	echo "running make up_laptop ..."
	vagrant up laptop --no-provision
	vagrant ssh laptop -- sudo systemctl disable apt-daily.service
	vagrant ssh laptop -- sudo systemctl disable apt-daily.timer
	vagrant halt laptop
	vagrant up laptop --no-provision
	vagrant provision laptop
	# vagrant provision will remove resolvconf and dnsmasq
	# which require a reboot of the VM
	vagrant halt laptop
	vagrant up laptop --no-provision

vagrant_acceptance_tests: ## runs acceptance tests on the 'laptop' box
	echo "running make vagrant_acceptance_tests ..."
	sleep 60
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.1
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.2
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.3
	vagrant ssh laptop -- ping -c 1 -w 20 169.254.0.10
	vagrant ssh laptop -- /vagrant/laptop/tests/test-dns
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
	vagrant ssh core01 -- sudo systemctl status isc-dhcp-server
	vagrant ssh core01 -- sudo systemctl status bind9
	vagrant ssh core02 -- sudo systemctl status bind9

vagrant_reload: ## reloads all vagrant VMs
	echo "running make vagrant_reload ..."
	vagrant halt core01
	vagrant up core01 --no-provision
	sleep 60
	vagrant halt core02
	vagrant up core02 --no-provision
	sleep 60
	vagrant halt core03
	vagrant up core03 --no-provision
	sleep 60
	vagrant halt git2consul
	vagrant up git2consul --no-provision
	sleep 60

.ONESHELL:
vagrant_test_cycle: ## runs a full acceptance test cycle using Vagrant
	set -e
	echo "running make vagrant_test_cycle ..."
	make clean
	# don't run make venv on nixos, we use nix-shell for that
	grep -i nixos /etc/os-release >/dev/null 2>&1 || make venv
	make up
	make it
	make up_laptop
	make vagrant_reload
	sleep 300
	make acceptance_tests
	make vagrant_acceptance_tests


.PHONY: help

help:
		@grep -E '^[A-Za-z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

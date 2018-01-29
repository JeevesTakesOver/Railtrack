""" fabfile.py """
# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

# Copyright (C) 2016 Jorge Costa

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from time import sleep
from fabric.context_managers import settings
from fabric.api import (task, env, execute, local, sudo)
from fabric.operations import put
from retrying import retry
from profilehooks import timecall
from pathos.multiprocessing import ProcessingPool as Pool
from bookshelf.api_v2.logging_helpers import log_green
from jinja2 import Template

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.clusters  # pylint: disable=F0401, wrong-import-position
import lib.git2consul  # pylint: disable=F0401, wrong-import-position
import lib.mycookbooks  # pylint: disable=F0401, wrong-import-position
from tests.acceptance import (  # pylint: disable=F0401, wrong-import-position
    test_that_consul_binaries_were_installed_on,
    test_that_consul_client_config_exists_on,
    test_that_consul_client_init_exists_on,
    test_that_consul_client_is_running_on,
    test_that_consul_directories_exists_on,
    test_that_consul_peers_are_reachable_on,
    test_that_consul_server_config_exists_on,
    test_that_consul_server_init_exists_on,
    test_that_consul_server_is_running_on,
    test_that_consul_user_exists_on,
    test_that_consul_web_ui_files_exists_on,
    test_that_cron_apt_is_installed_on,
    test_that_patches_were_installed_on,
    test_that_tinc_binaries_were_installed_on,
    test_that_tinc_conf_files_were_deployed_on,
    test_that_tinc_interface_files_were_deployed_on,
    test_that_tinc_is_running_on,
    test_that_fail2ban_is_running_on,
    test_that_tinc_key_pairs_were_deployed_on,
    test_that_tinc_nets_boot_files_were_deployed_on,
    test_that_tinc_peers_are_pingable_on,
    test_that_tinc_peers_host_files_were_deployed_on,
    test_that_fsconsul_binaries_were_installed_on,
    test_that_fsconsul_init_exists_on,
    test_that_fsconsul_service_is_running_on,
    test_that_git2consul_init_exists_on,
    test_that_git2consul_service_is_running_on,
    test_that_dhcpd_server_is_running_on,
    test_that_dhcpd_binaries_were_installed_on,
    test_that_dhcpd_server_config_exists_on,
    test_that_dhcpd_server_init_exists_on,
    test_that_dnsserver_server_is_running_on,
    test_that_dnsserver_binaries_were_installed_on,
    test_that_dnsserver_server_config_exists_on,
    test_that_dnsserver_server_init_exists_on,
)  # pylint: disable=F0401, wrong-import-position


@task
@timecall(immediate=True)
def run_it(parallel_reboot=False):
    """ provisions OBOR """

    # first deploy the tinc cluster, as all steps depend on it
    if parallel_reboot:
        local('fab -f tasks/fabfile.py '
              'step_02_deploy_tinc_cluster:parallel_reboot=True')
    else:
        local('fab -f tasks/fabfile.py step_02_deploy_tinc_cluster')

    def tinc_flow():
        local('fab -f tasks/fabfile.py step_03_deploy_consul_cluster')
        local('fab -f tasks/fabfile.py step_06_deploy_fsconsul')
        local('fab -f tasks/fabfile.py step_07_deploy_dhcpd')
        local('fab -f tasks/fabfile.py step_08_deploy_dnsserver')

    def git2consul_flow():
        local('fab -f tasks/fabfile.py step_04_deploy_git2consul_tinc_client')
        local('fab -f tasks/fabfile.py step_05_deploy_git2consul')

    pool = Pool(processes=3)
    results = []
    results.append(pool.apipe(tinc_flow))
    results.append(pool.apipe(git2consul_flow))

    for stream in results:
        stream.get()

    local('fab -f tasks/fabfile.py step_09_reboot_hosts')


@task
@timecall(immediate=True)
def step_01_create_hosts():
    """ provisions new EC2 instances """
    t = Template(open('templates/main.tf.j2').read())

    with open('main.tf' ,'w') as f:
        f.write(
            t.render(
                key_pair = CFG['ec2_common']['key_pair'],
                key_filename = CFG['ec2_common']['key_filename'],
                aws_dns_domain = CFG['ec2_common']['aws_dns_domain'],
                region = CFG['ec2_common']['region'],
                instance_type = CFG['ec2_common']['instance_type']
            )
        )

    local("./terraform init")
    local("echo yes | ./terraform apply")


@task  # noqa: C901
@timecall(immediate=True)
def step_02_deploy_tinc_cluster():
    """ deploys the tinc cluster """

    tinc_cluster = lib.clusters.TincCluster()

    pool = Pool(processes=3)
    results = []
    for tinc_node in tinc_cluster.tinc_nodes:
        results.append(pool.apipe(tinc_node.install_patches))

    for stream in results:
        stream.get()

    def first_flow(tinc_node):
        """ executes a chain of tasks """
        tinc_node.install_cron_apt()
        tinc_node.install_fail2ban()
        tinc_node.install_tinc_software()

    pool = Pool(processes=3)
    results = []
    for tinc_node in tinc_cluster.tinc_nodes:
        results.append(pool.apipe(first_flow, tinc_node))
    for stream in results:
        stream.get()

    def second_flow(tinc_node, tinc_network):
        """ executes a chain of tasks """
        tinc_node.deploy_tinc_key_pair(
            tinc_network_name=tinc_network.tinc_network_name
        )

        tinc_node.deploy_tinc_conf_file(
            tinc_network_name=tinc_network.tinc_network_name
        )

        tinc_node.deploy_tinc_interface_files(
            tinc_network_name=tinc_network.tinc_network_name,
            tinc_network=tinc_network.tinc_network,
            tinc_netmask=tinc_network.tinc_netmask
        )

        tinc_node.deploy_tinc_peers_host_file(
            tinc_network_name=tinc_network.tinc_network_name
        )

        tinc_node.deploy_tinc_nets_boot_files(
            tinc_network_name=tinc_network.tinc_network_name
        )

    for tinc_network in tinc_cluster.tinc_networks:
        pool = Pool(processes=3)
        results = []
        for tinc_node in tinc_network.tinc_nodes:
            results.append(pool.apipe(second_flow, tinc_node, tinc_network))
        for stream in results:
            stream.get()

        for tinc_node in tinc_network.tinc_nodes:
            log_green('restarting tinc...')
            tinc_node.restart_tinc()
            sleep(15)


@task
@timecall(immediate=True)
def step_03_deploy_consul_cluster():
    """ deploys the consul cluster """

    consul_cluster = lib.clusters.ConsulCluster()

    def flow(consul_node):
        """ runs a chain of tasks """
        consul_node.deploy_consul_binary()
        consul_node.create_user_consul()
        consul_node.create_consul_directories()
        consul_node.create_consul_server_config()
        consul_node.download_consul_web_ui_files()
        consul_node.create_consul_server_init_script()

    pool = Pool(processes=3)
    results = []
    for consul_node in consul_cluster.consul_nodes:
        results.append(pool.apipe(flow, consul_node))
    for stream in results:
        stream.get()

    consul_cluster.consul_nodes[0].create_consul_bootstrap_config()
    consul_cluster.consul_nodes[0].start_bootstrap_cluster_process()
    sleep(30)

    for consul_node in consul_cluster.consul_nodes[1:]:
        consul_node.restart_consul_service()
        sleep(30)

    consul_cluster.consul_nodes[0].finish_bootstrap_cluster_process()
    sleep(30)

    for consul_node in consul_cluster.consul_nodes:
        consul_node.restart_consul_service()
        sleep(30)


@task
@timecall(immediate=True)
def step_04_deploy_git2consul_tinc_client():  # pylint: disable=invalid-name
    """ deploys the git2consul tinc client """

    consul_cluster = lib.clusters.ConsulCluster()
    git2consul = lib.git2consul.Git2ConsulService(consul_cluster)
    tinc_cluster = lib.clusters.TincCluster()

    git2consul.install_patches()
    with settings(warn_only=True):
        git2consul.reboot()
    git2consul.install_cron_apt()
    git2consul.install_fail2ban()

    git2consul.install_tinc_software()

    git2consul.deploy_tinc_key_pair(
        tinc_network_name=git2consul.tinc_network_name
    )

    git2consul.deploy_tinc_conf_file(
        git2consul.tinc_network_name
    )

    git2consul.deploy_tinc_interface_files(
        tinc_network_name=git2consul.tinc_network_name,
        tinc_network=git2consul.tinc_network,
        tinc_netmask=git2consul.tinc_netmask)

    git2consul.deploy_tinc_peers_host_file(
        tinc_network_name=git2consul.tinc_network_name)

    git2consul.deploy_tinc_nets_boot_files(
        tinc_network_name=git2consul.tinc_network_name)

    git2consul.restart_tinc()

    # must deploy public key to tinc-cluster boxes
    for tinc_node in tinc_cluster.tinc_nodes:
        tinc_node.deploy_tinc_client_host_file(git2consul)
        tinc_node.restart_tinc()
        sleep(30)

    git2consul.deploy_consul_binary()
    git2consul.create_user_consul()
    git2consul.create_consul_directories()
    git2consul.create_consul_client_config()
    git2consul.download_consul_web_ui_files()
    git2consul.create_consul_client_init_script(git2consul.tinc_network)
    git2consul.restart_consul_client_service()


@task
@timecall(immediate=True)
def step_05_deploy_git2consul():
    """ deploys the git2consul service """
    consul_cluster = lib.clusters.ConsulCluster()
    git2consul = lib.git2consul.Git2ConsulService(consul_cluster)

    git2consul.install_git2consul()
    git2consul.create_git2consul_config()
    git2consul.bootstrap_git2consul()
    git2consul.deploy_init_git2consul()


@task
@timecall(immediate=True)
def step_06_deploy_fsconsul():
    """ deploys the FSConsul servers """
    fsconsul_cluster = lib.clusters.FSconsulCluster()

    def flow(fsconsul_node):
        """ runs a chain of tasks """
        fsconsul_node.install_fsconsul()
        fsconsul_node.deploy_conf_fsconsul()
        fsconsul_node.deploy_init_fsconsul()

    pool = Pool(processes=3)
    results = []
    for fsconsul_node in fsconsul_cluster.fsconsul_nodes:
        results.append(pool.apipe(flow, fsconsul_node))
    for stream in results:
        stream.get()


@task
@timecall(immediate=True)
def step_07_deploy_dhcpd():
    """ deploys the DHCP server """
    dhcpd_cluster = lib.clusters.DHCPdCluster()

    def flow(dhcpd_node):
        """ runs a chain of tasks """
        dhcpd_node.deploy_dhcpd_binary()
        dhcpd_node.deploy_conf_dhcpd()
        dhcpd_node.restart_dhcpd()

    pool = Pool(processes=3)
    results = []
    for dhcpd_node in dhcpd_cluster.dhcpd_nodes:
        results.append(pool.apipe(flow, dhcpd_node))
    for stream in results:
        stream.get()


@task
@timecall(immediate=True)
def step_08_deploy_dnsserver():
    """ deploys the DNS server """
    dnsserver_cluster = lib.clusters.DNSSERVERCluster()

    def flow(dnsserver_node):
        """ runs a chain of tasks """
        dnsserver_node.deploy_dnsserver_binary()
        dnsserver_node.deploy_conf_dnsserver()
        dnsserver_node.restart_dnsserver()

    pool = Pool(processes=3)
    results = []
    for dnsserver_node in dnsserver_cluster.dnsserver_nodes:
        results.append(pool.apipe(flow, dnsserver_node))
    for stream in results:
        stream.get()


@task
@timecall(immediate=True)
def step_09_reboot_hosts():
    """ reboot the VMs """
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_node in tinc_cluster.tinc_nodes:
        with settings(warn_only=True):
            tinc_node.reboot()
            sleep(30)

    consul_cluster = lib.clusters.ConsulCluster()
    git2consul = lib.git2consul.Git2ConsulService(consul_cluster)
    with settings(warn_only=True):
        git2consul.reboot()


@task
@timecall(immediate=True)
def acceptance_tests():  # pylint: disable=too-many-statements
    """ runs the acceptance_tests """
    tinc_cluster = lib.clusters.TincCluster()
    consul_cluster = lib.clusters.ConsulCluster()
    git2consul = lib.git2consul.Git2ConsulService(consul_cluster)
    fsconsul_cluster = lib.clusters.FSconsulCluster()
    dhcpd_cluster = lib.clusters.DHCPdCluster()
    dnsserver_cluster = lib.clusters.DNSSERVERCluster()

    nodes = []
    nodes.extend(tinc_cluster.tinc_nodes)
    nodes.append(git2consul)

    pool = Pool()
    results = []
    for node in nodes:
        results.append(pool.apipe(test_that_patches_were_installed_on, node))
        results.append(pool.apipe(test_that_cron_apt_is_installed_on, node))
        results.append(pool.apipe(test_that_tinc_binaries_were_installed_on, node))
        results.append(pool.apipe(test_that_tinc_is_running_on, node))
        results.append(pool.apipe(test_that_fail2ban_is_running_on, node))

    for network in tinc_cluster.tinc_networks:
        results.append(pool.apipe(test_that_tinc_key_pairs_were_deployed_on, network))
        results.append(pool.apipe(test_that_tinc_conf_files_were_deployed_on, network))
        results.append(pool.apipe(test_that_tinc_interface_files_were_deployed_on, network))
        results.append(pool.apipe(test_that_tinc_nets_boot_files_were_deployed_on, network))
        results.append(pool.apipe(test_that_tinc_peers_host_files_were_deployed_on, network))
        results.append(pool.apipe(test_that_tinc_peers_are_pingable_on, network))


    nodes = []
    nodes.extend(consul_cluster.consul_nodes)
    nodes.append(git2consul)

    for node in nodes:
        results.append(pool.apipe(test_that_consul_binaries_were_installed_on, node))
        results.append(pool.apipe(test_that_consul_user_exists_on, node))
        results.append(pool.apipe(test_that_consul_directories_exists_on, node))
        results.append(pool.apipe(test_that_consul_web_ui_files_exists_on, node))
        results.append(pool.apipe(test_that_consul_peers_are_reachable_on, node))


    nodes = consul_cluster.consul_nodes
    for node in nodes:
        results.append(pool.apipe(test_that_consul_server_config_exists_on, node))
        results.append(pool.apipe(test_that_consul_server_init_exists_on, node))
        results.append(pool.apipe(test_that_consul_server_is_running_on, node))
        results.append(pool.apipe(test_that_fail2ban_is_running_on, node))


    nodes = fsconsul_cluster.fsconsul_nodes
    for node in nodes:
        results.append(pool.apipe(test_that_fsconsul_binaries_were_installed_on, node))
        results.append(pool.apipe(test_that_fsconsul_init_exists_on, node))
        results.append(pool.apipe(test_that_fsconsul_service_is_running_on, node))
        results.append(pool.apipe(test_that_fail2ban_is_running_on, node))


    results.append(pool.apipe(test_that_consul_client_config_exists_on, git2consul))
    results.append(pool.apipe(test_that_consul_client_init_exists_on, git2consul))
    results.append(pool.apipe(test_that_consul_client_is_running_on, git2consul))

    results.append(pool.apipe(test_that_git2consul_service_is_running_on, git2consul))
    results.append(pool.apipe(test_that_git2consul_init_exists_on, git2consul))

    results.append(pool.apipe(test_that_fail2ban_is_running_on, git2consul))


    nodes = dhcpd_cluster.dhcpd_nodes

    for node in nodes:
        results.append(pool.apipe(test_that_dhcpd_binaries_were_installed_on, node))
        results.append(pool.apipe(test_that_dhcpd_server_config_exists_on, node))
        results.append(pool.apipe(test_that_dhcpd_server_init_exists_on, node))
        results.append(pool.apipe(test_that_dhcpd_server_is_running_on, node))
        results.append(pool.apipe(test_that_fail2ban_is_running_on, node))

    nodes = dnsserver_cluster.dnsserver_nodes

    for node in nodes:
        results.append(pool.apipe(test_that_dnsserver_binaries_were_installed_on, node))
        results.append(pool.apipe(test_that_dnsserver_server_config_exists_on, node))
        results.append(pool.apipe(test_that_dnsserver_server_init_exists_on, node))
        results.append(pool.apipe(test_that_dnsserver_server_is_running_on, node))
        results.append(pool.apipe(test_that_fail2ban_is_running_on, node))

    for stream in results:
        stream.get()



@task
@timecall(immediate=True)
def clean():
    """ cleanup tasks """
    log_green('running clean')
    local("echo yes | ./terraform destroy")



@task
@timecall(immediate=True)
def provision_laptop():
    """ provisions box """
    log_green('running provision_laptop')

    local('tar -C laptop/ -cvzf /tmp/laptop.tgz .')

    with settings(
        host_string='ubuntu@laptop-public.aws.azulinho.com',
    ):
        put('/tmp/laptop.tgz', '/tmp/laptop.tgz')
        sudo('tar -C / -xvf /tmp/laptop.tgz')
        sudo('apt-get update')
        sudo('DEBIAN_FRONTEND=noninteractive apt-get -y --allow-remove-essential remove resolvconf dnsmasq')
        sudo('DEBIAN_FRONTEND=noninteractive apt-get -y install tinc')




@task
@timecall(immediate=True)
@retry(stop_max_attempt_number=3, wait_fixed=30000)
def laptop_acceptance_tests():
    """ runs the laptop based acceptance tests """
    log_green('running laptop_acceptance_tests')

    with settings(
        host_string='ubuntu@laptop-public.aws.azulinho.com',
    ):
        sudo('ifconfig -a | grep "10.254.0."')
        for ip_addr in ['10.254.0.1', '10.254.0.2', '10.254.0.3', '10.254.0.4']:
            sudo('ping -c 1 -w 20 %s' % ip_addr)

        sudo('/tests/test-dns')



@task
@timecall(immediate=True)
def jenkins_build():
    """ runs a full jenkins build """
    try:
        local('wget -c https://releases.hashicorp.com/terraform/0.11.2/'
              'terraform_0.11.2_linux_amd64.zip')
        local('rm -f terraform')
        local('unzip terraform_0.11.2_linux_amd64.zip')
        local('chmod +x terraform')

        execute(step_01_create_hosts)
        execute(run_it)
        sleep(30)  # give enough time for DHCP do its business
        execute(provision_laptop)
        execute(acceptance_tests)
        sleep(30)  # give enough time for the laptop to do its business
        execute(laptop_acceptance_tests)
        execute(clean)
    except:  # noqa: E722 pylint: disable=bare-except
        execute(clean)
        sys.exit(1)


#    ___main___

CFG = lib.mycookbooks.parse_config(
    os.getenv('CONFIG_YAML', 'config/config.yaml')
)

env.user = CFG['ec2_common']['username']
env.key_filename = CFG['ec2_common']['key_filename']
env.connection_attempts = 10
env.timeout = 30
env.warn_only = False

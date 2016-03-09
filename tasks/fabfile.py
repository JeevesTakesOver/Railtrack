# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.clusters
import lib.git2consul
import lib.mycookbooks
import tests.acceptance

from fabric.api import task, env, execute

from bookshelf.api_v1 import (sleep_for_one_minute)

from bookshelf.api_v2.ec2 import (connect_to_ec2, create_server_ec2)
from bookshelf.api_v2.logging_helpers import log_green


@task
def it():
    execute(step_02_deploy_tinc_cluster)
    execute(step_03_deploy_consul_cluster)
    execute(step_04_deploy_git2consul_tinc_client)
    execute(step_05_deploy_git2consul)
    execute(step_06_deploy_fsconsul)


@task
def step_01_create_hosts():

    for k_node, v_node in cfg['consul_servers']['servers'].items():

        connection = connect_to_ec2(
            region=v_node['region'],
            access_key_id=v_node['access_key_id'],
            secret_access_key=v_node['secret_access_key']
        )

        log_green('creating new EC2 instance for : %s' % k_node)

        instance = create_server_ec2(
            connection=connection,
            region=v_node['region'],
            disk_name=v_node['disk_name'],
            disk_size=v_node['disk_size'],
            ami=v_node['ami'],
            key_pair=v_node['key_pair'],
            instance_type=v_node['instance_type'],
            tags=v_node['tags'],
            security_groups=v_node['security_groups']
        )

        log_green('new EC2 instance for %s is %s' % (
            k_node,
            instance.public_dns_name)
        )

    v_node = cfg['git2consul']

    connection = connect_to_ec2(
        region=v_node['region'],
        access_key_id=v_node['access_key_id'],
        secret_access_key=v_node['secret_access_key']
    )
    log_green('creating new EC2 instance for : %s' % v_node['tinc_node'])

    instance = create_server_ec2(
        connection=connection,
        region=v_node['region'],
        disk_name=v_node['disk_name'],
        disk_size=v_node['disk_size'],
        ami=v_node['ami'],
        key_pair=v_node['key_pair'],
        instance_type=v_node['instance_type'],
        tags=v_node['tags'],
        security_groups=v_node['security_groups']
    )

    log_green('new EC2 instance for %s is %s' % (
        k_node,
        instance.public_dns_name)
    )


@task
def step_02_deploy_tinc_cluster():

    tinc_cluster = lib.clusters.TincCluster()
    for tinc_node in tinc_cluster.tinc_nodes:
        tinc_node.install_patches()
        tinc_node.install_tinc_software()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:

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

            tinc_node.restart_tinc()


@task
def step_03_deploy_consul_cluster():

    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        consul_node.deploy_consul_binary()
        consul_node.create_user_consul()
        consul_node.create_consul_directories()
        consul_node.create_consul_server_config()
        consul_node.download_consul_web_ui_files()
        consul_node.create_consul_server_init_script()

    consul_cluster.consul_nodes[0].create_consul_bootstrap_config()
    consul_cluster.consul_nodes[0].start_bootstrap_cluster_process()

    for consul_node in consul_cluster.consul_nodes[1:]:
        consul_node.restart_consul_service()
        sleep_for_one_minute()

    consul_cluster.consul_nodes[0].finish_bootstrap_cluster_process()


@task
def step_04_deploy_git2consul_tinc_client():

    git2consul = lib.git2consul.Git2ConsulService()
    tinc_cluster = lib.clusters.TincCluster()

    git2consul.install_patches()

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
        sleep_for_one_minute

    git2consul.deploy_consul_binary()
    git2consul.create_user_consul()
    git2consul.create_consul_directories()
    git2consul.create_consul_client_config(git2consul.tinc_cluster.tinc_nodes)
    git2consul.create_consul_client_config(git2consul.tinc_cluster.tinc_nodes)
    git2consul.download_consul_web_ui_files()
    git2consul.create_consul_client_init_script(git2consul.tinc_network)
    git2consul.restart_consul_client_service()


@task
def step_05_deploy_git2consul():
    git2consul = lib.git2consul.Git2ConsulService()

    git2consul.install_git2consul()
    git2consul.create_git2consul_config()
    git2consul.bootstrap_git2consul()
    git2consul.deploy_init_git2consul()


@task
def step_06_deploy_fsconsul():
    fsconsul_cluster = lib.clusters.FSconsulCluster()

    for fsconsul_node in fsconsul_cluster.fsconsul_nodes:
        fsconsul_node.install_fsconsul()
        fsconsul_node.deploy_conf_fsconsul()
        fsconsul_node.deploy_init_fsconsul()


@task
def run_tests():
    tests.acceptance.test_that_patches_were_installed_on_tinc_nodes()
    tests.acceptance.test_that_tinc_binaries_were_installed()
    tests.acceptance.test_that_tinc_key_pairs_were_deployed()
    tests.acceptance.test_that_tinc_conf_files_were_deployed()
    tests.acceptance.test_that_tinc_interface_files_were_deployed()
    tests.acceptance.test_that_tinc_nets_boot_files_were_deployed
    tests.acceptance.test_that_tinc_peers_host_files_were_deployed
    tests.acceptance.test_that_tinc_is_running()
    tests.acceptance.test_that_tinc_peers_are_pingable()

    tests.acceptance.test_that_consul_binaries_were_installed()
    tests.acceptance.test_that_consul_user_exists()
    tests.acceptance.test_that_consul_directories_exists()
    tests.acceptance.test_that_consul_server_config_exists()
    tests.acceptance.test_that_consul_web_ui_files_exists()
    tests.acceptance.test_that_consul_server_init_exists()
    tests.acceptance.test_that_consul_servers_are_running()
    tests.acceptance.test_that_consul_peers_are_reachable()

    tests.acceptance.test_that_patches_were_installed_on_git2consul_nodes()
    tests.acceptance.test_that_tinc_binaries_were_installed_on_git2consul_box()


def get_consul_encryption_key():
    return cfg['consul']['encrypt']

"""
    ___main___
"""

cfg = lib.mycookbooks.parse_config('config/config.yaml')

# tinc_network_name = cfg['roles']['core-vpn-node']['tinc_network_name']
# tinc_network = cfg['roles']['core-vpn-node']['tinc_network']
# tinc_netmask = cfg['roles']['core-vpn-node']['tinc_netmask']

# consul_encryption_key = cfg['consul']['encrypt']


env.user = cfg['ec2_common']['username']
env.key_filename = cfg['ec2_common']['key_filename']
env.connection_attempts = 10
env.timeout = 30
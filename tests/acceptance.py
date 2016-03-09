
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.clusters
import lib.git2consul

from fabric.context_managers import settings, hide
from fabric.api import sudo

from lib.mycookbooks import (
    parse_config,
)


def test_that_patches_were_installed_on_tinc_nodes():
    tinc_cluster = lib.clusters.TincCluster()

    line = '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded'

    for tinc_node in tinc_cluster.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            cmd = sudo('apt-get upgrade')
            assert line in cmd.stdout
            assert cmd.return_code == 0


def test_that_tinc_binaries_were_installed():
    tinc_cluster = lib.clusters.TincCluster()

    line = '/usr/sbin/tincd'

    for tinc_node in tinc_cluster.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            cmd = sudo('which tincd')
            assert line in cmd.stdout


def test_that_tinc_key_pairs_were_deployed():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:
            with settings(
                hide('stdout', 'running'),
                host_string=tinc_node.host_string,
                private_key_filename=tinc_node.private_key
            ):
                tinc_network_name = tinc_network.tinc_network_name

                cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
                assert 'rsa_key.priv' in cmd.stdout
                assert 'rsa_key.pub' in cmd.stdout


def test_that_tinc_conf_files_were_deployed():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:
            with settings(
                hide('stdout', 'running'),
                host_string=tinc_node.host_string,
                private_key_filename=tinc_node.private_key
            ):
                tinc_network_name = tinc_network.tinc_network_name

                cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
                assert 'tinc.conf' in cmd.stdout


def test_that_tinc_interface_files_were_deployed():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:
            with settings(
                hide('stdout', 'running'),
                host_string=tinc_node.host_string,
                private_key_filename=tinc_node.private_key
            ):
                tinc_network_name = tinc_network.tinc_network_name

                cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
                assert 'tinc-up' in cmd.stdout
                assert 'tinc-down' in cmd.stdout


def test_that_tinc_nets_boot_files_were_deployed():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):

            cmd = sudo('ls -l /etc/tinc/')
            assert 'nets.boot' in cmd.stdout


def test_that_tinc_peers_host_files_were_deployed():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:
            with settings(
                hide('stdout', 'running'),
                host_string=tinc_node.host_string,
                private_key_filename=tinc_node.private_key
            ):
                tinc_network_name = tinc_network.tinc_network_name

                cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
                for tinc_peer in tinc_node.tinc_peers:
                    assert tinc_peer.tinc_node in cmd.stdout


def test_that_tinc_is_running():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_node in tinc_cluster.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            cmd = sudo('ps -ef | grep tincd | grep -v grep ')
            assert 'tincd' in cmd.stdout

            cmd = sudo('service tinc status')
            assert 'running' in cmd.stdout


def test_that_tinc_peers_are_pingable():
    tinc_cluster = lib.clusters.TincCluster()

    for tinc_network in tinc_cluster.tinc_networks:
        for tinc_node in tinc_network.tinc_nodes:
            with settings(
                hide('stdout', 'running'),
                host_string=tinc_node.host_string,
                private_key_filename=tinc_node.private_key
            ):
                tinc_network_name = tinc_network.tinc_network_name

                for tinc_peer in tinc_node.tinc_peers:
                    cmd = sudo('ping -c 1 %s' % tinc_peer.tinc_ip)
                    assert cmd.return_code == 0


def test_that_consul_binaries_were_installed():
    consul_cluster = lib.clusters.ConsulCluster()

    line = '/usr/local/bin/consul'
    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            cmd = sudo('which consul')
            assert line in cmd.stdout


def test_that_consul_user_exists():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            assert sudo('getent passwd consul').return_code == 0


def test_that_consul_directories_exists():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            cmd = sudo('ls -l /etc/consul.d')
            assert 'bootstrap' in cmd.stdout
            assert 'server' in cmd.stdout
            assert 'client' in cmd.stdout
            assert 'consul consul' in sudo('ls -ld /var/consul').stdout


def test_that_consul_server_config_exists():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            cmd = sudo('ls -l /etc/consul.d/server/')
            assert 'config.json' in cmd.stdout


def test_that_consul_web_ui_files_exists():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            cmd = sudo('ls -l /home/consul/')
            assert 'index.html' in cmd.stdout


def test_that_consul_server_init_exists():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            cmd = sudo('ls -l /etc/systemd/system/')
            assert 'consul-server.service' in cmd.stdout


def test_that_consul_servers_are_running():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            line = 'consul agent -config-dir /etc/consul.d/server'
            cmd = sudo('ps -ef')
            assert line in cmd.stdout


def test_that_consul_peers_are_reachable():
    consul_cluster = lib.clusters.ConsulCluster()

    for consul_node in consul_cluster.consul_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=consul_node.host_string,
            private_key_filename=consul_node.private_key
        ):
            line = 'consul agent -config-dir /etc/consul.d/server'
            cmd = sudo('consul members | grep server | grep alive')
            for consul_peer in consul_node.consul_peers:
                assert consul_peer.consul_ip in cmd.stdout


def test_that_patches_were_installed_on_git2consul_nodes():
    git2consul = lib.git2consul.Git2ConsulService()

    line = '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded'

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        cmd = sudo('apt-get upgrade')
        assert line in cmd.stdout
        assert cmd.return_code == 0


def test_that_tinc_binaries_were_installed_on_git2consul_box():
    git2consul = lib.git2consul.Git2ConsulService()

    line = '/usr/sbin/tincd'

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        cmd = sudo('which tincd')
        assert line in cmd.stdout







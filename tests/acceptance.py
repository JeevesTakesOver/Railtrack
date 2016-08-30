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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import lib.clusters
import lib.git2consul

from fabric.context_managers import settings, hide
from fabric.api import sudo


def echo(func):
    "This decorator echos the arguments passed to a function before calling it"
    fname = func.func_name

    def echo_func(*args, **kwargs):
        print fname
        return func(*args, **kwargs)

    return echo_func


@echo
def test_that_patches_were_installed_on(node):

    line = '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('apt-get -u upgrade --assume-no')
        assert line in cmd.stdout
        assert cmd.return_code == 0


@echo
def test_that_cron_apt_is_installed_on(node):

    line = 'cron-apt'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('dpkg -l')
        assert line in cmd.stdout
        assert cmd.return_code == 0


@echo
def test_that_tinc_binaries_were_installed_on(node):

    line = '/usr/sbin/tincd'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('which tincd')
        assert line in cmd.stdout


@echo
def test_that_tinc_key_pairs_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            tinc_network_name = tinc_network.tinc_network_name

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
            assert 'rsa_key.priv' in cmd.stdout
            assert 'rsa_key.pub' in cmd.stdout


@echo
def test_that_tinc_conf_files_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            tinc_network_name = tinc_network.tinc_network_name

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
            assert 'tinc.conf' in cmd.stdout


@echo
def test_that_tinc_interface_files_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            tinc_network_name = tinc_network.tinc_network_name

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/%s' % tinc_network_name)
            assert 'tinc-up' in cmd.stdout
            assert 'tinc-down' in cmd.stdout


@echo
def test_that_tinc_nets_boot_files_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/')
            assert 'nets.boot' in cmd.stdout


@echo
def test_that_tinc_peers_host_files_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            tinc_network_name = tinc_network.tinc_network_name

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/%s/hosts' % tinc_network_name)
            for tinc_peer in tinc_node.tinc_peers:
                assert tinc_peer.tinc_name in cmd.stdout


@echo
def test_that_tinc_is_running_on(node):

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('ps -ef | grep tincd | grep -v grep ')
        assert 'tincd' in cmd.stdout

        cmd = sudo('service tinc status')
        assert 'running' in cmd.stdout


@echo
def test_that_fail2ban_is_running_on(node):

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('ps -ef | grep fail2ban | grep -v grep ')
        assert 'fail2ban' in cmd.stdout

        cmd = sudo('service fail2ban status')
        assert 'running' in cmd.stdout


@echo
def test_that_tinc_peers_are_pingable_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):
            print(" running on %s" % tinc_node.host_string)

            for tinc_peer in tinc_node.tinc_peers:
                cmd = sudo('ping -c 1 %s' % tinc_peer.tinc_ip)
                assert cmd.return_code == 0


@echo
def test_that_consul_binaries_were_installed_on(consul_node):

    line = '/usr/local/bin/consul'
    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('which consul')
        assert line in cmd.stdout


@echo
def test_that_consul_user_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        assert sudo('getent passwd consul').return_code == 0


@echo
def test_that_consul_directories_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d')
        assert 'bootstrap' in cmd.stdout
        assert 'server' in cmd.stdout
        assert 'client' in cmd.stdout
        assert 'consul consul' in sudo('ls -ld /var/consul').stdout


@echo
def test_that_consul_server_config_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d/server/')
        assert 'config.json' in cmd.stdout


@echo
def test_that_consul_client_config_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d/client/')
        assert 'config.json' in cmd.stdout


@echo
def test_that_consul_web_ui_files_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /home/consul/')
        assert 'index.html' in cmd.stdout


@echo
def test_that_consul_server_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        assert 'consul-server.service' in cmd.stdout


@echo
def test_that_consul_client_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        assert 'consul-client.service' in cmd.stdout


@echo
def test_that_consul_server_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        line = 'consul agent -config-dir /etc/consul.d/server'
        cmd = sudo('ps -ef')
        assert line in cmd.stdout

        cmd = sudo('systemctl is-active consul-server')
        assert 'active' in cmd.stdout


@echo
def test_that_consul_client_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        line = 'consul agent -config-dir /etc/consul.d/client'
        cmd = sudo('ps -ef')
        assert line in cmd.stdout

        cmd = sudo('systemctl is-active consul-client')
        assert 'active' in cmd.stdout


@echo
def test_that_consul_peers_are_reachable_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('consul members | grep server | grep alive')
        for consul_peer in consul_node.consul_peers:
            assert consul_peer.consul_ip in cmd.stdout


@echo
def test_that_fsconsul_service_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        line = 'fsconsul -configFile=/etc/fsconsul.json'
        cmd = sudo('ps -ef')
        assert line in cmd.stdout

        cmd = sudo('systemctl is-active fsconsul')
        assert 'active' in cmd.stdout


@echo
def test_that_fsconsul_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        assert 'fsconsul.service' in cmd.stdout


@echo
def test_that_fsconsul_binaries_were_installed_on(consul_node):

    line = 'fsconsul'
    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('which fsconsul')
        assert line in cmd.stdout


@echo
def test_that_git2consul_init_exists_on(git2consul):

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        print(" running on %s" % git2consul.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        assert 'git2consul.service' in cmd.stdout


@echo
def test_that_git2consul_service_is_running_on(git2consul):

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        print(" running on %s" % git2consul.host_string)

        cmd = sudo('systemctl is-active git2consul')
        assert 'active' in cmd.stdout

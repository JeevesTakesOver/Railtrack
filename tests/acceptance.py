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

from fabric.context_managers import settings, hide
from fabric.api import sudo, env

from retrying import retry

env.abort_on_prompts = True
env.colorize_errors = True
env.disable_known_hosts = True
env.parallel = True
env.pool_size = 16
env.warn_only = True


def echo(func):
    "This decorator echos the arguments passed to a function before calling it"
    fname = func.func_name

    def echo_func(*args, **kwargs):
        print fname
        return func(*args, **kwargs)

    return echo_func


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_patches_were_installed_on(node):

    line = '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('apt-get -u upgrade --assume-no')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))
        try:
            assert cmd.return_code == 0
        except Exception as detail:
            raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_cron_apt_is_installed_on(node):

    line = 'cron-apt'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('dpkg -l')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        try:
            assert cmd.return_code == 0
        except Exception as detail:
            raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_tinc_binaries_were_installed_on(node):

    line = '/usr/sbin/tincd'

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('which tincd')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
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
            try:
                assert 'rsa_key.priv' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))

            try:
                assert 'rsa_key.pub' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
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
            try:
                assert 'tinc.conf' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
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

            try:
                assert 'tinc-up' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))

            try:
                assert 'tinc-down' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_tinc_nets_boot_files_were_deployed_on(tinc_network):

    for tinc_node in tinc_network.tinc_nodes:
        with settings(
            hide('stdout', 'running'),
            host_string=tinc_node.host_string,
            private_key_filename=tinc_node.private_key
        ):

            print(" running on %s" % tinc_node.host_string)

            cmd = sudo('ls -l /etc/tinc/')
            try:
                assert 'nets.boot' in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
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
                try:
                    assert tinc_peer.tinc_name in cmd.stdout
                except Exception as detail:
                    raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_tinc_is_running_on(node):

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('COLUMNS=1000 ps -edalf | grep tincd | grep -v grep ')
        try:
            assert 'tincd' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        cmd = sudo('systemctl is-active tinc')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_fail2ban_is_running_on(node):

    with settings(
        hide('stdout', 'running'),
        host_string=node.host_string,
        private_key_filename=node.private_key
    ):
        print(" running on %s" % node.host_string)

        cmd = sudo('COLUMNS=1000 ps -edalf | grep fail2ban | grep -v grep ')
        try:
            assert 'fail2ban' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        cmd = sudo('systemctl is-active fail2ban')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
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
                try:
                    assert cmd.return_code == 0
                except Exception as detail:
                    raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_binaries_were_installed_on(consul_node):

    line = '/usr/local/bin/consul'
    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('which consul')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_user_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        try:
            assert sudo('getent passwd consul').return_code == 0
        except Exception as detail:
            raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_directories_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d')
        try:
            assert 'bootstrap' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        try:
            assert 'server' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        try:
            assert 'client' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        try:
            assert 'consul consul' in sudo('ls -ld /var/consul').stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_server_config_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d/server/')
        try:
            assert 'config.json' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_client_config_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/consul.d/client/')
        try:
            assert 'config.json' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_web_ui_files_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /home/consul/')
        try:
            assert 'index.html' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_server_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        try:
            assert 'consul-server.service' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_client_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        try:
            assert 'consul-client.service' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_server_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('systemctl is-active consul-server')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        line = 'consul agent -config-dir /etc/consul.d/server'
        cmd = sudo('COLUMNS=1000 ps -edalf')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_client_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        line = 'consul agent -config-dir /etc/consul.d/client'
        cmd = sudo('COLUMNS=1000 ps -edalf')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        cmd = sudo('systemctl is-active consul-client')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_consul_peers_are_reachable_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('consul members | grep server | grep alive')
        for consul_peer in consul_node.consul_peers:
            try:
                assert consul_peer.consul_ip in cmd.stdout
            except Exception as detail:
                raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_fsconsul_service_is_running_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        line = 'fsconsul -configFile=/etc/fsconsul.json'
        cmd = sudo('COLUMNS=1000 ps -edalf')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        cmd = sudo('systemctl is-active fsconsul')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_fsconsul_init_exists_on(consul_node):

    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        try:
            assert 'fsconsul.service' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_fsconsul_binaries_were_installed_on(consul_node):

    line = 'fsconsul'
    with settings(
        hide('stdout', 'running'),
        host_string=consul_node.host_string,
        private_key_filename=consul_node.private_key
    ):
        print(" running on %s" % consul_node.host_string)

        cmd = sudo('which fsconsul')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_git2consul_init_exists_on(git2consul):

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        print(" running on %s" % git2consul.host_string)

        cmd = sudo('ls -l /etc/systemd/system/')
        try:
            assert 'git2consul.service' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_git2consul_service_is_running_on(git2consul):

    with settings(
        hide('stdout', 'running'),
        host_string=git2consul.host_string,
        private_key_filename=git2consul.private_key
    ):
        print(" running on %s" % git2consul.host_string)

        cmd = sudo('systemctl is-active git2consul')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dhcpd_binaries_were_installed_on(dhcpd_server):

    with settings(
        hide('stdout', 'running'),
        host_string=dhcpd_server.host_string,
        private_key_filename=dhcpd_server.private_key
    ):
        print(" running on %s" % dhcpd_server.host_string)

        cmd = sudo('systemctl is-active dhcpd')
        try:
            assert 'active' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dhcpd_server_is_running_on(dhcpd_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dhcpd_node.host_string,
        private_key_filename=dhcpd_node.private_key,
    ):
        print(" running on %s" % dhcpd_node.host_string)

        cmd = sudo('systemctl status isc-dhcp-server >/dev/null')
        try:
            assert cmd.return_code == 0
        except Exception as detail:
            raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dhcpd_binaries_were_installed_on(dhcpd_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dhcpd_node.host_string,
        private_key_filename=dhcpd_node.private_key
    ):
        print(" running on %s" % dhcpd_node.host_string)

        cmd = sudo('which dhcpd')
        try:
            assert 'dhcpd' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        cmd = sudo('which nsupdate')
        try:
            assert 'nsupdate' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dhcpd_server_config_exists_on(dhcpd_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dhcpd_node.host_string,
        private_key_filename=dhcpd_node.private_key
    ):
        print(" running on %s" % dhcpd_node.host_string)

        cmd = sudo('ls -l /etc/dhcp/dhcpd.conf ')
        try:
            assert 'dhcpd.conf' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dhcpd_server_init_exists_on(dhcpd_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dhcpd_node.host_string,
        private_key_filename=dhcpd_node.private_key
    ):
        print(" running on %s" % dhcpd_node.host_string)

        cmd = sudo('ls -l /etc/init/isc-dhcp-server.conf')
        try:
            assert 'dhcp' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dnsserver_binaries_were_installed_on(dnsserver_server):

    with settings(
        hide('stdout', 'running'),
        host_string=dnsserver_server.host_string,
        private_key_filename=dnsserver_server.private_key
    ):
        print(" running on %s" % dnsserver_server.host_string)

        cmd = sudo('which named')
        try:
            assert 'named' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dnsserver_server_is_running_on(dnsserver_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dnsserver_node.host_string,
        private_key_filename=dnsserver_node.private_key,
    ):
        print(" running on %s" % dnsserver_node.host_string)

        cmd = sudo('systemctl status bind9 >/dev/null')
        try:
            assert cmd.return_code == 0
        except Exception as detail:
            raise Exception("%s %s" % (cmd.return_code, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dnsserver_binaries_were_installed_on(dnsserver_node):

    line = 'named'
    with settings(
        hide('stdout', 'running'),
        host_string=dnsserver_node.host_string,
        private_key_filename=dnsserver_node.private_key
    ):
        print(" running on %s" % dnsserver_node.host_string)

        cmd = sudo('which named')
        try:
            assert line in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dnsserver_server_config_exists_on(dnsserver_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dnsserver_node.host_string,
        private_key_filename=dnsserver_node.private_key
    ):
        print(" running on %s" % dnsserver_node.host_string)

        cmd = sudo('ls -l /var/cache/bind/')
        try:
            assert 'tinc-core-vpn.hosts' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

        try:
            assert '0.254.10.in-addr.arpa.hosts' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))


@echo
@retry(stop_max_attempt_number=3, wait_fixed=5000)
def test_that_dnsserver_server_init_exists_on(dnsserver_node):

    with settings(
        hide('stdout', 'running'),
        host_string=dnsserver_node.host_string,
        private_key_filename=dnsserver_node.private_key
    ):
        print(" running on %s" % dnsserver_node.host_string)

        cmd = sudo('systemctl is-enabled bind9')
        try:
            assert 'enabled' in cmd.stdout
        except Exception as detail:
            raise Exception("%s %s" % (cmd.stdout, detail))

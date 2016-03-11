# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from time import sleep
from bookshelf.api_v2.logging_helpers import log_green
from fabric.context_managers import cd, settings, hide
from fabric.api import sudo
from fabric.contrib.files import upload_template

from bookshelf.api_v2.pkg import (
    apt_install,
)
from bookshelf.api_v2.os_helpers import add_usr_local_bin_to_path
import lib.host


class ConsulHost(lib.host.Host):
    """ A virtual consul Host object providing methods for installing and
    maintaining the consul software
    """
    def __init__(self, ssh_credentials):
        """ Generates a ConsulHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        lib.host.Host.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_consul_binary(self):
        """ Install the consul software """
        log_green('deploying consul binary...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):

            apt_install(packages=['unzip'])
            with cd('/usr/local/bin'):
                if 'consul' not in sudo('ls /usr/local/bin'):
                    sudo(
                        'wget -c https://releases.hashicorp.com/consul/%s'
                        '/consul_%s_linux_amd64.zip' % (self.version,
                                                        self.version)
                    )
                    sudo('unzip *zip')
                    sudo('rm -f *.zip')
            add_usr_local_bin_to_path()

    def create_user_consul(self):
        """ creates the user consul """
        log_green('creating user for consul...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
            warn_only=True,
        ):
            if 'consul' not in sudo('getent passwd consul'):
                sudo('useradd -m -d /home/consul -s /bin/bash consul')

    def create_consul_directories(self):
        """ creates consul directories """
        log_green('creating directories for consul...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            sudo('mkdir -p /etc/consul.d/{bootstrap,server,client}')
            sudo('mkdir -p /var/consul')
            sudo('chown consul:consul /var/consul')

    def download_consul_web_ui_files(self):
        """ installs the consul web ui files """
        log_green('install web ui for consul...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            if 'dist' not in sudo('ls /home/consul/'):
                with cd('/home/consul'):
                    sudo(
                        'wget -c '
                        'https://releases.hashicorp.com/consul/'
                        '%s/consul_%s_web_ui.zip' % (
                            self.version, self.version),
                        user='consul'
                    )

                    sudo('unzip -o *.zip', user='consul')
                    sudo('rm -f *.zip', user='consul')


class ConsulServer(ConsulHost):
    """ An object representing the Consul Server service """
    def __init__(self,
                 consul_ip,
                 consul_interface,
                 consul_peers,
                 datacenter,
                 version,
                 consul_encryption_key,
                 ssh_credentials):
        """ Generates a ConsulServer object

        params:
            string consul_ip: the ip that consul will bind to
            string consul_interface: the network interface consul will bind to
            array consul_peers: a list of consul peers for this node
            string datacenter: the consul datacenter
            string version: the consul version
            string: consul_encryption_key: the consul encryption shared key
            object ssh_credentials: ssh credentials to login to the host
        """
        self.consul_ip = consul_ip
        self.consul_interface = consul_interface
        self.consul_peers = consul_peers
        self.datacenter = datacenter
        self.version = version
        self.consul_encryption_key = consul_encryption_key
        ConsulHost.__init__(self, ssh_credentials=ssh_credentials)

    def create_consul_server_config(self):
        """ creates the consul server config file """
        log_green('create consul server config...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            consul_server_file = '/etc/consul.d/server/config.json'

            peer_list = [
                consul_peer.consul_ip for consul_peer in self.consul_peers
            ]

            upload_template(
                filename='consul.conf.j2',
                template_dir='templates',
                destination=consul_server_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'bootstrap': 'false',
                    'server': 'true',
                    'datacenter': self.datacenter,
                    'encrypt': self.consul_encryption_key,
                    'start_join': json.dumps(peer_list)
                }
            )

    def create_consul_server_init_script(self):
        """ creates the consul server init file """
        log_green('create consul server init script...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            consul_init_file = '/etc/systemd/system/consul-server.service'

            upload_template(filename='consul-init-server.j2',
                            template_dir='templates',
                            destination=consul_init_file,
                            use_sudo=True,
                            use_jinja=True,
                            context={'consul_interface': self.consul_interface,
                                     'node_ip': self.consul_ip})
            sudo('systemctl daemon-reload')

    def create_consul_bootstrap_config(self):
        """ creates the consul server bootstrap config """
        log_green('create consul server bootstrap config...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            consul_bootstrap_file = '/etc/consul.d/bootstrap/config.json'

            upload_template(filename='consul.bootstrap.j2',
                            template_dir='templates',
                            destination=consul_bootstrap_file,
                            use_sudo=True,
                            use_jinja=True,
                            context={'bootstrap': 'true',
                                     'server': 'true',
                                     'datacenter': self.datacenter,
                                     'encrypt': self.consul_encryption_key})

    def start_bootstrap_cluster_process(self):
        """ starts the bootstrap cluster process  """
        log_green('start bootstrap cluster process...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            if 'bootstrapped' not in sudo('ls /etc/consul.d/'):
                sudo(
                    "su - consul -c "
                    "'consul agent "
                    "-config-dir /etc/consul.d/bootstrap "
                    "-bind %s &'" % self.consul_ip)

                sudo('touch /etc/consul.d/bootstrapped.in_progress')

    def restart_consul_service(self):
        """ restarts the consul server service """
        log_green('restarting consul server service ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            sudo('service consul-server restart')
            sleep(30)

    def finish_bootstrap_cluster_process(self):
        """ finishes the consul bottstrapping process """
        log_green('finish bootstrap cluster process ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            if 'bootstrapped.in_progress' in sudo('ls /etc/consul.d/'):
                sudo("kill $( ps -ef | grep consul | grep -v grep | "
                     "awk '{ print $2 }')")

                sudo('service consul-server restart')
                sudo('rm /etc/consul.d/bootstrapped.in_progress')
                sudo('touch /etc/consul.d/bootstrapped.locked')


class ConsulClient(ConsulHost):
    """ An object representing a Consul Client service """
    def __init__(self, ssh_credentials, consul_cluster):
        """ Generates a ConsulClient object

        params:
            object ssh_credentials: ssh credentials to login to the host
        """
        ConsulHost.__init__(self, ssh_credentials=ssh_credentials)
        self.consul_peers = consul_cluster.consul_nodes

    def create_consul_client_config(self):
        """ creates the consul client config file """
        log_green('create consul client config ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            consul_nodes_ip = [
                item.consul_ip for item in self.consul_peers
            ]

            consul_client_file = '/etc/consul.d/client/config.json'
            upload_template(
                filename='consul-client.j2',
                template_dir='templates',
                destination=consul_client_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'server': 'false',
                    'datacenter': self.datacenter,
                    'encrypt': self.consul_encryption_key,
                    'start_join': json.dumps(consul_nodes_ip)
                }
            )

    def create_consul_client_init_script(self, tinc_network_name):
        """ creates the consul client init file """
        log_green('create consul client init script ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            consul_init_file = '/etc/systemd/system/consul-client.service'

            upload_template(filename='consul-init-client.j2',
                            template_dir='templates',
                            destination=consul_init_file,
                            use_sudo=True,
                            use_jinja=True,
                            context={'tinc_network_name': tinc_network_name,
                                     'node_ip': self.tinc_ip})
            sudo('systemctl daemon-reload')

    def restart_consul_client_service(self):
        """ restarts the consul client service """
        log_green('restart consul client service ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            sudo('service consul-client restart')

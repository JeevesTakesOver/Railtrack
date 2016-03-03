# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.host import Host
from fabric.contrib.files import upload_template
from fabric.api import sudo
from fabric.context_managers import settings, hide
from fabric.operations import put as file_upload
from bookshelf.api_v2.pkg import (
    apt_install,
    enable_apt_repositories,
)

from bookshelf.api_v2.logging_helpers import log_green
from bookshelf.api_v2.os_helpers import (
    install_ubuntu_development_tools,
    add_usr_local_bin_to_path
)

from lib.mycookbooks import (
    install_tinc,
    ubuntu14_required_packages
)


class TincNetwork(object):
    """ A virtual Tinc Network object composed of multiple TincEndpoints,
    a network name, address_block and netmask"""

    def __init__(self,
                 tinc_network_name,
                 tinc_network,
                 tinc_netmask,
                 tinc_nodes):
        self.tinc_network_name = tinc_network_name
        self.tinc_network = tinc_network
        self.tinc_netmask = tinc_netmask
        self.tinc_nodes = tinc_nodes
        """ Generates a TincNetwork object

        params:
            string tinc_network_name: name of the tinc-network
            string tinc_network: CIDR block for the tinc-network
            string tinc_netmask: netmask for the tinc_network
            array tinc_nodes: list of TincEndpoint objects
        """


class TincHost(Host):
    """ A virtual Tinc Host object providing methods for installing and
    maintaining the tinc software
    """
    def __init__(self, ssh_credentials):
        """ Generates a TincHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        Host.__init__(self, ssh_credentials=ssh_credentials)

    def install_tinc_software(self):
        """ Install the tinc software """
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):

            enable_apt_repositories('deb',
                                    'http://archive.ubuntu.com/ubuntu',
                                    '$(lsb_release -sc)',
                                    'main universe restricted multiverse')
            install_ubuntu_development_tools()
            apt_install(packages=ubuntu14_required_packages())
            add_usr_local_bin_to_path()
            install_tinc()

    def restart_tinc(self):
        """ restarts the tinc service """
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            sudo('service tinc restart')


class TincPeer(object):
    """ An object representing a tinc peer of the current tinc node """
    def __init__(self, tinc_name, tinc_ip, tinc_public_key, public_dns_name):
        """ Generates a TincPeer object

        params:
            string tinc_name: tinc node name
            string tinc_ip: ip address of the node in the tinc network
            string tinc_public_key: public key of the node in the tinc network
            string public_dns_name: internet routable dns name of the node
        """
        self.tinc_name = tinc_name
        self.tinc_ip = tinc_ip
        self.tinc_public_key = tinc_public_key
        self.public_dns_name = public_dns_name


class TincEndpoint(TincHost):
    """ An object representing the Tinc service """
    def __init__(self,
                 tinc_name,
                 tinc_ip,
                 public_dns_name,
                 tinc_private_key,
                 tinc_public_key,
                 tinc_peers,
                 ssh_credentials):
        """ Generates a TincEndpoint object

        params:
            string tinc_name: tinc node name
            string tinc_ip: ip address of the node in the tinc network
            string tinc_public_key: public key of the node in the tinc network
            string tinc_private_key: private key of the node in the tinc
            network
            string public_dns_name: internet routable dns name of the node
            list tinc_peers: collection of the tinc peers of this tinc node
            object ssh_credentials: ssh credentials to login to the host
        """
        self.tinc_name = tinc_name
        self.tinc_ip = tinc_ip
        self.tinc_peers = tinc_peers
        self.tinc_private_key = tinc_private_key
        self.tinc_public_key = tinc_public_key
        self.ssh_credentials = ssh_credentials

        TincHost.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_tinc_key_pair(self, tinc_network_name):
        """ deploys the tinc private key for the network """
        log_green('deploying tinc key pair ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            sudo('mkdir -p /etc/tinc/%s' % tinc_network_name)

            file_upload(
                local_path=self.tinc_private_key,
                remote_path='/etc/tinc/%s/rsa_key.priv' % tinc_network_name,
                use_sudo=True,
                mode="0600"
            )

            sudo(
                'echo "%s" > /etc/tinc/%s/rsa_key.pub' % (
                    self.tinc_public_key,
                    tinc_network_name))

            sudo('chown root:root -R /etc/tinc/')

    def deploy_tinc_conf_file(self, tinc_network_name):
        """ deploys the tinc configuration file for the network  """
        log_green('deploying tinc config file ...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            tinc_config_file = '/etc/tinc/%s/tinc.conf' % tinc_network_name
            sudo('mkdir -p /etc/tinc/%s' % tinc_network_name)

            list_of_peers = [
                tinc_peer.tinc_name for tinc_peer in self.tinc_peers
            ]
            upload_template(filename='tinc.conf.j2',
                            template_dir='templates',
                            destination=tinc_config_file,
                            use_sudo=True,
                            use_jinja=True,
                            context={'tinc_node': self.tinc_name,
                                     'tinc_nodes': list_of_peers}
                            )

    def deploy_tinc_interface_files(self,
                                    tinc_network_name,
                                    tinc_network,
                                    tinc_netmask):
        """ deploys the tinc interface file for the network  """
        log_green('deploying tinc interface file ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            for item in ['tinc-up', 'tinc-down']:
                tinc_interface_file = '/etc/tinc/%s/%s' % (tinc_network_name,
                                                           item)

                upload_template(filename='%s.j2' % item,
                                template_dir='templates',
                                destination=tinc_interface_file,
                                use_sudo=True,
                                use_jinja=True,
                                context={'tinc_ip': self.tinc_ip,
                                         'tinc_netmask': tinc_netmask,
                                         'tinc_network': tinc_network})

                sudo('chmod 755 %s' % tinc_interface_file)
                sudo('chown root:root %s' % tinc_interface_file)

    def deploy_tinc_client_host_file(self, tinc_client):
        """ deploys the tinc client public key for the network  """

        log_green('deploying tinc client host file ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            sudo('mkdir -p /etc/tinc/%s/hosts' % tinc_client.tinc_network_name)

            tinc_client_host_file = '/etc/tinc/%s/hosts/%s' % (
                tinc_client.tinc_network_name,
                tinc_client.tinc_name
            )

            upload_template(
                filename='host.j2',
                template_dir='templates',
                destination=tinc_client_host_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'tinc_node': tinc_client.tinc_name,
                    'public_ip_address': tinc_client.public_dns_name,
                    'tinc_ip': tinc_client.tinc_ip,
                    'tinc_public_key': tinc_client.tinc_public_key
                },
            )

    def deploy_tinc_peers_host_file(self, tinc_network_name):
        """ deploys the tinc peer public key for the network  """
        log_green('deploying tinc peer host file ...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            sudo('mkdir -p /etc/tinc/%s/hosts' % tinc_network_name)

            for peer in self.tinc_peers:

                tinc_host_file = '/etc/tinc/%s/hosts/%s' % (
                    tinc_network_name,
                    peer.tinc_name
                )

                upload_template(
                    filename='host.j2',
                    template_dir='templates',
                    destination=tinc_host_file,
                    use_sudo=True,
                    use_jinja=True,
                    context={
                        'tinc_node': peer.tinc_name,
                        'public_ip_address': peer.public_dns_name,
                        'tinc_ip': peer.tinc_ip,
                        'tinc_public_key': peer.tinc_public_key
                    },
                )

    def deploy_tinc_nets_boot_files(self, tinc_network_name):
        """ deploys the tinc nets boot file  """
        log_green('deploying tinc nets boot file ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            tinc_nets_file = '/etc/tinc/nets.boot'

            upload_template(
                filename='nets.boot.j2',
                template_dir='templates',
                destination=tinc_nets_file,
                use_sudo=True,
                use_jinja=True,
                context={'tinc_network_name': tinc_network_name}
            )

            sudo('chown root:root %s' % tinc_nets_file)

# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bookshelf.api_v2.logging_helpers import log_green
from fabric.context_managers import cd, settings, hide
from fabric.api import sudo, run
from fabric.contrib.files import upload_template

from lib.mycookbooks import (
    parse_config,
)

import lib.consul
import lib.clusters


class Git2ConsulHost(lib.consul.ConsulClient):
    """ A virtual git2consul host object providing methods for installing and
    maintaining the git2consul software
    """
    def __init__(self, ssh_credentials, consul_cluster):
        """ Generates a Git2ConsulHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        lib.consul.ConsulClient.__init__(self,
                                         ssh_credentials=ssh_credentials,
                                         consul_cluster=consul_cluster)

    def install_git2consul(self):
        """ installs the git2consul software """
        log_green('installing git2consul ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            with hide('stdout', 'running'):
                sudo('apt-get update')
                sudo('apt-get install -y npm nodejs nodejs-legacy git')
                sudo('npm install git2consul')

    def deploy_init_git2consul(self):
        """ installs the git2consul init script """
        log_green('deploying git2consul init script ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            git2consul_init_file = '/etc/systemd/system/git2consul.service'

            upload_template(
                filename='git2consul.init.conf',
                template_dir='templates',
                destination=git2consul_init_file,
                use_sudo=True,
                use_jinja=True,
                context={'username': self.username,
                         'groupname': self.username},
            )
            sudo('systemctl daemon-reload')
            sudo('systemctl enable git2consul')
            sudo('systemctl restart git2consul')


class Git2ConsulService(Git2ConsulHost,
                        lib.tinc.TincEndpoint):
    """ A git2consul service object providing """
    def __init__(self, consul_cluster):
        """ Generates a Git2ConsulService object """
        self.cfg = parse_config('config/config.yaml')
        self.public_dns_name = self.cfg['git2consul']['public_dns_name']
        self.username = self.cfg['git2consul']['username']
        self.private_key = self.cfg['git2consul']['key_filename']
        self.tinc_network_name = self.cfg['git2consul']['tinc_network_name']
        self.tinc_network = self.cfg['git2consul']['tinc_network']
        self.tinc_netmask = self.cfg['git2consul']['tinc_netmask']
        self.datacenter = self.cfg['git2consul']['datacenter']
        self.version = self.cfg['git2consul']['version']
        self.consul_encryption_key = self.cfg['git2consul']['encrypt']
        self.consul_cluster = consul_cluster
        self.tinc_cluster = lib.clusters.TincCluster()
        self.git_url = self.cfg['git2consul']['git_url']
        self.git_root = self.cfg['git2consul']['git_root']
        self.pooling_interval = self.cfg['git2consul']['pooling_interval']
        self.git_branches = self.cfg['git2consul']['git_branches']
        self.service_name = self.cfg['git2consul']['service_name']

        ssh_credentials = lib.host.SshCredentials(
            public_dns_name=self.public_dns_name,
            username=self.username,
            private_key=self.private_key
        )

        lib.tinc.TincEndpoint.__init__(
            self,
            tinc_name=self.cfg['git2consul']['tinc_node'],
            tinc_ip=self.cfg['git2consul']['tinc_ip'],
            public_dns_name=self.cfg['git2consul']['public_dns_name'],
            tinc_private_key=self.cfg['git2consul']['tinc_private_key'],
            tinc_public_key=self.cfg['git2consul']['tinc_public_key'],
            tinc_peers=self.tinc_cluster.tinc_nodes,
            ssh_credentials=ssh_credentials
        )

        lib.git2consul.Git2ConsulHost.__init__(
            self,
            ssh_credentials=ssh_credentials,
            consul_cluster=consul_cluster
        )

    def create_git2consul_config(self):
        """ creates the git2consul config file """
        log_green('deploying git2consul config file ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            git2consul_bootstrap_file = '/etc/git2consul.json'

            upload_template(
                filename='git2consul.json.j2',
                template_dir='templates',
                destination=git2consul_bootstrap_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'service_name': self.service_name,
                    'git_url': self.git_url,
                    'git_branches': self.git_branches,
                    'git_root': self.git_root,
                    'pooling_interval': self.pooling_interval
                },
            )

    def bootstrap_git2consul(self):
        """ bootstraps git2consul """
        log_green('bootstrapping git2consul ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            with cd('/home/%s/node_modules/git2consul' % self.username):
                run('nodejs utils/config_seeder.js /etc/git2consul.json')

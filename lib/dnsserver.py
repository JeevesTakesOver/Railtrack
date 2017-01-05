# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et

# Copyright (C) 2016  Jorge Costa

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
from bookshelf.api_v2.os_helpers import (
    add_usr_local_bin_to_path,
    systemd
)
import lib.host

class DNSSERVERHost(lib.host.Host):
    """ A virtual DNSSERVER Host object providing methods for installing and
    maintaining the DNSSERVER software
    """
    def __init__(self, ssh_credentials):
        """ Generates a DNSSERVERHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        lib.host.Host.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_dnsserver_binary(self):
        """ Install the DNSSERVER software """
        log_green('deploying DNSSERVER binary...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            apt_install(packages=['bind9'])

class DNSSERVERServer(DNSSERVERHost):
    """ An object representing the DNSSERVER Server service """
    def __init__(self,
                 dnsserver_role,
                 zone_name,
                 allow_transfer,
                 reverse_zone,
	             ns1,
                 ns2,
				 secret,
                 listen_ip,
                 primary_ip,
                 ssh_credentials):
        """ Generates a DNSSERVERServer object

        params:
            string zone_name: DNS zone
            string allow_transfer: allow_transfer
            string reverse_zone: reverse_zone
            string dnsserver_role: either master or slave
            string ns1: ns1 ip address
            string ns2: ns2 ip address
            string secret: rdnc.key
            string listen_ip: ip where the service is listening
            string primary_ip: ip for the master DNS server
            object ssh_credentials: ssh credentials to login to the host
        """
        self.dnsserver_role = dnsserver_role
        self.zone_name = zone_name
        self.allow_transfer = allow_transfer
        self.reverse_zone = reverse_zone
        self.ns1 = ns1
        self.ns2 = ns2
        self.secret = secret
        self.listen_ip = listen_ip
        self.primary_ip = primary_ip
        self.ssh_credentials = ssh_credentials
        DNSSERVERHost.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_conf_dnsserver(self):
        """ creates the DNSSERVER server config file """
        log_green('create DNSSERVER server config...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            DNSSERVER_named_conf_options_file = '/etc/bind/named.conf.options'
            upload_template(
                filename='named.conf.options.j2',
                template_dir='templates',
                destination=DNSSERVER_named_conf_options_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'listen_ip': self.listen_ip
                }
            )

            DNSSERVER_named_conf_file = '/etc/bind/named.conf.local'
            upload_template(
                filename='named.conf.local.j2',
                template_dir='templates',
                destination=DNSSERVER_named_conf_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'dnsserver_role': self.dnsserver_role,
                    'allow_transfer': self.allow_transfer,
                    'zone_name': self.zone_name,
                    'ns1': self.ns1,
                    'ns2': self.ns2,
                    'reverse_zone': self.reverse_zone
                }
            )

            DNSSERVER_hosts_file = '/var/cache/bind/%s.hosts' % self.zone_name

            upload_template(
                filename='named.hosts.j2',
                template_dir='templates',
                destination=DNSSERVER_hosts_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'dnsserver_role': self.dnsserver_role,
                    'zone_name': self.zone_name,
                    'allow_transfer': self.allow_transfer,
                    'reverse_zone': self.reverse_zone,
                    'ns1': self.ns1,
                    'ns2': self.ns2,
                }
            )

            DNSSERVER_reverse_file = '/var/cache/bind/%s.hosts' % self.reverse_zone

            upload_template(
                filename='reverse.hosts.j2',
                template_dir='templates',
                destination=DNSSERVER_reverse_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'dnsserver_role': self.dnsserver_role,
                    'zone_name': self.zone_name,
                    'allow_transfer': self.allow_transfer,
                    'reverse_zone': self.reverse_zone,
                    'ns1': self.ns1,
                    'ns2': self.ns2,
                }
            )

            DNSSERVER_key_file = '/etc/bind/rndc.key'

            upload_template(
                filename='rndc.key.j2',
                template_dir='templates',
                destination=DNSSERVER_key_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'secret': self.secret
                }
            )
            sudo('chown root:bind /etc/bind/*')
            sudo('chmod g=rw,u=rw /etc/bind/*')
            sudo('chown root:bind /var/cache/bind/*')
            sudo('chmod g=rw,u=rw /var/cache/bind/*')
            sudo('chown root:bind /etc/bind/rndc.key')
            sudo('chmod 660 /etc/bind/rndc.key')


    def restart_dnsserver(self):
        """ restarts the DNSSERVER service """
        log_green('restarting DNSSERVER...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            systemd(
                service='bind9',
                start=True,
                enabled=True,
                restart=True
            )

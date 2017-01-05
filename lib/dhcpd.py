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


class DHCPdHost(lib.host.Host):
    """ A virtual dhcpd Host object providing methods for installing and
    maintaining the dhcpd software
    """
    def __init__(self, ssh_credentials):
        """ Generates a DHCPdHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        lib.host.Host.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_dhcpd_binary(self):
        """ Install the dhcpd software """
        log_green('deploying dhcpd binary...')

        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            apt_install(packages=['isc-dhcp-server', 'dnsutils'])

class DHCPdServer(DHCPdHost):
    """ An object representing the DHCPd Server service """
    def __init__(self,
                 dhcpd_role,
                 listen_ip,
                 domain_name,
                 nameservers,
                 pool_range,
                 secret,
                 reverse_zone,
                 peer_address,
                 subnet,
                 netmask,
                 failover_peer,
                 primary_ip,
                 listen_interface,
                 ssh_credentials):
        """ Generates a DHCPdServer object

        params:
            string dhcpd_role: either primary or secondary
            string listen_ip: which IP should DHCPd listen on
            string domain_name: domain name for the DHCP pool
            string nameservers: nameservers to provide to the client
            string pool_range: ip range pool
            string secret: shared key between primary and secondary
            string reverse_zone: reverse_zone name
            string peer_address: IP address of the peer dhcpd server
            string subnet: subnet to offer leases
            string netmask: netmask for offers
            string primary_ip: IP address of the DHCPd master
            string listen_interface: which interface to serve DHCP requests
            object ssh_credentials: ssh credentials to login to the host
        """
        self.dhcpd_role = dhcpd_role
        self.listen_ip = listen_ip
        self.domain_name = domain_name
        self.nameservers = nameservers
        self.pool_range = pool_range
        self.secret = secret
        self.reverse_zone = reverse_zone
        self.peer_address = peer_address
        self.subnet = subnet
        self.netmask = netmask
        self.failover_peer = failover_peer
        self.primary_ip = primary_ip
        self.listen_interface = listen_interface
        self.ssh_credentials = ssh_credentials
        DHCPdHost.__init__(self, ssh_credentials=ssh_credentials)

    def deploy_conf_dhcpd(self):
        """ creates the DHCPd server config file """
        log_green('create dhcpd server config...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            dhcpd_server_file = '/etc/dhcp/dhcpd.conf'

            upload_template(
                filename='dhcpd.conf.j2',
                template_dir='templates',
                destination=dhcpd_server_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'dhcpd_role': self.dhcpd_role,
                    'listen_ip': self.listen_ip,
                    'domain_name': self.domain_name,
                    'nameservers': self.nameservers,
                    'pool_range': self.pool_range,
                    'secret': self.secret,
                    'reverse_zone': self.reverse_zone,
                    'peer_address': self.peer_address,
                    'subnet': self.subnet,
                    'netmask': self.netmask,
                    'failover_peer': self.failover_peer,
                    'primary_ip': self.primary_ip,
                    'listen_interface': self.listen_interface
                }
            )

            dhcpd_defaults_file = '/etc/default/isc-dhcp-server'

            upload_template(
                filename='etc.default.isc-dhcp-server.j2',
                template_dir='templates',
                destination=dhcpd_defaults_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'listen_interface': self.listen_interface
                }
            )

            DNSSERVER_add2dns_file = '/etc/dhcp/add2dns'

            upload_template(
                filename='add2dns.j2',
                template_dir='templates',
                destination=DNSSERVER_add2dns_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'secret': self.secret,
                    'domain_name': self.domain_name,
                    'reverse_zone': self.reverse_zone,
                    'primary_ip': self.primary_ip
                }
            )

            sudo('chown root:dhcpd /etc/dhcp/add2dns')
            sudo('chmod 750 /etc/dhcp/add2dns')

            DNSSERVER_removefromdns_file = '/etc/dhcp/removefromdns'

            upload_template(
                filename='removefromdns.j2',
                template_dir='templates',
                destination=DNSSERVER_removefromdns_file,
                use_sudo=True,
                use_jinja=True,
                context={
                    'secret': self.secret,
                    'domain_name': self.domain_name,
                    'reverse_zone': self.reverse_zone,
                    'primary_ip': self.primary_ip
                }
            )

            sudo('chown root:dhcpd /etc/dhcp/removefromdns')
            sudo('chmod 750 /etc/dhcp/removefromdns')


            DNSSERVER_apparmor_file = '/etc/apparmor.d/usr.sbin.dhcpd'

            upload_template(
                filename='apparmor.usr.sbin.dhcpd.j2',
                template_dir='templates',
                destination=DNSSERVER_apparmor_file,
                use_sudo=True,
                use_jinja=True,
                context={}
            )

            sudo('chown root:root /etc/apparmor.d/usr.sbin.dhcpd')
            sudo('service apparmor reload')

    def restart_dhcpd(self):
        """ restarts the dhcpd service """
        log_green('restarting dhcpd...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):
            systemd(
                service='isc-dhcp-server',
                start=True,
                enabled=True,
                restart=True
            )

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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fabric.context_managers import settings, hide

from bookshelf.api_v2.os_helpers import (
    install_os_updates,
)

from bookshelf.api_v2.pkg import apt_install

from bookshelf.api_v2.cloud import wait_for_ssh
from bookshelf.api_v2.logging_helpers import log_green

from lib.mycookbooks import (
    upgrade_kernel_and_grub,
)
from retrying import retry
from fabric.api import sudo


class SshCredentials(object):
    """ an object providining enough information that a function can use to
    connect to an existing Host using ssh
    """
    def __init__(self, public_dns_name, username, private_key):
        """ params:

            string public_dns_name: FQDN for ssh access

            string username: 'username' which contains a valid public_key in
            its .ssh/authorized_keys file.

            string private_key: location of the ssh private_key file, matching
            the public_key listed in the .ssh/authorized_keys of 'username'

        """
        self.public_dns_name = public_dns_name
        self.username = username
        self.private_key = private_key


class Host(object):
    """ an host/VM object providing generic methods related to the object host,
    and not related to any application running on this host.

    Examples: installation of patches, kernel upgrades.
    """
    def __init__(self, ssh_credentials):
        """ params:
            object ssh_credentials: ssh_credentials object
        """

        self.private_key = ssh_credentials.private_key
        self.public_dns_name = ssh_credentials.public_dns_name
        self.username = ssh_credentials.username
        self.host_string = "%s@%s" % (self.username,
                                      self.public_dns_name)

    @retry(stop_max_attempt_number=3, wait_fixed=10000)
    def install_patches(self):
        """ installs the latest updates, updates the kernel and reboots,
            the instance/host/vm.
            This function blocks until ssh is available after reboot
        """
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            log_green(self.host_string)
            install_os_updates(distribution='ubuntu14.04')
            upgrade_kernel_and_grub(do_reboot=False)

    @retry(stop_max_attempt_number=3, wait_fixed=10000)
    def reboot(self):
        """ reboots the VM 
            This function blocks until ssh is available after reboot
        """
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            log_green(self.host_string)
            sudo('reboot')
            wait_for_ssh(self.public_dns_name)

    @retry(stop_max_attempt_number=3, wait_fixed=10000)
    def install_cron_apt(self):
        """ installs apt-cron which provides automatic security updates """
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            log_green(self.host_string)
            apt_install(packages=['cron-apt'])

    @retry(stop_max_attempt_number=3, wait_fixed=10000)
    def install_fail2ban(self):
        """ installs fail2ban to block ssh brute-force attacks"""
        with settings(
            hide('running', 'stdout'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            log_green(self.host_string)
            apt_install(packages=['fail2ban'])

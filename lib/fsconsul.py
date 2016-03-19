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

from fabric.context_managers import cd, settings, hide, shell_env
from fabric.contrib.files import upload_template
from fabric.api import sudo, run

from bookshelf.api_v2.logging_helpers import log_green
from bookshelf.api_v2.os_helpers import (
    add_usr_local_bin_to_path
)
from bookshelf.api_v2.git import git_clone
from bookshelf.api_v2.pkg import apt_install

import lib.host
import lib.tinc


class FSconsulHost(lib.host.Host):
    """ A virtual fsconsul Host object providing methods for installing and
    maintaining the fsconsul software
    """
    def __init__(self, ssh_credentials):
        """ Generates a FSconsulHost object

        params:
            object ssh_credentials: ssh credentials for the Host
        """
        lib.host.Host.__init__(self, ssh_credentials=ssh_credentials)

    def install_fsconsul(self):
        """ installs fsconsul """
        log_green('installing fsconsul ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            add_usr_local_bin_to_path()
            apt_install(packages=['git'])

            with cd('/usr/local'):
                if 'go' not in sudo('ls -l /usr/local/bin'):
                    sudo('wget -c https://storage.googleapis.com/golang/'
                         'go1.5.3.linux-amd64.tar.gz')
                    sudo('tar xzf go1.5.3.linux-amd64.tar.gz')

            if 'fsconsul' not in sudo('ls -l /usr/local/bin'):
                git_clone('https://github.com/Cimpress-MCP/fsconsul.git',
                          'fsconsul')
                run('mkdir -p gopath')
                run('mkdir -p bin')
                with shell_env(
                    PATH='$PATH:/usr/local/go/bin',
                    GOPATH='/home/%s/gopath' % self.username,
                    GOBIN='/home/%s/bin' % self.username
                ):
                    with cd('fsconsul'):
                        run('go get -x github.com/mitchellh/gox')
                        run('go get github.com/Sirupsen/logrus')
                        run('go get github.com/armed/mkdirp')
                        run('go get github.com/cimpress-mcp/gosecret/api')
                        run('go get -x github.com/hashicorp/consul/api')
                        run('go install .')
                sudo('cp /home/%s/bin/fsconsul /usr/local/bin' % self.username)

    def deploy_init_fsconsul(self):
        """ installs the fsconsul init file """
        log_green('installing fsconsul ...')
        log_green('deploying init script for fsconsul ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key
        ):
            fsconsul_init_file = '/etc/systemd/system/fsconsul.service'

            upload_template(
                filename='fsconsul.init.j2',
                template_dir='templates',
                destination=fsconsul_init_file,
                use_sudo=True,
                use_jinja=True,
                context={},
            )

            sudo('systemctl daemon-reload')
            sudo('service fsconsul restart')


class FSconsulServer(FSconsulHost):
    """ An object representing the fsconsul service """
    def __init__(self,
                 fsconsul_prefix,
                 fsconsul_path,
                 datacenter,
                 ssh_credentials):
        """ Generates a FSconsulServer object

        params:
            string fsconsul_prefix: prefix in consul to monitor for changes
            string fsconsul_path: where to write the changes in the filesystem
            string datacenter: the consul datacenter
            object ssh_credentials: ssh credentials to login to the host
        """

        self.tinc_cluster = lib.clusters.TincCluster()
        self.datacenter = datacenter
        self.fsconsul_path = fsconsul_path
        self.fsconsul_prefix = fsconsul_prefix
        self.consul = datacenter
        lib.fsconsul.FSconsulHost.__init__(
            self, ssh_credentials=ssh_credentials
        )

    def deploy_conf_fsconsul(self):
        """ installs the fsconsul configuration file """
        log_green('deploying config file for fsconsul ...')
        with settings(
            hide('stdout', 'running'),
            host_string=self.host_string,
            private_key_filename=self.private_key,
        ):

            fsconsul_conf_file = '/etc/fsconsul.json'

            upload_template(
                filename='fsconsul.json.j2',
                template_dir='templates',
                destination=fsconsul_conf_file,
                use_sudo=True,
                use_jinja=True,
                context={'prefix': self.fsconsul_prefix,
                         'path': self.fsconsul_path,
                         'dc': self.datacenter},
            )

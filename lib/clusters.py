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

import lib.tinc
import lib.consul
import lib.fsconsul
import lib.dhcpd
import lib.dnsserver

from lib.mycookbooks import (
    parse_config,
)


class TincCluster(object):
    """ A Cluster object composed of multiple Tinc Servers which form an L2
    network """
    def __init__(self):
        """ consumes the config.yaml parameters files generating a set of
        attributes that map to the different Tinc Cluster objects.

        tinc_nodes: List of lib.tinc.TincEndpoint objects (Running Tinc Daemons)
        tinc_networks: List of lib.tinc.TincNetwork objects (Virtual Tinc Networks)
        """
        self.cfg = parse_config(
            os.getenv('CONFIG_YAML', 'config/config.yaml')
        )
        self.tinc_nodes = []
        self.tinc_networks = []

        # some background on the Tinc archictecture,
        # We can have '3-n' Hosts running a tinc deamon each, serving a number
        # of '1-n' tinc networks (different network segments), where each tinc
        # network can contain one or more hosts, identified by a set of
        # attributes:
        # * tinc public key, tinc private key,
        # * tinc ip address in the tinc network
        # * [for servers: tinc daemon ip address on the internet]
        #

        # collate all the networks and all the lib.tinc.TincEndpoint objects in each
        # network.
        # these lib.tinc.TincEndpoint objects combined make our TincCluster object.
        for k_tinc_network, v_tinc_network in self.cfg['tinc_networks'].items():
            tinc_nodes = []
            for k_node, v_node in v_tinc_network['servers'].items():

                tinc_nodes.append(
                    lib.tinc.TincEndpoint(
                        tinc_name=k_node,
                        tinc_ip=v_node['tinc_ip'],
                        tinc_private_key=v_node['tinc_private_key'],
                        tinc_public_key=v_node['tinc_public_key'],
                        public_dns_name=v_node['public_dns_name'],
                        tinc_peers=[],
                        ssh_credentials=lib.host.SshCredentials(
                            public_dns_name=v_node['public_dns_name'],
                            username=v_node['username'],
                            private_key=v_node['key_filename']
                        )
                    )
                )

            # update tinc_peers, each tinc_node needs to know about all the
            # other tinc servers available on the network.
            for tinc_node in tinc_nodes:
                tinc_node.tinc_peers = set(tinc_nodes) - set([tinc_node])

            tinc_network = lib.tinc.TincNetwork(
                tinc_network_name=k_tinc_network,
                tinc_network=v_tinc_network['tinc_network'],
                tinc_netmask=v_tinc_network['tinc_netmask'],
                tinc_nodes=tinc_nodes
            )

            self.tinc_networks.append(tinc_network)

        # make sure we don't have tinc_nodes duplicated.
        seen = set()
        for tinc_network in self.tinc_networks:
            for tinc_node in tinc_network.tinc_nodes:
                if tinc_node not in seen:
                    self.tinc_nodes.append(tinc_node)
                    seen.add(tinc_node)


class ConsulCluster(object):
    """ A Cluster object composed of multiple Consul Servers """
    def __init__(self):
        """ consumes the config.yaml parameters files generating a set of
        attributes that map to the different Consul Cluster objects.

        consul_nodes: List of lib.consul.ConsulServers objects (hosts that run consul
        in server mode)
        version: consul version
        datacenter: consul datacenter string
        consul_encryption_key: common encryption key to all consul daemons
        """

        self.cfg = parse_config(
            os.getenv('CONFIG_YAML', 'config/config.yaml')
        )
        self.version = self.cfg['consul_servers']['version']
        self.datacenter = self.cfg['consul_servers']['datacenter']
        self.consul_encryption_key = self.cfg['consul_servers']['encrypt']
        self.consul_nodes = []

        # some background on the Consul archictecture
        # We can have '3-n' Hosts running a consul server deamon each.
        # These are identified as part of a logical 'datacenter', and will
        # accept connections from consul daemons running in client and server
        # mode which happen to provide the correct encryption key.

        # these lib.consul.ConsulServer objects combined make our ConsulCluster object.
        for k_node, v_node in self.cfg['consul_servers']['servers'].items():
            self.consul_nodes.append(
                lib.consul.ConsulServer(
                    consul_ip=v_node['consul_ip'],
                    consul_interface=v_node['consul_interface'],
                    consul_peers=[],
                    datacenter=self.datacenter,
                    version=self.version,
                    consul_encryption_key=self.consul_encryption_key,
                    ssh_credentials=lib.host.SshCredentials(
                        public_dns_name=v_node['public_dns_name'],
                        username=v_node['username'],
                        private_key=v_node['key_filename']
                    )
                )
            )

        # update consul_peers, each consul node should know about the other
        # consul servers in the network
        for consul_node in self.consul_nodes:
            consul_node.consul_peers = set(self.consul_nodes) - set(
                [consul_node])


class FSconsulCluster(object):
    """ A 'Cluster' object composed of multiple fsonsul Servers,
    this is not a true cluster, as the fsconsul servers are not linked in any
    way.  This object represents a list of all the fsconsul servers associated
    with a particular Consul Cluster
    """

    def __init__(self):
        """ consumes the config.yaml parameters files generating a set of
        attributes that map to the different FSConsul objects.

        fsconsul_nodes: List of FSlib.consul.ConsulServers objects
        """

        self.consul_cluster = ConsulCluster()
        self.cfg = parse_config(
            os.getenv('CONFIG_YAML', 'config/config.yaml')
        )
        self.fsconsul_nodes = []
        self.datacenter = self.cfg['git2consul']['datacenter']

        # some background on the FSConsul archictecture
        # each server managed by fsconsul will have a consul server running
        # locally. Fsconsul will connect the local consul server to retrieve
        # the list of files to generate in the filesystem.

        # these FSlib.consul.ConsulServer objects combined make our FSConsulCluster object
        for consul_node in self.consul_cluster.consul_nodes:

            self.fsconsul_nodes.append(
                lib.fsconsul.FSconsulServer(
                    fsconsul_prefix='/self_service_vpn',
                    fsconsul_path='/etc/tinc/core-vpn/hosts',
                    datacenter=self.datacenter,
                    ssh_credentials=lib.host.SshCredentials(
                        public_dns_name=consul_node.public_dns_name,
                        username=consul_node.username,
                        private_key=consul_node.private_key
                    )
                )
            )

        # TODO do we need this? fsconsul nodes have no peers
        # update consul_peers
        for fsconsul_node in self.fsconsul_nodes:
            fsconsul_node.consul_peers = set(self.fsconsul_nodes) - set([fsconsul_node])

class DHCPdCluster(object):
    """ A 'Cluster' object composed of primary and secondaries DHCPd servers,
    """

    def __init__(self):
        """ consumes the config.yaml parameters files generating a set of
        attributes that map to the different dhcpd objects.

        dhcpd_nodes: List of DHCPd servers objects
        """

        self.cfg = parse_config(
            os.getenv('CONFIG_YAML', 'config/config.yaml')
        )
        self.dhcpd_nodes = []

        # some background on the DHCPd archictecture:
        # each HA setup will have a primary one secondary

        for k_node, v_node in self.cfg['dhcpd_servers']['servers'].items():
            self.dhcpd_nodes.append(
                lib.dhcpd.DHCPdServer(
                    dhcpd_role=v_node['dhcpd_role'],
                    listen_ip=v_node['listen_ip'],
                    domain_name=v_node['domain_name'],
                    nameservers=v_node['nameservers'],
                    pool_range=v_node['pool_range'],
                    secret=v_node['secret'],
                    reverse_zone=v_node['reverse_zone'],
                    peer_address=v_node['peer_address'],
                    subnet=v_node['subnet'],
                    netmask=v_node['netmask'],
                    failover_peer=v_node['failover_peer'],
                    primary_ip=v_node['primary_ip'],
                    listen_interface=v_node['listen_interface'],
                    ssh_credentials=lib.host.SshCredentials(
                        public_dns_name=v_node['public_dns_name'],
                        username=v_node['username'],
                        private_key=v_node['key_filename']
                    )
                )
            )

class DNSSERVERCluster(object):
    """ A 'Cluster' object composed of primary and secondaries DNSSERVER servers,
    """

    def __init__(self):
        """ consumes the config.yaml parameters files generating a set of
        attributes that map to the different dhcpd objects.

        dhcpd_nodes: List of DNSSERVER servers objects
        """

        self.cfg = parse_config(
            os.getenv('CONFIG_YAML', 'config/config.yaml')
        )
        self.dnsserver_nodes = []

        # some background on the DNSSERVER archictecture:
        # each HA setup will have a primary one secondary
        for k_node, v_node in self.cfg['dnsserver_servers']['servers'].items():
            self.dnsserver_nodes.append(
                lib.dnsserver.DNSSERVERServer(
                    zone_name=v_node['zone_name'],
                    reverse_zone=v_node['reverse_zone'],
                    allow_transfer=v_node['allow_transfer'],
	                dnsserver_role=v_node['dnsserver_role'],
	                ns1=v_node['ns1'],
	                ns2=v_node['ns2'],
	                secret=v_node['secret'],
                    listen_ip=v_node['listen_ip'],
                    primary_ip=v_node['primary_ip'],
                    ssh_credentials=lib.host.SshCredentials(
                        public_dns_name=v_node['public_dns_name'],
                        username=v_node['username'],
                        private_key=v_node['key_filename']
                    )
                )
            )

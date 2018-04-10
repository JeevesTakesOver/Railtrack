.. image:: https://badge.waffle.io/Azulinho/Board.png?label=ready&title=Ready 
 :target: https://waffle.io/Azulinho/Board 
 :alt: 'Stories in Ready'
.. image:: https://api.codacy.com/project/badge/Grade/5360e3ee056647b3931899b2079a4be7
   :alt: Codacy Badge
   :target: https://app.codacy.com/app/Azulinho/Railtrack?utm_source=github.com&utm_medium=referral&utm_content=JeevesTakesOver/Railtrack&utm_campaign=badger


=========
Railtrack
=========

* A building block for a cloud based infrastructure.
* A distributed L2 switch across multiple cloud providers.
* A resilient, meshed VPN/Network layer.
* Built on `Tinc <https://www.tinc-vpn.org/>`_
* Self-serviceable.
* Access control provided by GitHub/GitLab/Bitbucket.
* Manages Pets
* Static or DHCP IP allocation of Pets on the VPN.
* Python based, built on Fabric and `Bookshelf <https://github.com/pyBookshelf/bookshelf>`_


The code in this repository provisions a fully meshed, geographically
distributed, resilient, Layer 2 encrypted virtual network.

This allows for deploying any networked service across the internet, including 
multi-cloud setups with a single network namespace. As it is a layer 2 VPN, it
also supports multicast,unicast services or floating virtual-ips.

Services can be added to the virtual network simply by binding the listening
ports of those services to the local virtual network ip addresses. This allows
for increased security as access to services is only available to hosts
connected in the VPN.

Management of the hosts allowed to access the virtual network is performed
through git and pull requests.
To add/remove a host of the virtual network, install the tinc client on that
box, generate a private/public key, update the tinc config to connect to the
central tinc nodes, and add the public key to the following repository:

https://github.com/JeevesTakesOver/menagerie


Workflow
========

The expected workflow is that any team member can add new team members or
services to the virtual network by commiting the tinc public keys of the tinc
clients to the `github repository <https://github.com/JeevesTakesOver/menagerie>`_ 
and submit a pull request.
This PR is peer reviewed and once approved, brings the new service online on
the virtual network.
This workflow allows for teams to self-service themselves, adding new hosts or 
team members or removing their access when they leave the project.


Usage cases
===========

* A new starter which upon joining his team, submits a pull request asking for access to the company services by providing his public key.

* Allow teams to be self-sufficient in adding/removing services to the virtual network.

* Full audits and history through git repository history.

* Single Network segment across multi-cloud vendors

* Highly available VPN services

* Cross-Region/Global network

* Deployment of secure services only available through the VPN.

* Mobile workers


How does it do it?
===================

There are four hosts:

3 core hosts (core01..03), running `tinc <https://www.tinc-vpn.org/>`_, `isc-dhcp-server <https://www.isc.org/>`_, `bind9 <http://www.bind9.net/>`_, `consul <https://www.consul.io/>`_, `fsconsul <https://github.com/Cimpress-MCP/fsconsul>`_.

1 git2consul host, running `git2consul <https://github.com/breser/git2consul>`_ and a `consul client <https://www.consul.io/>`_


As soon a public key is commited to the `menagerie github repository <https://github.com/JeevesTakesOver/menagerie>`_
a process running in the `git2consul host <https://github.com/breser/git2consul>`_ 
will forward the new key to a `consul cluster <https://www.consul.io/>`_ running on the three core vpn nodes.
On each one of the core vpn master, another process `fsconsul <https://github.com/Cimpress-MCP/fsconsul>`_
will write down the ssh keys into the `tinc host directories <https://www.tinc-vpn.org/>`_ and reload the daemons.
At this point the new tinc client is allowed access to the VPN and all its services.

On the client side, the tinc interface-up scripts will ask for a DHCP ip address through the VPN link.
On the first core-vpn server `isc-dhcp-server <https://www.isc.org/downloads/dhcp/>`_ is running and will
provide an ip address from a DHCP pool. That ip address is then added to a local `bind9 <http://www.bind9.net/>`_
DNS zone.
The DNS servers are configured as caching DNS servers and will forward queries upstream, so they can be configured on
the client as the main DNS servers, or simply for the VPN zone domains.


Requirements
============

* python virtualenv


Configuration and Deployment
=============================

#. Set the following environment variables

   .. code-block:: bash

      export AWS_ACCESS_KEY_ID=MY_AWS_KEY
      export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

#. prepare a git repository for holding your secrets

   .. code-block:: bash

      mkdir deployment-secrets
      cd deployment-secrets
      echo "Railtrack" > .gitignore
      git init
      git add .gitignore
      git commit -m "ignore all Railtrack dir"
      mkdir key-pairs


#. Generate private and public keys for the different hosts:

   .. code-block:: bash

      openssl genrsa -out key-pairs/core01.priv 4096
      openssl rsa -pubout -in key-pairs/core01.priv -out key-pairs/core01.pub

      openssl genrsa -out key-pairs/core02.priv 4096
      openssl rsa -pubout -in key-pairs/core02.priv -out key-pairs/core02.pub

      openssl genrsa -out key-pairs/core03.priv 4096
      openssl rsa -pubout -in key-pairs/core03.priv -out key-pairs/core03.pub

      openssl genrsa -out key-pairs/git2consul.priv 4096
      openssl rsa -pubout -in key-pairs/git2consul.priv -out key-pairs/git2consul.pub

      ssh-keygen -f key-pairs/tinc-vpn.pem

#. commit your keys

   .. code-block:: bash

      git add key-pairs
      git commit -m "added tinc keys"

#. clone the Railtrack repo

   .. code-block:: bash

      git clone git@github.com:JeevesTakesOver/Railtrack.git
      cd Railtrack
      git checkout v1.0.1
      cd -

#. copy the config.yaml sample file

   .. code-block:: bash

      cp Railtrack/config/config.yaml config.yaml
      export CONFIG_YAML=$PWD/config.yaml

#. edit the config.yaml deployment file:

   * update any file paths so that they point to the newly created key-pair files
   * Add new public DNS names, IP addresses of the EC2 instances.
   * Add the public key contents to the different blocks.
   * Choose a Consul Encryption Key.

   .. code-block:: bash

      vim $CONFIG_YAML

#. commit your config.yaml

   .. code-block:: bash

      git add config.yaml
      git commit -m "added config.yaml"

#. Prepare a python virtualenv

   .. code-block:: bash

      cd Railtrack
      virtualenv venv
      . venv/bin/activate
      pip install -r requirements.txt


#. Edit the `main.tf <https://github.com/JeevesTakesOver/Railtrack/blob/feature/improve_docs/templates/main.tf.j2>`_ if needed.


#. To deploy, run the following:

   .. code-block:: bash

      fabric -f tasks/fabfile.py step_01_create_hosts
      fabric -f tasks/fabfile.py run_it
      fabric -f tasks/fabfile.py acceptance_tests


Laptop Configuration
=============================

To consume a DHCP IP address from the VPN, see the provision block for
the laptop, and the up_laptop task in the Makefile.
The laptop VM is an example for configuring a client to obtain an IP
address from the VPN which is automatically registered in DNS.


NIXOS
==============================

My local development laptop is `NixOS <https://nixos.org/>`_, there's is a local default.nix file to
help with consuming the python code in a more standard virtualenv way.

just run:
   .. code-block:: bash

      nix-shell



Jenkins Builds on NixOS using Mesos
=====================================

This is my Jenkins build job for RailTrack CI

   .. code-block:: bash

      #!/usr/bin/env bash

      source /etc/profile

      export HOME=/var/lib/mesos
      export PYTHONUNBUFFERED=no

      set -e	

      export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
      export AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYYYYYY

      export CONFIG_YAML=config/config.yaml

      nix-shell --run "fab -f tasks/fabfile.py jenkins_build"


License
========

Copyright (C) 2016  Jorge Costa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

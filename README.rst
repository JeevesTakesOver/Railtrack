.. image:: https://badge.waffle.io/Azulinho/Board.png?label=ready&title=Ready 
 :target: https://waffle.io/Azulinho/Board 
 :alt: 'Stories in Ready'


=========
Railtrack
=========

* A building block for a cloud based infrastructure.
* A distributed L2 switch across multiple cloud providers.
* A resilient, meshed VPN/Network layer.
* Self-serviceable.
* Access control provided by GitHub/GitLab/Bitbucket.
* Manages Pets
* Static or DHCP IP allocation of Pets on the VPN.
* Python based, built on Fabric


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

Each branch in the repository above represents a virtual network, with a
different addressing space.


Workflow
========

The expected workflow is that any team member can add new team members or
services to the virtual network by commiting the tinc public keys of the tinc
clients to the github repository and submit a pull request.
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


Requirements
============

* python virtualenv


Configuration and Deployment
=============================

#. Prepare a python virtualenv
   .. code-block:: bash

      virtualenv venv
      . venv/bin/activate
      pip install -r requirements.txt


On AWS:

#. Generate private and public keys for the different hosts:

   .. code-block:: bash

      openssl genrsa -out key_pairs/core01.priv 4096
      openssl rsa -pubout -in key_pairs/core01.priv -out key_pairs/core01.pub

      openssl genrsa -out key_pairs/core02.priv 4096
      openssl rsa -pubout -in key_pairs/core02.priv -out key_pairs/core02.pub

      openssl genrsa -out key_pairs/core03.priv 4096
      openssl rsa -pubout -in key_pairs/core03.priv -out key_pairs/core03.pub

      openssl genrsa -out key_pairs/git2consul.priv 4096
      openssl rsa -pubout -in key_pairs/git2consul.priv -out key_pairs/git2consul.pub

      ssh-keygen -f key_pairs/tinc-vpn.pem

#. Set the following environment variables

   .. code-block:: bash

      export AWS_ACCESS_KEY_ID=MY_AWS_KEY
      export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

#. Create the same EC2 Key-Pair in every region.
   In this example, it is named ``ci``.


#. Edit the ``main.tf`` if needed.


#. Edit the ``config/config.yaml`` file or set CONFIG_YAML to your config.yaml file:

   * Add new public DNS names, IP addresses of the EC2 instances.
   * Add the public key contents to the different blocks.
   * Choose a Consul Encryption Key.


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

My local development laptop is NIXOS, there's is a local default.nix file to
help with consuming the python code in a more standard virtualenv way.

just run:
   .. code-block:: bash

      nix-shell



Jenkins Builds on NixOS using Mesos
=====================================

This is my Jenkins build job for RailTrack CI

   .. code-block:: bash

      #!/usr/bin/env bash

      # Jenkins job parameters:
      # IMPORT_VMS
      # UPLOAD_VMS
      # RESET_CONSUL
      # BRANCH_TO_BUILD

      source /etc/profile

      export HOME=/var/lib/mesos
      export PYTHONUNBUFFERED=no

      rm -rf "/var/lib/mesos/VirtualBox VMs/laptop"

      set -e	


      export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
      export AWS_SECRET_ACCESS_KEY=YYYYYYYYYYYYYYYYY

      export CONFIG_YAML=config/config.yaml

      nix-shell --run "fab -f tasks/fabfile.py jenkins_build"


Future Work
===========

Provide a REST api service for management of the access key git repository.


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


.. image:: https://api.codacy.com/project/badge/Grade/5360e3ee056647b3931899b2079a4be7
   :alt: Codacy Badge
   :target: https://app.codacy.com/app/Azulinho/Railtrack?utm_source=github.com&utm_medium=referral&utm_content=JeevesTakesOver/Railtrack&utm_campaign=badger
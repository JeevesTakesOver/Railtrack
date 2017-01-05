=========
Railtrack
=========

* A building block for a cloud based infrastructure.
* A distributed L2 switch across multiple cloud providers.
* A resilient, meshed VPN/Network layer.
* Self-serviceable.
* Access control provided by GitHub/GitLab/Bitbucket.
* Manages Pets
* Python based, built on Fabric


The code in this repository provisions a fully meshed, geographically
distributed, resilient, encrypted virtual network.

Services can be added to the virtual network simply by binding the listening
ports of those services to the local virtual network ip addresses.

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

Usage cases
===========

* A new starter which upon joining his team, submits a pull request asking for access to the company services by providing his public key.

* Allow teams to be self-sufficient in adding/removing services to the virtual network.

* Full audits and history through git repository history.


Requirements
============

* python virtualenv
* vagrant and virtualbox (for testing locally)

Playing with Railtrack Locally/Testing using Vagrant
====================================================

To test locally using Vagrant and VirtualBox, install vagrant plugins and
set the following environment variables:

.. code-block:: bash

   vagrant plugin install vagrant-hostmanager
   vagrant plugin install hostupdater

   export AWS_ACCESS_KEY_ID=VAGRANT
   export AWS_SECRET_ACCESS_KEY=VAGRANT

   export KEY_PAIR_NAME=vagrant-tinc-vpn
   export KEY_FILENAME=$HOME/.vagrant.d/insecure_private_key

   export TINC_KEY_FILENAME_CORE_NETWORK_01=key-pairs/core01.priv
   export TINC_KEY_FILENAME_CORE_NETWORK_02=key-pairs/core02.priv
   export TINC_KEY_FILENAME_CORE_NETWORK_03=key-pairs/core03.priv
   export TINC_KEY_FILENAME_GIT2CONSUL=key-pairs/git2consul.priv
   export CONFIG_YAML=config/config.yaml

   make vagrant_test_cycle

This will create a set of virtual machines.

central vpn boxes:

* ``core01``
* ``core02``
* ``core03``

git2consul host:

* ``git2consul``

road warrior - laptop box:

* ``laptop``


After provisioning all hosts should be accessible from a private virtual
network.
Boxes ``core01``, ``core02``, ``core03``, and ``git2consul`` have fixed IP addresses.
``laptop`` will get a dynamic IP address on connecting to the network.

Run the following to login in to the laptop:

.. code-block:: bash

   vagrant ssh laptop
   ifconfig -a


Configuration and Deployment
=============================

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

      export KEY_PAIR_NAME=key_pairs/tinc-vpn
      export KEY_FILENAME=key_pairs/tinc-vpn.pem

      export TINC_KEY_FILENAME_CORE_NETWORK_01=key_pairs/core01.priv
      export TINC_KEY_FILENAME_CORE_NETWORK_02=key_pairs/core02.priv
      export TINC_KEY_FILENAME_CORE_NETWORK_03=key_pairs/core03.priv
      export TINC_KEY_FILENAME_GIT2CONSUL=key_pairs/git2consul.priv

#. Create the same EC2 Key-Pair in every region.
   In this example, it is named ``tinc-vpn``.

#. Create Security Groups across the different regions:

   .. code-block:: bash

      scripts/create-security-groups.sh

#. Create VMs on EC2:

   .. code-block:: bash

      make venv step_01

#. Edit the ``config/config.yaml`` file or set CONFIG_YAML to your config.yaml file:

   * Add new public DNS names, IP addresses of the EC2 instances.
   * Add the public key contents to the different blocks.
   * Choose a Consul Encryption Key.

#. To deploy, run the following:

   .. code-block:: bash

      make it


Laptop Configuration
=============================

To consume a DHCP IP address from the VPN, see the Vagrant provision block for
the laptop, and the up_laptop task in the Makefile.
The laptop vagrant VM is an example for configuring a client to obtain an IP
address from the VPN which is automatically registered in DNS.



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

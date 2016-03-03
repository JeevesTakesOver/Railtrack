============
Railtrack
============

* A building block for a cloud based infrastructure.

* A distributed L2 switch across multiple cloud providers.

* A resilient, meshed VPN/Network layer.

* Self-serviceable

* Access control provided by GitHub/GitLab/Bitbucket

* Manages Pets

* Python based, built on Fabric


Requirements
===============

* python virtualenv
* vagrant and virtualbox (for testing locally)
* docker (for creating the tincd keys)


Configuration and Deployment
=============================

On AWS:
 1. Set the following environment variables

    .. code-block:: bash

        export AWS_ACCESS_KEY_ID=MY_AWS_KEY
        export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

        export KEY_PAIR_NAME=tinc-vpn
        export KEY_FILENAME=tinc-vpn.pem

        export TINC_KEY_FILENAME_CORE_NETWORK_01=key-pairs/core01.priv
        export TINC_KEY_FILENAME_CORE_NETWORK_02=key-pairs/core02.priv
        export TINC_KEY_FILENAME_CORE_NETWORK_03=key-pairs/core03.priv
        export TINC_KEY_FILENAME_GIT2CONSUL=key-pairs/git2consul.priv

2. Create the same EC2 Key-Pair in every region:

   - named `tinc-vpn` in this example

3. Create Security Groups across the different regions:

   execute:
       scripts/create-security-groups.sh

4. Create VMs on EC2

   execute:
       make step_01

5. Generate Tinc KeyPairs for each VM

    execute locally, and save the resulting key into different files:
    .. code-block:: bash

        docker run -it ubuntu bash
        apt-get update
        apt-get install tinc
        tincd -K 4096

    save /etc/tinc/rsa_key.priv and /etc/tinc/rsa_key.pub, as :

    - key-pairs/core01.priv
    - key-pairs/core02.priv
    - key-pairs/core03.priv
    - key-pairs/git2consul.priv

    We will be adding the .pub keys to the config file

6. Edit the config/config.yaml file

    6.1 Add new public DNS names, IP addresses of the EC2 instances

    6.2 Add the public key contents to the different blocks

    6.3 Choose a Consul Encryption Key

7. Deploy:

    execute:
        make it

Playing with Railtrack locally/Testing
========================================

To test locally using Vagrant and VirtualBox, do:

 1. Set the following environment variables

    .. code-block:: bash

        export AWS_ACCESS_KEY_ID=MY_AWS_KEY
        export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

        export KEY_PAIR_NAME=vagrant-tinc-vpn
        export KEY_FILENAME=$HOME/.vagrant.d/insecure_private_key

        export TINC_KEY_FILENAME_CORE_NETWORK_01=key-pairs/core01.priv
        export TINC_KEY_FILENAME_CORE_NETWORK_02=key-pairs/core02.priv
        export TINC_KEY_FILENAME_CORE_NETWORK_03=key-pairs/core03.priv
        export TINC_KEY_FILENAME_GIT2CONSUL=key-pairs/git2consul.priv


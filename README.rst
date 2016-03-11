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

Requirements
============

* python virtualenv
* vagrant and virtualbox (for testing locally)
* docker (for creating the tincd keys)

Playing with Railtrack Locally/Testing using Vagrant
====================================================

To test locally using Vagrant and VirtualBox, install vagrant plugins and
set the following environment variables:

.. code-block:: bash

   vagrant plugin install vagrant-hostmanager
   vagrant plugin install hostupdater

   export AWS_ACCESS_KEY_ID=MY_AWS_KEY
   export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

   export KEY_PAIR_NAME=vagrant-tinc-vpn
   export KEY_FILENAME=$HOME/.vagrant.d/insecure_private_key

   export TINC_KEY_FILENAME_CORE_NETWORK_01=key-pairs/core01.priv
   export TINC_KEY_FILENAME_CORE_NETWORK_02=key-pairs/core02.priv
   export TINC_KEY_FILENAME_CORE_NETWORK_03=key-pairs/core03.priv
   export TINC_KEY_FILENAME_GIT2CONSUL=key-pairs/git2consul.priv

Then generate a Tinc KeyPair for your workstation by

executing these commands locally.Save the resulting keys into different files:

.. code-block:: bash

    apt-get update
    apt-get install tinc
    mkdir -p /etc/tinc/core-vpn/hosts
    echo 'core-vpn' > /etc/tinc/nets.boot

Add a conf file:

.. code-block:: bash

    vi /etc/tinc/core-vpn/tinc.conf


        Name=laptop
        Device=/dev/net/tun
        Mode=switch
        ConnectTo=core_network_02
        ConnectTo=core_network_03
        ConnectTo=core_network_01
        Cipher=aes-256-cbc


    vi /etc/tinc/core-vpn/core_network_01

       Name=core_network_01
       Address=192.168.56.101
       Port=655
       Compression=0
       Subnet=169.254.0.1/32

       -----BEGIN RSA PUBLIC KEY-----
       MIICCgKCAgEAozzeSS7NSQsb3s9vJS1rJAV3Z4c9ib422bAEOeK8oGcKjTKxFtaE
       9FNGT+wmvwqYz/I81YlB4MIcHojLx94PGXq8lef1awtiekpS23yeanwLFN0esPET
       Dsj51nWQ65QVcxN8cp6UODGlq8SYF8ikkkNiLyeDJabDKf8RQk5B1HhUHLbhyxJc
       FyqRiEXsBELCKVqBZEGTYeKqx8IatIfpIY0v9ddapsUQsELwSY3dLxI55sHDV5zk
       0wU3gpq1Ht6I030nxCPJ9gXXOTF6pwWUdYZyGXGnVbVRMPcxu4jfukuxf8jIWDwe
       2Iw+PRUPOl11/4sjULtqd71l8eh90I4FTAG20sHixatb4APYm7v4UXDrs57IU3PF
       NGOSYSQFDLPxRWpmtn/tY3IC5ILNXjvjWRdWIqrzz1ozzthvsqYMyqBZf8RQFN9j
       PKfK/oakrAhbBBZ4unKQD7Li3gfzUmDANy1mQXEkIjpfCLiq1C3lKkf1VnTPr9DJ
       315Acc8p6TIr+olFZVM7Fg6wCflrswJVYXy3wd9U+pfDK4d6/1va8K+2zQH9c2gE
       jy+PxPRYL0yn8EhPGc6z9Q7jFVuKOkgRDLDMmheLUAAYvhJj6d6MSDbWR5zShIds
       84wj88+90J2P+CrPbnhn7N78dfxTshR0wTAZQgUvJsqgDkRLovOTxmECAwEAAQ==
       -----END RSA PUBLIC KEY-----


    vi /etc/tinc/core-vpn/core_network_02

        Name=core_network_02
        Address=192.168.56.102
        Port=655
        Compression=0
        Subnet=169.254.0.2/32

        -----BEGIN RSA PUBLIC KEY-----
        MIICCgKCAgEA1pZWhTHR20c98RkwbHjvrVlDziK49c4nlaz1IxG3byLCKCVxNWt5
        YQFC+cPI+paMO3zWTWAF05b7yKfDLYfWXJU79EBL4kkYldAzTrUawMRYSJtItbrS
        LtEvfPBP0L82FgB/Jz7MyGU6tgnPOtMoDkO6fSLCbVKBraIAfs+uxYFjjjp7nRFA
        Atj/8iKDYOoF5Rpkd3jDpRnBUMU5jfJJiMnKK6v0cWWPmRCySdP4nkBseeibi3r3
        apuZMS59eGsBQRkJCpmGU3aQKPVYO79l+W+cWJyNspoEe7/i8uQT0fhQDInnycZu
        lrDlfY3/CkSyH0qkg9RDfE5DFfrLS4cuLdmu1ishWRLR3ANwxAExc5j7sgmveBnD
        Bj6aGG+xRirdrbyODMUxRewjkbSCZDjjIsWHPaGcK0WK+8Ri/o+xucsFnrCclEfd
        Xj7+uxdvq/8IMNGsUADhy4rjwdizNnsqPdfeJGIAgBi1of1tqpttEyLyzq0OQ27+
        jVkO7IXfq/EQR0c8hdU/D9DTD6mkVy71ScExKwcY9nUn40ssvu2cmkktuM0lq/JV
        WAxzMgL9PVcuHgd5IeusgW9qZk2wkqlKdYQIRhVgy1JFlqvMNYSqN28iIPuWWUuq
        oTzQuL7LdRO9TC6gS+JCrP03GAqpNS+q84BIXT/DJpi2+nJGkREbHd8CAwEAAQ==
        -----END RSA PUBLIC KEY-----


    vi /etc/tinc/core-vpn/core_network_03

        Name=core_network_03
        Address=192.168.56.103
        Port=655
        Compression=0
        Subnet=169.254.0.3/32

        -----BEGIN RSA PUBLIC KEY-----
        MIICCgKCAgEAlimDWppur7zym2LHca10GRipVSVTz4XSPE4bEEsjI3pGkUAt1s/9
        FlGJ3IiMtCOkbOsG3eaNK6zbYisl/n+j29EAe47U3ESzz2Mq2R4loJEJHLbuCknu
        edmUMtTT4dUIM4iJSAIQwqr7bTMID470xITkkK9yxG0LUtE0Wo73PW9Y6lm4nwKU
        9fQwCbkUAtXRR8k5z95v+l4P5G395qeG0MdZ4TlVWu+PzdMeV/uAl/tiWyGDWfkD
        6bZBsrb+89skR302ibEIf/WCWa0Gnrd5bC8SwAWI47VocF0pybWD9ImvhB4TkYHf
        mRp2k+cWxqi9IU/lCz1PTME9CaFteadYkE6mijcGPEC62QnF+jLE85vulwr9g0Lf
        yOKGgC0gqw0PgjShoQalcvD+9c+I76mEiX6NnNxIIJ5m/+Jgdn4dwh3rNc9R/R+k
        4Gs5dgf8u/1VAmXdkXpTjN/aJtwt7FOo1lkY5cYL8lIxV3xwOnYd6m3cL9dwCK97
        4mLTcJFjsRZSmTUXm9xCqZ/EYmSXviEodulvsnl8fO/1JjVxxNaV25LE71nSvF9F
        k3ud6ALnTFlKl+UrtWY199ODqK1S8lbTkso/ebLAN0zDdXXbD9KVpsSAUuNQRwop
        gpyzPAVIL9gQX373tY8y7al4cVg6hq2FHxJlAWtikFQA3dXRVH4Ix0sCAwEAAQ==
        -----END RSA PUBLIC KEY-----


    vi /etc/tinc/core-vpn/tinc-up

        #!/bin/sh
        avahi-autoipd -D $INTERFACE


    vi /etc/tinc/core-vpn/tinc-down

        #!/bin/sh
        ifconfig $INTERFACE down


Generate new keys

.. code-block:: bash

    tincd -K 4096


and deploy:

.. code-block:: bash

    make venv up it acceptance_tests


Configuration and Deployment
=============================

On AWS:

#. Set the following environment variables

   .. code-block:: bash

       export AWS_ACCESS_KEY_ID=MY_AWS_KEY
       export AWS_SECRET_ACCESS_KEY=MY_SECRET_KEY

       export KEY_PAIR_NAME=tinc-vpn
       export KEY_FILENAME=tinc-vpn.pem

       export TINC_KEY_FILENAME_CORE_NETWORK_01=key-pairs/core01.priv
       export TINC_KEY_FILENAME_CORE_NETWORK_02=key-pairs/core02.priv
       export TINC_KEY_FILENAME_CORE_NETWORK_03=key-pairs/core03.priv
       export TINC_KEY_FILENAME_GIT2CONSUL=key-pairs/git2consul.priv

#. Create the same EC2 Key-Pair in every region.
   In this example, it is named ``tinc-vpn``.

#. Create Security Groups across the different regions:

   .. code-block:: bash

      scripts/create-security-groups.sh

#. Create VMs on EC2:

   .. code-block:: bash

      make venv step_01

#. Generate Tinc KeyPairs for each VM.

   * Run the following locally:

     .. code-block:: bash

        docker run -it ubuntu bash
        apt-get update
        apt-get install tinc
        tincd -K 4096

   * Now save the resulting key into different files. Save ``/etc/tinc/rsa_key.priv`` and ``/etc/tinc/rsa_key.pub``, as:

     - key-pairs/core01.priv
     - key-pairs/core02.priv
     - key-pairs/core03.priv
     - key-pairs/git2consul.priv

     We will be adding the ``.pub`` keys to the config file.

#. Edit the ``config/config.yaml`` file:

   * Add new public DNS names, IP addresses of the EC2 instances.
   * Add the public key contents to the different blocks.
   * Choose a Consul Encryption Key.

#. To deploy, run the following:

   .. code-block:: bash

      make it

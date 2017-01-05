# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true
  config.hostmanager.include_offline = true

  config.vm.define "core01" do |core01|
    # https://github.com/chef/bento/issues/577#issuecomment-215133141
    core01.vm.box = "gbarbieru/xenial"
    core01.vm.hostname = 'core01'
    core01.vm.network :private_network, ip: "192.168.56.101"
    core01.ssh.insert_key = false

    core01.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core01"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]


    end

    core01.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh
      grep -q "swapfile" /etc/fstab
      if [ $? -ne 0 ]; then
        echo 'swapfile not found. Adding swapfile.'
        fallocate -l 1024M /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap defaults 0 0' >> /etc/fstab
      else
        echo 'swapfile found. No changes made.'
      fi
    SHELL
  end

  config.vm.define "core02" do |core02|
    # https://github.com/chef/bento/issues/577#issuecomment-215133141
    core02.vm.box = "gbarbieru/xenial"
    core02.vm.hostname = 'core02'

    core02.vm.network :private_network, ip: "192.168.56.102"
    core02.ssh.insert_key = false

    core02.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core02"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
    end
    core02.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh
      grep -q "swapfile" /etc/fstab
      if [ $? -ne 0 ]; then
        echo 'swapfile not found. Adding swapfile.'
        fallocate -l 1024M /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap defaults 0 0' >> /etc/fstab
      else
        echo 'swapfile found. No changes made.'
      fi
    SHELL
  end

  config.vm.define "core03" do |core03|
    # https://github.com/chef/bento/issues/577#issuecomment-215133141
    core03.vm.box = "gbarbieru/xenial"
    core03.vm.hostname = 'core03'

    core03.vm.network :private_network, ip: "192.168.56.103"
    core03.ssh.insert_key = false

    core03.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core03"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
    end
    core03.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh
      grep -q "swapfile" /etc/fstab
      if [ $? -ne 0 ]; then
        echo 'swapfile not found. Adding swapfile.'
        fallocate -l 1024M /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap defaults 0 0' >> /etc/fstab
      else
        echo 'swapfile found. No changes made.'
      fi
    SHELL
  end

  config.vm.define "git2consul" do |git2consul|
    # https://github.com/chef/bento/issues/577#issuecomment-215133141
    git2consul.vm.box = "gbarbieru/xenial"
    git2consul.vm.hostname = 'git2consul'

    git2consul.vm.network :private_network, ip: "192.168.56.110"
    git2consul.ssh.insert_key = false

    git2consul.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "git2consul"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
    end
    git2consul.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh
      grep -q "swapfile" /etc/fstab
      if [ $? -ne 0 ]; then
        echo 'swapfile not found. Adding swapfile.'
        fallocate -l 1024M /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap defaults 0 0' >> /etc/fstab
      else
        echo 'swapfile found. No changes made.'
      fi
    SHELL
  end

  config.vm.define "laptop" do |laptop|
    # https://github.com/chef/bento/issues/577#issuecomment-215133141
    laptop.vm.box = "gbarbieru/xenial"
    laptop.vm.hostname = 'laptop'

    laptop.vm.network :private_network, ip: "192.168.56.200"
    laptop.ssh.insert_key = false

    laptop.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "laptop"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
    end

    laptop.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh
      grep -q "swapfile" /etc/fstab
      if [ $? -ne 0 ]; then
        echo 'swapfile not found. Adding swapfile.'
        fallocate -l 1024M /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap defaults 0 0' >> /etc/fstab
      else
        echo 'swapfile found. No changes made.'
      fi
      sleep 500 # wait for first apt-get update to finish
      export DEBIAN_FRONTEND=noninteractive
      sudo apt-get update
      sudo apt-get install -y tinc rsync avahi-autoipd dnsutils
      sudo rsync -a /vagrant/laptop/ /
      sudo apt-get -y remove resolvconf dnsmasq
    SHELL
  end

end

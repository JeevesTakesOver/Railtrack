# -*- mode: ruby -*-
# vi: set ft=ruby :

# https://github.com/chef/bento/issues/577#issuecomment-215133141
UPSTREAM_VM_BOX = 'gbarbieru/xenial'

Vagrant.configure("2") do |config|

  config.hostmanager.enabled = true
  config.hostmanager.manage_host = false
  config.hostmanager.manage_guest = true
  config.hostmanager.include_offline = true

  config.vm.define "core01" do |core01|
    # consume a local Vagrant image if available
    if ENV.has_key?('CORE01_VM_BOX_URL')
        core01.vm.box = "RAILTRACK_CORE01_VM"
    else
        core01.vm.box = UPSTREAM_VM_BOX
    end
    core01.vm.hostname = 'core01'
    core01.vm.network :private_network, ip: "192.168.56.101"
    core01.ssh.insert_key = false

    core01.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core01"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://www.virtualbox.org/manual/ch05.html#iocaching
      # disable hostio-cache to save memory
      v.customize [
        "storagectl", :id, 
        "--name", "SATA",
        "--hostiocache", "off"
      ]
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

      # wait for apt-get actions to finished
      ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      while [ $? == 0 ]
      do
        echo "apt-... running"
        sleep 1
        ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      done

    SHELL
  end

  config.vm.define "core02" do |core02|
    # consume a local Vagrant image if available
    if ENV.has_key?('CORE02_VM_BOX_URL')
        core02.vm.box = "RAILTRACK_CORE02_VM"
    else
        core02.vm.box = UPSTREAM_VM_BOX
    end
    core02.vm.hostname = 'core02'

    core02.vm.network :private_network, ip: "192.168.56.102"
    core02.ssh.insert_key = false

    core02.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core02"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://www.virtualbox.org/manual/ch05.html#iocaching
      # disable hostio-cache to save memory
      v.customize [
        "storagectl", :id, 
        "--name", "SATA",
        "--hostiocache", "off"
      ]
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

      # wait for apt-get actions to finished
      ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      while [ $? == 0 ]
      do
        sleep 1
        ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      done
    SHELL
  end

  config.vm.define "core03" do |core03|
    # consume a local Vagrant image if available
    if ENV.has_key?('CORE03_VM_BOX_URL')
        core03.vm.box = "RAILTRACK_CORE03_VM"
    else
        core03.vm.box = UPSTREAM_VM_BOX
    end
    core03.vm.hostname = 'core03'

    core03.vm.network :private_network, ip: "192.168.56.103"
    core03.ssh.insert_key = false

    core03.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "core03"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://www.virtualbox.org/manual/ch05.html#iocaching
      # disable hostio-cache to save memory
      v.customize [
        "storagectl", :id, 
        "--name", "SATA",
        "--hostiocache", "off"
      ]
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

      # wait for apt-get actions to finished
      ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      while [ $? == 0 ]
      do
        sleep 1
        ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      done
    SHELL
  end

  config.vm.define "git2consul" do |git2consul|
    # consume a local Vagrant image if available
    if ENV.has_key?('GIT2CONSUL_VM_BOX_URL')
        git2consul.vm.box = "RAILTRACK_GIT2CONSUL_VM"
    else
        git2consul.vm.box = UPSTREAM_VM_BOX
    end
    git2consul.vm.hostname = 'git2consul'

    git2consul.vm.network :private_network, ip: "192.168.56.110"
    git2consul.ssh.insert_key = false

    git2consul.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "git2consul"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://www.virtualbox.org/manual/ch05.html#iocaching
      # disable hostio-cache to save memory
      v.customize [
        "storagectl", :id, 
        "--name", "SATA",
        "--hostiocache", "off"
      ]
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

      # wait for apt-get actions to finished
      ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      while [ $? == 0 ]
      do
        sleep 1
        ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      done
    SHELL
  end

  config.vm.define "laptop" do |laptop|
    # consume a local Vagrant image if available
    if ENV.has_key?('LAPTOP_VM_BOX_URL')
        laptop.vm.box = "RAILTRACK_LAPTOP_VM"
    else
        laptop.vm.box = UPSTREAM_VM_BOX
    end
    laptop.vm.hostname = 'laptop'

    laptop.vm.network :private_network, ip: "192.168.56.200"
    laptop.ssh.insert_key = false

    laptop.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 256]
      v.customize ["modifyvm", :id, "--name", "laptop"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://www.virtualbox.org/manual/ch05.html#iocaching
      # disable hostio-cache to save memory
      v.customize [
        "storagectl", :id, 
        "--name", "SATA",
        "--hostiocache", "off"
      ]
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

      # wait for apt-get actions to finished
      ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      while [ $? == 0 ]
      do
        sleep 1
        ps -ef | grep -v grep | grep apt >/dev/null 2>&1
      done

      sudo apt-get update
      sudo apt-get install -y tinc rsync dnsutils
      sudo rsync -a /vagrant/laptop/ /
      # use additional flags, as ubuntu adds resolvconf and dnsmasq to
      # 'essential' pkgs.
      sudo DEBIAN_FRONTEND=noninteractive apt-get -y --allow-remove-essential remove resolvconf dnsmasq
    SHELL
  end
end

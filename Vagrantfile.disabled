# -*- mode: ruby -*-
# vi: set ft=ruby :

UPSTREAM_VM_BOX = 'bento/ubuntu-16.04'

Vagrant.configure("2") do |config|

  config.hostmanager.enabled = true
  config.hostmanager.manage_host = false
  config.hostmanager.manage_guest = true
  config.hostmanager.include_offline = true

  config.vm.define "core01" do |core01|
    core01.vm.box = UPSTREAM_VM_BOX
    core01.vm.hostname = 'core01'
    core01.vm.network :private_network, ip: "192.168.56.11"
    core01.ssh.insert_key = false

    core01.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--memory", 1024]
      v.customize ["modifyvm", :id, "--name", "core01"]
      v.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      # https://forums.virtualbox.org/viewtopic.php?f=20&t=45245
      v.customize [
        "storagectl", :id, 
        "--name", "SATA Controller",
        "--hostiocache", "off"
      ]
    end
  end

  config.vm.define "core02" do |core02|
    core02.vm.box = UPSTREAM_VM_BOX
    core02.vm.hostname = 'core02'

    core02.vm.network :private_network, ip: "192.168.56.12"
    core02.ssh.insert_key = false

    core02.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--memory", 1024]
      v.customize ["modifyvm", :id, "--name", "core02"]
      v.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
      # https://forums.virtualbox.org/viewtopic.php?f=20&t=45245
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      v.customize [
        "storagectl", :id, 
        "--name", "SATA Controller",
        "--hostiocache", "off"
      ]
    end
  end

  config.vm.define "core03" do |core03|
    core03.vm.box = UPSTREAM_VM_BOX
    core03.vm.hostname = 'core03'

    core03.vm.network :private_network, ip: "192.168.56.13"
    core03.ssh.insert_key = false

    core03.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--memory", 1024]
      v.customize ["modifyvm", :id, "--name", "core03"]
      v.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
      # https://forums.virtualbox.org/viewtopic.php?f=20&t=45245
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      v.customize [
        "storagectl", :id, 
        "--name", "SATA Controller",
        "--hostiocache", "off"
      ]
    end
  end

  config.vm.define "git2consul" do |git2consul|
    git2consul.vm.box = UPSTREAM_VM_BOX
    git2consul.vm.hostname = 'git2consul'

    git2consul.vm.network :private_network, ip: "192.168.56.110"
    git2consul.ssh.insert_key = false

    git2consul.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
      v.customize ["modifyvm", :id, "--memory", 768]
      v.customize ["modifyvm", :id, "--name", "git2consul"]
      v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
      # https://forums.virtualbox.org/viewtopic.php?f=20&t=45245
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      v.customize [
        "storagectl", :id, 
        "--name", "SATA Controller",
        "--hostiocache", "off"
      ]
    end
  end

  config.vm.define "laptop" do |laptop|
    laptop.vm.box = UPSTREAM_VM_BOX
    laptop.vm.hostname = 'laptop'

    laptop.vm.network :private_network, ip: "192.168.56.200"
    laptop.ssh.insert_key = false

    laptop.vm.provider :virtualbox do |v|
      v.linked_clone = true
      v.customize ["modifyvm", :id, "--memory", 512]
      v.customize ["modifyvm", :id, "--name", "laptop"]
      v.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
      # https://forums.virtualbox.org/viewtopic.php?f=20&t=45245
      Vagrant::Util::Platform.linux? and v.customize ["modifyvm", :id, "--paravirtprovider", "kvm"]
      v.customize [
        "storagectl", :id, 
        "--name", "SATA Controller",
        "--hostiocache", "off"
      ]
    end

    laptop.vm.provision "shell", inline: <<-SHELL
      #!/bin/sh

      sudo apt-get update
      sudo apt-get install -y tinc rsync dnsutils
      sudo rsync -a /vagrant/laptop/ /
      # use additional flags, as ubuntu adds resolvconf and dnsmasq to
      # 'essential' pkgs.
      sudo DEBIAN_FRONTEND=noninteractive apt-get -y --allow-remove-essential remove resolvconf dnsmasq
    SHELL
  end
end

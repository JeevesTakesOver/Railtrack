# vim: ai ts=4 sts=4 et sw=4 ft=python fdm=indent et foldlevel=0

""" Collection of helpers for fabric tasks

Contains a collection of helper functions for fabric task used in this
fabfile.
List them a-z if you must.
"""


import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import os
import sys
import yaml
import re

from fabric.api import sudo, env
from fabric.context_managers import settings, hide

from bookshelf.api_v1 import (
    log_yellow,
    reboot,
    apt_install
)


def ubuntu14_required_packages():
    return ["apt-transport-https",
            "software-properties-common",
            "build-essential",
            "python-virtualenv",
            "desktop-file-utils",
            "git",
            "python-dev",
            "python-tox",
            "python-virtualenv",
            "libffi-dev",
            "libssl-dev",
            "wget",
            "curl",
            "openjdk-7-jre-headless",
            "libffi-dev",
            "ntp",
            "libncurses5-dev",
            "libexpat1-dev",
            "libreadline-dev",
            "libcurl4-openssl-dev",
            "zlib1g-dev",
            "libwww-curl-perl",
            "libssl-dev",
            "libsvn-perl",
            "liblzo2-dev",
            "ruby-dev"]


def upgrade_kernel_and_grub(do_reboot=False, log=True):
    """ updates the kernel and the grub config """

    print(env.host_string)
    if log:
        log_yellow('upgrading kernel')

    with settings(hide('running', 'stdout')):
        sudo('unset UCF_FORCE_CONFFOLD; '
             'export UCF_FORCE_CONFFNEW=YES; '
             'ucf --purge /boot/grub/menu.lst; '
             'export DEBIAN_FRONTEND=noninteractive ; '
             'apt-get update; '
             'apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy '
             'dist-upgrade')
        with settings(warn_only=True):
            if do_reboot:
                if log:
                    log_yellow('rebooting host')
                reboot()


def parse_config(filename):
    """ parses the YAML config file and expands any environment variables """

    pattern = re.compile(r'^\<%= ENV\[\'(.*)\'\] %\>(.*)$')
    yaml.add_implicit_resolver("!pathex", pattern)

    def pathex_constructor(loader, node):
        value = loader.construct_scalar(node)
        envVar, remainingPath = pattern.match(value).groups()
        return os.environ[envVar] + remainingPath

    yaml.add_constructor('!pathex', pathex_constructor)

    with open(filename) as f:
        return(
            yaml.load(f)
        )


def install_tinc():
    """ installs tinc """
    apt_install(packages=['tinc'])

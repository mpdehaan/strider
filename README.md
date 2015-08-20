STRIDER!!!
==========

Strider is a minimal program that both helps *test* development environments and *bakes* cloud images.  

You may think of it as Vagrant+Packer in one, reading from one config file.

Strider is brought to you by the guy who wrote Cobbler and Ansible (Michael DeHaan), and is named after Robert Plant's dog.

Installation
============

    pip install strider

Usage
=====

    # configure your setup and check this into your repo root
    vim striderfile.py

    # spin up new VMs and configure them
    python striderfile.py --up

    # make some changes and apply them without booting a new instance
    python striderfile.py --provision

    # log into a VM
    python striderfile.py --ssh

    # bake a cloud image and show the ID
    python striderfile.py --bake [--auto-teardown]

    # tear down the instances
    python striderfile.py --destroy

TODO List
=========

    * minor code cleanup
    * also support reading credentials from a Boto profile
    * MOAR PLUGINS
    * --bake-results to output AMI build info to a JSON file in addition to stdout logging
    * AMI tagging (different tag list than instance)

Got Plugins?
============

Strider is being developed for Ansible and AWS first, but other Virt plugins and Provisioners are SUPER welcome as long as the underlying tool doesn't suck and the code is clean.  For instance, Google Compute Engine, Virtual Box, Puppet, Chef, etc, are all fair game. We're almost ready, but not quite.  Pending a little refactoring first.  I'll let you know.

Again, you will note that unlike Vagrant with Vagrantfiles, there is no binary named strider and no magic filenames. Your code is the entry point and can be named anything.  

License
=======

Apache 2.  Program (C) Michael DeHaan, 2015

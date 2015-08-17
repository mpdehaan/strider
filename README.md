STRIDER!!!
==========

Strider is a minimal development tool for testing code against virtual machines.  

Basically it's a Python program that consumes something that looks a lot like a Vagrantfile.

When run, it spins up VMs if they don't already exist, and can configure them ad nauseum, and also destroy them.

Strider is brought to you by the guy who wrote Cobbler and Ansible (Michael DeHaan), and is named after Robert Plant's dog.

Why?
====

Originally I wanted a LOCAL (non-SSH-ing) rsync+ansible Vagrant-like workflow tool that was easy to tweak and this was an easy thing to do to get it without modifying Vagrant.  I also figured I'd want to do more with AWS over time and grow things in different directions.  Once I got going, I decided there wasn't much to it, so I kept going.  

The result is a provisioner that works a bit more like Packer does, and runs a little faster, and a codebase that is a little
easier to tweak (for me, being a Python fan).

Right now it works better for me, at least, for the AWS + Ansible use case than the stock Vagrant ansible provisioner.
It may also fit your needs.

Major Vagrant differences
=========================

The application is written in Python.

There is no binary. Running the "striderfile" replaces running commands like "vagrant up".

A failure will not remove your VMs.  Take care to watch the AWS console if you don't want to leave a failed deploy running.

There are many SIGNIFICANTLY less provisioners and virtualization targets at this point.  

Status
======

Alpha. Functional for AWS + Ansible together, but may have some small bugs here and there.  TODOs:

    * IMMEDIATELY NEXT: Need to add the trivial "strider --ssh" command too for quickly firing up a shell, since we know how
    * Minor code cleanup
    * AWS code may have some small buglets.  But I don't know of any at the moment.  Let me know!
    * Support standard EC2 credential profile files to allow shorter/easier entry
    * Improve Error Handling
    * MOAR PLUGINS

Got Plugins?
============

Strider is being developed for Ansible and AWS first, but other Virt plugins and Provisioners are SUPER welcome as long as the underlying tool doesn't suck and the code is clean.  For instance, Google Compute Engine, Virtual Box, Puppet, Chef, etc, are all fair game. We're almost ready, but not quite.  Pending a little refactoring first.  I'll let you know.

Installation
============

    pip install strider

Usage
=====

    vim striderfile.py # refer to the example in this project
    python striderfile.py [--up|--provision|--destroy]
    # or just use the API in strider/__init__.py
    echo "STRIDER!!!"

Again, you will note that unlike Vagrant with Vagrantfiles, there is no binary named strider and no magic filenames. Your code is the entry point and can be named anything.  

License
=======

Apache 2.  Program (C) Michael DeHaan, 2015

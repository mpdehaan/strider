STRIDER
=======

Strider is a minimal development tool for testing code against virtual machines.  

Basically it's a Python program that consumes something that looks a lot like a Vagrantfile.

I'm not building this for people to use it, but rather to try some things out.  

The end goal is more to provide a playground environment to do more things with AWS, as yet to be determined.  
Right now it doesn't do a lot that you couldn't do with awscli + ssh + rsync, but if you're just looking for
a Ansible + AWS Vagrant-alike thing, it does most of that already.

STATUS
======

EARLY

TODO:

    * Toy implementation, not finished.  Unless you're a developer interested in this, you probably shouldn't use it.
    * Minor code cleanup
    * Finish CLI
    * AWS code may (?) have eventual consistency errors or instance state related buglets.
    * Ansible provisioner is very literal, should just be a shell provisioner
    * Support standard EC2 credential profile files to allow shorter/easier entry
    * Need to add the trivial "strider ssh" command too for quickly firing up a shell.

GOT PLUGINS?
============

Strider is being developed for Ansible and AWS first, but other Virt plugins and Provisioners are SUPER welcome as long as the underlying
tool doesn't suck and the code is clean.  For instance, Google Compute Engine, Virtual Box, Puppet, Chef, etc, are all fair game.
We're almost ready, but not quite.

USAGE
=====

pip install boto
then take a look at example.py
run it

Community
=========

It's way early yet, but see CONTRIBUTING.md.

CLI Gameplan
============

Assuming the Strider config in 'demo.py'

    python examples/demo.py --up
    python examples/demo.py --provision 
    python examples/demo.py --list
    python examples/demo.py --destroy

This isn't quite there yet but is trivial to add.

License
=======

Apache 2.  Program (C) Michael DeHaan, 2015

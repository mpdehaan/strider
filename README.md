STRIDER
=======

Strider is a minimal development tool for testing code against virtual machines.  

Basically it's a Python program that consumes something that looks a lot like a Vagrantfile.

Strider is brought to you by the guy who wrote Cobbler and Ansible (Michael DeHaan), and is named after Robert Plant's dog.

STATUS
======

Alpha. Functional for AWS + Ansible together, but may have some small bugs here and there.

TODO:

    * Minor code cleanup
    * AWS code may (?) have eventual consistency errors or instance state related buglets.
    * Support standard EC2 credential profile files to allow shorter/easier entry
    * Need to add the trivial "strider ssh" command too for quickly firing up a shell, since we know how
    * Improve Error Handling
    * MOAR PLUGINS

GOT PLUGINS?
============

Strider is being developed for Ansible and AWS first, but other Virt plugins and Provisioners are SUPER welcome as long as the underlying
tool doesn't suck and the code is clean.  For instance, Google Compute Engine, Virtual Box, Puppet, Chef, etc, are all fair game.
We're almost ready, but not quite.  Pending a little refactoring first.  I'll let you know.

USAGE
=====

    pip install strider
    vim striderfile.py # refer to the example in this project
    python striderfile.py [--up|--provision|--destroy]
    # or just use the API in strider/__init__.py
    echo "STRIDER!!!"

You will note that unlike Vagrant with Vagrantfiles, there is no binary named strider and no magic filenames.  
Your code is the entry point and can be named anything.  

WHY
===

Originally I wanted a rsync+ansible Vagrant workflow tool that was easy to tweak and this was an easy thing to do to get it.
I also figured I'd want to do more with AWS over time and grow things in different directions.

Plus, it was a bit of a tech demo about how easy it was to do.  There's not much code anywhere.

License
=======

Apache 2.  Program (C) Michael DeHaan, 2015

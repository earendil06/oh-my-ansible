#!/usr/bin/env bash

git clone --depth=1 --no-tags https://github.com/ansible/ansible.git ansible-repo
ln -s ./ansible-repo/lib/ansible ./ansible
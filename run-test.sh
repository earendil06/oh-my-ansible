#!/usr/bin/env bash

export ANSIBLE_LIBRARY="$PWD/modules"
ansible-playbook testmod.yml
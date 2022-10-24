#!/bin/sh
while [[ $# -gt 0 ]]; do case $1 in


  --test|-t)
    poetry run pytest --cov=path_dict test.py --cov-report term-missing
    rm ./.coverage
    shift ;;


  --profiler|-p)
    poetry run python profiler.py
    rm ./profiling.prof
    shift ;;


  *|-*|--*)
    echo "Unknown option $1"
    echo "Usage: [ -t | --test ]"
    exit 2
    exit 1 ;;


esac; done

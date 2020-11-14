#!/bin/sh
export DOTNET_ROOT=$HOME/.dotnet
export PATH=$PATH:$HOME/.dotnet

./00-crawl.sh
./01-filter-and-convert.sh "$DICTS"
./02-merge.sh
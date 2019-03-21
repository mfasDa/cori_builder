#! /bin/bash
#
# Build script wrapper, running inside shiferimage
# Expecting to find alidist inside $packagerepo/$installation
# Packages will be installed to $packagerepo/sw

packagerepo=$1
installation=$2
defaults=$3
packagename=$4

source /opt/rh/devtoolset-7/enable
cd $packagerepo/$installation
cmd=$(printf "aliBuild -d -z -w ../sw --defaults %s build %s" $defaults $packagename)
eval $cmd

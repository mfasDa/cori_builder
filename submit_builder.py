#! /usr/bin/env python
from datetime import datetime
import argparse
import os
import subprocess
import sys

scriptrepo = os.path.abspath(os.path.dirname(sys.argv[0]))
nersc_host = os.environ["NERSC_HOST"]

def create_buildscript(buildsciptname, packagerepo, installation, defaults, packagename, maxhours, qos):
    buildscriptdir = os.path.abspath(os.path.dirname(buildsciptname))
    if not os.path.exists(buildscriptdir):
        os.makedirs(buildscriptdir, 0755)
    if os.path.exists(buildsciptname):
        os.remove(buildsciptname)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    logfile = "%s/logs/%s_%s.log" %(packagerepo, packagename, timestamp)
    logdir = os.path.abspath(os.path.dirname(logfile))
    if not os.path.exists(logdir):
        os.makedirs(logdir, 0755)
    with open(buildsciptname, "w") as myscript:
        myscript.write("#! /bin/bash\n")
        #myscript.write("#SBATCH --qos premium\n")
        myscript.write("#SBATCH --qos=%s\n" %qos)
        if "cori" in nersc_host:
            myscript.write("#SBATCH --constraint=haswell\n")
        myscript.write("#SBATCH --nodes=1\n")
        #myscript.write("#SBATCH --time=%d:00:00\n" %maxhours)
        myscript.write("#SBATCH --time=30:00\n")
        myscript.write("#SBATCH --image=docker:mfasel/cc7-alice:latest\n")
        myscript.write("#SBATCH --output=%s\n" %logfile)
        myscript.write("#SBATCH --license=cscratch1,project\n") 
        #myscript.write("#SBATCH --volume=\"/project/projectdirs/alice/software:/project/projectdirs/alice/software\"\n")
        #myscript.write("#SBATCH --volume=\"%s:%s\"\n" %(os.environ["CSCRATCH"], os.environ["CSCRATCH"]))
        myscript.write("shifter %s/runBuild.sh %s %s %s %s\n" %(scriptrepo, packagerepo, installation, defaults, packagename))
        myscript.write("rm %s\n" %buildsciptname)
        myscript.write("echo Done ...\n")

def submitBuildJob(packagerepo, installation, defaults, packagename, maxhours, qos):
    buildsciptname = os.path.join(packagerepo, "buildscripts", "build%s_%s_%s_%s.sh" %(nersc_host, installation, packagename, defaults))
    create_buildscript(buildsciptname, packagerepo, installation, defaults, packagename, maxhours, qos)
    subprocess.call(["sbatch", buildsciptname])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="submit_builder", description="Tool submitting ALICE build task on Cori/Edison")
    parser.add_argument("repo", metavar="REPO", help="Path to the installation repository")
    parser.add_argument("installation", metavar="INSTALLATION", help="Path to the directory containing alidist and development packages")
    parser.add_argument("packagename", metavar="PACKAGENAME", help="Name of the package to be built")
    parser.add_argument("-d", "--defaults", type=str, default="root6", help="Build defaults")
    parser.add_argument("-t", "--maxtime", type=int, default=5, help="Max. allowed time for build (hours)")
    parser.add_argument("-q", "--qos", type=str, default="premium", help="Queue used for build task")
    args = parser.parse_args()
    submitBuildJob(args.repo, args.installation, args.defaults, args.packagename, args.maxtime, args.qos)

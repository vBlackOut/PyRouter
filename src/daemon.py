import os
import sys
from daemonize import Daemonize
from netfilterqueue import NetfilterQueue
import socket
import signal
import psutil
import subprocess
import time


def get_pid(name):
    for proc in psutil.process_iter():
        # Get the process info using PID
        process = psutil.Process(
            proc.pid).cmdline()
        process_id = psutil.Process(
            proc.pid)
        pname = " ".join(process)
        if name in pname:
            return "{0}".format(
                process_id.pid)


def is_running(pid):
    if os.path.isdir(
            '/proc/{}'.format(pid)):
        return True
    return False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_and_accept(pkt):
    print(pkt)
    pkt.accept()


def main():
    nfqueue = NetfilterQueue()
    nfqueue.bind(1, print_and_accept)
    s = socket.fromfd(
        nfqueue.get_fd(),
        socket.AF_UNIX,
        socket.SOCK_STREAM)
    try:
        nfqueue.run_socket(s)
    except:
        print('')
    s.close()
    nfqueue.unbind()

if __name__ == '__main__':
    if sys.argv[1] == "start":
        subprocess.Popen(
            ["iptables",
                "-I",
                "INPUT",
                "-d",
                "10.60.0.0/24",
                "-j",
                "NFQUEUE",
                "--queue-num",
                "1"])

        CubyRouter = os.path.basename(
            sys.argv[0])
        # any name
        pidfile = '/tmp/%s' % CubyRouter
        daemon = Daemonize(
            app=CubyRouter,
            pid=pidfile,
            action=main)
        # daemon.start()
        try:
            pid = open(pidfile, "r")
            pid = pid.readline()
        except:
            pid = "0"
        if is_running(pid) == True:
            print(
                "Service CubyRouter\t\tstart\t[" +
                bcolors.HEADER +
                bcolors.FAIL +
                "!!" +
                bcolors.ENDC +
                "]")
            print(
                "Process {} exist".format(pid))
        else:
            print(
                "Service CubyRouter \t\tstart\t[" +
                bcolors.HEADER +
                bcolors.OKGREEN +
                "ok" +
                bcolors.ENDC +
                "]")
            daemon.start()

    if sys.argv[1] == "stop":
        try:
            if sys.argv[2] == "forced":
                forced = True
            elif sys.argv[2] == "forced-on":
                forced = False
        except:
            forced = True

        if forced == False:
            subprocess.Popen(
                ["iptables",
                    "-D",
                    "INPUT",
                    "-d",
                    "10.60.0.0/24",
                    "-j",
                    "NFQUEUE",
                    "--queue-num",
                    "1"])

        CubyRouter = os.path.basename(
            sys.argv[0])
        pidfile = '/tmp/%s' % CubyRouter  # any name
        pid = get_pid("daemon.py start")
        pid = int(pid or 0)
        os.kill(pid, signal.SIGTERM)
        try:
            if forced:
                subprocess.Popen(
                    ["python3",
                        "daemon.py",
                        "stop",
                        "forced-on"],
                    stdout=subprocess.PIPE)
                print(
                "Service CubyRouter \t\tstop\t[" +
                bcolors.HEADER +
                bcolors.OKGREEN +
                "ok" +
                bcolors.ENDC +
                "]")
        except:
            print(
                "Service CubyRouter \t\tstop\t[" +
                bcolors.HEADER +
                bcolors.FAIL +
                "!!" +
                bcolors.ENDC +
                "]")

    if sys.argv[1] == "restart":
        subprocess.Popen(
            ["python3", 
            "daemon.py", 
            "stop"], 
            stdout=subprocess.PIPE)
        time.sleep(1)
        subprocess.Popen(["python3",
                          "daemon.py",
                          "start"],
                         stdout=subprocess.PIPE)

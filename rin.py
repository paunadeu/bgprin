import os.path
import sys
from itertools import count

import psutil
import inquirer

from configparser import ConfigParser
from bgpdumpy import BGPDump, TableDumpV2

configPath = 'config.ini'
exaConfigPath = 'exabgp.conf'

def WriteRINConf(IP, BGP, MRT):
    Config = ConfigParser()
    Config['rin'] = {}

    # Check for empty values
    Config['rin'].update(IP)
    Config['rin'].update(BGP)
    Config['rin'].update(MRT)

    with open(configPath, 'w') as configfile:
        Config.write(configfile)


def WriteExaConf(IP, BGP):
    Exaconf = "neighbor {} {{\n\
    router-id {};\n\
    local-address {};\n\
    local-as {};\n\
    peer-as {};\n\
}}".format(IP['Remote-IPv4'], IP['Local-IPv4'], IP['Local-IPv4'], BGP['Local-AS'], BGP['Remote-AS'])

    with open(exaConfigPath, 'w') as configfile:
        configfile.write(Exaconf)

def read():
    Config = ConfigParser()
    Config.read(configPath)
    return Config


def getCurrentParam(param):
    Config = read()
    return '' if param not in Config['rin'] else Config['rin'][param]


def configure(section):
    print("Running in configure mode")
    if section == 'main':
        # Check if fileconfig and dir exists, if not create
        if not os.path.exists(configPath):
            print(configPath + " don't exists, creating it with default values.")
            IP = {
                'Interface': psutil.net_if_addrs().keys[0],
                'Local-IPv4': '0.0.0.0',
                'Net-Length-v4': 29,
                'Remote-IPv4': '0.0.0.0'
            }
            BGP = {'Local-AS': 0, 'Remote-AS': 0}
            MRT = {'File': ''}
            WriteRINConf(IP, BGP, MRT)

        else:
            # Inquirer!! :)
            q = [
                inquirer.List('Interface',
                              message="Select interface to configure",
                              choices=psutil.net_if_addrs().keys(),
                              default=getCurrentParam('Interface'),
                              ),
                # Local address
                inquirer.Text('Local-IPv4',
                              message='Local IPv4 Address (without netmask)',
                              default=getCurrentParam('Local-IPv4')),
                # Remote address
                inquirer.Text('Remote-IPv4', message='Remote IPv4 Address (without netmask)',
                              default=getCurrentParam('Remote-IPv4')),
                #Net-Length
                inquirer.Text('Net-Length-v4',
                              message='Network Length for IPv4 (29, 30, 24...)',
                              default=getCurrentParam('Net-Length-v4')),

                # BGP
                inquirer.Text('Local-AS', message='Local BGP AS Number (3356, 174...)',
                              default=getCurrentParam('Local-AS')),
                inquirer.Text('Remote-AS', message='Remote BGP AS Number (33932, 213303...)',
                              default=getCurrentParam('Remote-AS')),

                # MRT
                inquirer.Text('file', message='MRT File Path (level3.mrt)', default=getCurrentParam('file')),

            ]

            r = inquirer.prompt(q)

            IP = {'Interface': r['Interface'], 'Local-IPv4': r['Local-IPv4'], 'Net-Length-v4': r['Net-Length-v4'],
                  'Remote-IPv4': r['Remote-IPv4'], }
            BGP = {'Local-AS': r['Local-AS'], 'Remote-AS': r['Remote-AS']}
            MRT = {'File': r['file']}
            WriteRINConf(IP, BGP, MRT)
            WriteExaConf(IP, BGP)


def run(section):
    if section == 'set':
        # Run run run!
        mrt_file = getCurrentParam('file')
        if not mrt_file:
            print("Don't have configured MRT.")
            exit()

        if not os.path.isfile(mrt_file):
            print("Invalid MRT file, {} don't exists.".format(mrt_file))
            exit()
        else:
            print("Reading {}".format(mrt_file))
            with BGPDump(mrt_file) as bgp:
                exabgpconf = open("exabgp.conf", "w")
                print(bgp.count())
                for entry in bgp:
                    # entry.body can be either be TableDumpV1 or TableDumpV2
                    if not isinstance(entry.body, TableDumpV2):
                        continue  # I expect an MRT v2 table dump file

                    # get a string representation of this prefix
                    prefix = '%s/%d' % (entry.body.prefix, entry.body.prefixLength)
                    asPath = "{} {}".format(getCurrentParam('Local-AS'), entry.body.routeEntries[0].attr.asPath)
                    localPref = entry.body.routeEntries[0].attr.localPref

                    exabgpconf.write(
                        "route {} next-hop {} local-preference {} as-path {};\n".format(prefix, getCurrentParam("Local-IP"),
                                                                                        localPref, asPath))
                    # just print it for demonstration purposes
                    # print('%s -> %s' % (prefix, '/'.join(originatingASs)))
            exabgpconf.close()

action = ''
if len(sys.argv) < 2:
    print("You should specify action to do")
    exit()
else:
    action = sys.argv[1]

if action == 'configure':
    if len(sys.argv) < 3:
        print("You should specify context to configure, i.e main")
        exit()
    else:
        context = sys.argv[2]
        configure(context)

if action == 'run':
    if len(sys.argv) < 3:
        print("You should specify context to configure, i.e set")
        exit()
    else:
        context = sys.argv[2]
        run(context)

import os.path
from configparser import ConfigParser
import psutil
import inquirer

configPath = 'config.ini'


def write(IP, BGP, MRT):
    Config = ConfigParser()
    Config['rin'] = {}

    # Check for empty values
    Config['rin'].update(IP)
    Config['rin'].update(BGP)
    Config['rin'].update(MRT)

    with open(configPath, 'w') as configfile:
        Config.write(configfile)


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
            write(IP, BGP, MRT)

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
            write(IP, BGP, MRT)


configure('main')

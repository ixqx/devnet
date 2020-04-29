"""

1.Собрать со всех устройств файлы конфигураций, сохранить их на диск, используя имя устройства и текущую дату в составе имени файла.

2. Проверить на всех коммутаторах-включен ли протокол CDP и есть ли упроцесса CDP на каждом из устройств данные о соседях.

3. Проверить, какой тип программного обеспечения(NPE или PE)* используется на устройствах и собрать со всех устройств данные о версиии спользуемого ПО.

4. Настроить на всех устройствах timezone GMT+0, получение данных для синхронизации времени от источника во внутренней сети, предварительно проверив его доступность.

5. Вывести отчет в виде нескольких строк, каждая изкоторых имеет следующий формат, близкий к такому:
    Имя устройства -тип устройства -версия ПО -NPE/PE -CDP on/off, Xpeers-NTP in sync/not sync.
    Пример:
ms-gw-01|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |PE|CDP is ON,5peers|Clock in Sync
ms-gw-02|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |NPE|CDP is ON,0 peers|Clock in Sync
"""

import datetime
import yaml
import netmiko
import re
import subprocess


###

DEBUG = 0 

def save_config(hostname, config):
    """
    save config into file
    """

    # get time
    now = datetime.datetime.now()

    # construct filename
    filename=hostname+"_"+now.strftime("%Y_%m_%d")
    if DEBUG:
        print(filename)

    with open(filename, 'w') as f:
        f.write(config)


def check_cdp(cli_output):
    """
    check cdp status:
        CDP is ON
	CDP is OFF
    """

    if "CDP is not enabled" in cli_output:
        result = "CDP is OFF"
    else:
        result = "CDP is ON"

    if DEBUG:
        print(result)
    return result


def check_cdp_nei(cli_output):
    """
    check and return the number of cdp peers
    """

    peers = 0
    cli_output = sh_cdp_nei.split('\n')
    for line in cli_output:
        if line.startswith('Device ID'):
            peers=len(cli_output)-cli_output.index(line)
    if DEBUG:
        print(peers)
    return peers


def check_ver(sh_ver):
    """
    check show version output and return
    NPE/PE for "No Payload Encryption" / "Payload Encryption"
    device type
    software version
    """

    result="NOTFOUND"
    cli_output = sh_ver.split('\n')
    for line in cli_output:
        if 'k9' and 'software' in line.lower():
            match=re.search(r'.+ Software, (?P<dev>\S+) Software \((?P<type>\S+K9\S+)\).+Version (?P<version>\S+),.+', line)
            break
    if match:
        result=match.group('dev')+"|"+match.group('version')
        if 'npe' in match.group('type').lower():
            result=result+"|"+'NPE'
        else:
            result=result+"|"+'PE'

    return result


def check_ntp(ping_output):
    """
    check NTP server 192.168.100.1 availability
    return
        1 - available
        0 - unavailable
    """
    success_rate = 0
    cli_output = ping_output.split('\n')
    for line in cli_output:
        if "Success rate is" in line:
            success_rate = line[len('Success rate is '):line.find(' percent')]
    success_rate = int(success_rate)
    if success_rate > 0:
        if DEBUG:
            print("NTP server 192.168.100.1 available")
        return 1
    else:
        if DEBUG:
            print("NTP server 192.168.100.1 unavailable")
        return 0

def check_ntp_status(cli_output):
    """
    check ntp status
    return
        Clock in Sync - if clock synchronized
	Clock not in Sync - if clock unsynchronized
    """
    cli_output = cli_output.split('\n')
    for line in cli_output:
        if 'Clock is' in line:
            if ' synchronized' in line:
                return "Clock in Sync"
    return "Clock not in Sync"



######
"""
MAIN
"""

#load device data into list of ictionaries
with open('devices.yaml', 'r') as f:
    devices = yaml.safe_load(f)

with open('output.txt', 'w') as f:
    for device in devices:
        with netmiko.ConnectHandler(**device) as ssh:
            try:
                ssh.enable()

                hostname=ssh.find_prompt()[:-1]

                # run commands and save output

                sh_config = ssh.send_command("show run")
                if DEBUG:
                   print("...got config...")

                sh_cdp = ssh.send_command("show cdp")
                if DEBUG:
                    print("...got CDP...")

                if "CDP is not enabled" not in sh_cdp:
                    sh_cdp_nei = ssh.send_command("show cdp nei")

                sh_ver = ssh.send_command("show version | i Cisco")
                if DEBUG:
                   print("...got show ver...")

                ping_output = ssh.send_command("ping 192.168.100.1")
                if DEBUG:
                   print("...checking NTP server...", ping_output)

                commands=["clock timezone GMT 0", "ntp server 192.168.100.1"]
                if check_ntp(ping_output):
                    result = ssh.send_config_set(commands)
                else:
                    print("NTP server not available for", device['ip'])
                    print("...skipping NTP configuration...")

                sh_ntp = ssh.send_command("sh ntp stat | i Clock is")
                if DEBUG:
                    print("...checking NTP status...")

            except netmiko.ssh_exception.NetMikoTimeoutException:
                print("Connection to device timed-out")
            except:
                print("ssh connection error")

        save_config(hostname, sh_config)
        result = hostname + "|"
        result = result + check_ver(sh_ver) + "|" 
        result = result + check_cdp(sh_cdp) + ", "
        result = result + str(check_cdp_nei(sh_cdp_nei)) + " peers|"
        result = result + check_ntp_status(sh_ntp)
        print(result)
        f.write(result+'\n')

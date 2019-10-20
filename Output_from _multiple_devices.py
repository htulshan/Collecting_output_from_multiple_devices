from itertools import repeat
from concurrent.futures import ThreadPoolExecutor
import netmiko
import csv
import yaml
import logging
from datetime import datetime
import time

class OutputFromMultipleDevices():

    logging.basicConfig(format = '%(threadName)s %(name)s %(levelname)s: %(message)s',level=logging.INFO)

    def login_and_collect_outputs(self, devicedata, commandset):

        start_msg = '===> {} {}: {}'
        received_msg = '<=== {} {}: {}'

        try:
            logging.info(start_msg.format(datetime.now(), 'Connection requested to', devicedata['ip']))

            device = netmiko.ConnectHandler(**devicedata)
            device.enable()
        except:
            logging.info(received_msg.format(datetime.now(), 'Connection failed to', devicedata['ip']))

            return devicedata['ip'], 'Unable to login\n'
        else:
            logging.info(received_msg.format(datetime.now(), 'Connection established with', devicedata['ip']))
            logging.info(start_msg.format(datetime.now(), 'Collecting output from', devicedata['ip']))

            output = ''
            for command in commandset:
                output += f"\n{device.send_command(command, strip_command = False)}\n"
            device.disconnect()

            logging.info(received_msg.format(datetime.now(), 'Collected outputs from', devicedata['ip']))

            return devicedata['ip'], output


    def main(self):
        logindatalist = []
        commandsetlist = []

        print("=="*20)
        input("Please make sure that login data is stored in 'logindata.csv' file and show command is stored in 'commandset.yaml' file, hit RETURN to continue")

        print("=="*20)
        print('Reading logindata.')
        with open('logindata.csv') as f:
            logindatalist = list(csv.DictReader(f))

        print("=="*20)
        print('Reading show command.')
        with open('commandset.yaml') as f:
            commandsetlist = yaml.safe_load(f)

        print("=="*20)
        print('Connecting to devices and collecting outputs.')
        print("=="*20)
        with ThreadPoolExecutor(max_workers=5) as executor:
            result = list(executor.map(self.login_and_collect_outputs, logindatalist, repeat(commandsetlist)))

        print("=="*20)
        print('Writing Data to "output.txt" file.')
        with open('output.txt', 'w') as f:
            for i in result:
                for j in i:
                    f.write(f"{j}\n")
        print("=="*20)

        print("=="*20)
        input('Data written to output.txt file, hit RETURN to exit ')
        print("=="*20)



if __name__ == "__main__":
    test = OutputFromMultipleDevices()
    test.main()

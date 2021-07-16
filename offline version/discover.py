#!/usr/bin/env python
__version__ = "0.0.1"
__author__ = "Utkarsh Mahar"
__author_email__ = "umahar@cisco.com"
__copyright__ = "Copyright (c) 2021 Cisco Systems. All rights reserved."
__license__ = "MIT"


import sys

from genie.conf.base import Device
import pprint
from mac_vendor_lookup import MacLookup
import csv
import yaml
import pprint
import os
from datetime import datetime
#import aide
from webexteamssdk import WebexTeamsAPI
date_time_now =  datetime.now().strftime("%d_%m_:%M")

site = sys.argv[1]
os.system('mkdir Reports')
device_folder = 'Device_Outputs/'+site
report_folder = 'Reports'
total_endpoints = 1
class Discover():

    def __init__(self):
        with open('topology.yaml') as f:
            self.topology = yaml.safe_load(f)
        self.site = site
        self.l2_switches = self.topology['sites'][site]['devices']['l2_switches']
        self.l3_switches = self.topology['sites'][site]['devices']['l3_hops']
        self.layer2_info = {}
        self.layer3_info = {}
        self.endpoints = []


    def update_layer2_information(self):
        for l2_switch in self.l2_switches:
               log("Fetching mac address table and CDP neighbors from " + str(l2_switch['hostname']))
               switch = Switch(l2_switch)
               layer_2_information = switch.get_layer2_information()
               self.layer2_info.update({l2_switch['hostname']:layer_2_information})
               log("Updated Layer 2 Information from "+str(l2_switch['hostname']))
               #for e in layer_2_information:
               #     log(e.info)

        for layer2_info, layer2_info_data in self.layer2_info.items():
          for endpoint in layer2_info_data:
            #log("updating endpoint "+endpoint.mac+" in sheet")
            self.endpoints.append(endpoint)


    def update_layer3_information(self):


          for l3_switch in self.l3_switches:
              log("Fetching layer 3 info from" + l3_switch['hostname'])
              switch = Switch(l3_switch)
              l3_info = switch.get_layer3_information()
              log("Updating layer 3 info from "+l3_switch['hostname'])
              self.layer3_info.update({l3_switch['hostname']:l3_info})

          for endpoint in self.endpoints:


              for layer3_info,layer3_info_data in self.layer3_info.items():
                  for interface, interface_data in layer3_info_data.items():
                          for neighbor, neighbor_data in interface_data['ipv4']['neighbors'].items():
                              if 'Vlan'  in interface:

                               if endpoint.vlan == interface and endpoint.mac == neighbor_data['link_layer_address']:
                                   endpoint.ip = neighbor_data['ip']
                                   log("Found IP of " + str(endpoint.mac) + '=====>' + str(neighbor_data['ip']) + " in " + str(endpoint.vlan))
                              else:
                               if endpoint.mac == neighbor_data['link_layer_address']:
                                  endpoint.ip = neighbor_data['ip']
                                  log("Found IP of "+str(endpoint.mac)+'=====>'+str(neighbor_data['ip']) +" in "+str(endpoint.vlan))




    def generate_report(self):
       self.update_layer2_information()
       self.update_layer3_information()


       with open(report_folder+'/'+self.site+'_endpoints.csv', 'w') as f:
           global total_endpoints
           total_endpoints= len(self.endpoints)
           print(total_endpoints)
           log("writing all endpoints to endpoints.csv")
           fieldnames = ['SWITCH','MAC','INTERFACE','VLAN','IP','VENDOR','CDP_PLATFORM','CDP_HOSTNAME','STATIC IP or DHCP','Cisco Comments','Customer Comments','Fabric IP (Old/New/Remove)']
           writer = csv.DictWriter(f, fieldnames=fieldnames)
           writer.writeheader()
           for endpoint in self.endpoints :
               dict = {'SWITCH': endpoint.switch,
                       'MAC': endpoint.mac,
                       'INTERFACE': endpoint.interface,
                       'VLAN': endpoint.vlan.split('Vlan')[1],
                       'IP': endpoint.ip,
                       'VENDOR': endpoint.vendor,
                       'CDP_PLATFORM': endpoint.cdp_platform,
                       'CDP_HOSTNAME': endpoint.cdp_hostname,
                       'STATIC IP or DHCP': ' ',
                       'Cisco Comments': ' ',
                       'Customer Comments': '',
                       'Fabric IP (Old/New/Remove)': ' ',

                       }
               #log("writing endpoint information about "+endpoint.mac)
               writer.writerow(dict)
       i = input(" Publish report via Webex Integration ? Y/N ")
       if i == 'Y':
           print("publishing Reports ")
           self.publish_gen_configs()
       else :
               print("Output generated in Reports folder ")


    def publish_gen_configs(self):
       #os.system("zip -r "+config_dir+".zip "+ config_dir)
       webex_api = WebexTeamsAPI(access_token=self.topology['webex']['bot_token'])
       webex_api.messages.create(roomId=self.topology['webex']['webex_room'], markdown="Publishing files for site " + site )
       webex_api.messages.create(roomId=self.topology['webex']['webex_room'], files=['Reports/'+site+'_endpoints.csv'])
       webex_api.messages.create(roomId=self.topology['webex']['webex_room'], files=['Reports/'+site+'_endpoints_' + date_time_now + '.log'])

class Switch():


    def __init__(self,switch):
        try:
         self.hostname = switch['hostname']
         self.endpoints = []
         self.dev = Device(name='aName', os='ios')
         self.dev.custom.abstraction = {'order': ['os']}
         self.layer3_info = {}
         self.ignore_trunks = switch['trunks_to_ignore_for_mac_learn']

        except :
            print()

    def get_layer2_information(self):
        self.get_mac_address_table()
        self.get_cdp_neighbors()

        return self.endpoints

    def get_layer3_information(self):
        with open(device_folder + '/' + self.hostname + '/show_arp.txt', encoding='utf8',errors='ignore') as f:
        #with open(device_folder + '/' + self.hostname + '/show_arp.txt') as f:
        #with open(device_folder + '/'+self.hostname + '/show_arp.txt', newline='', encoding='utf16') as f:
            data = f.read()
        pprint.pprint("Parsing show show arp from " + self.hostname)
        parsed_output = self.dev.parse('show arp', output=data)
        log(parsed_output)
        return(parsed_output['interfaces'])
        for interface, interface_data in parsed_output['interfaces'].items():
            for neighbor, neighbor_data in interface_data['ipv4']['neighbors'].items():
                  self.layer3_info[neighbor_data['link_layer_address']] = neighbor_data['ip']
        return self.layer3_info

    def get_mac_address_table(self):
        log("Parsing show mac address-table from " + self.hostname)
        #with open(device_folder + '/' + self.hostname + '/show_mac_address-table.txt', 'rb') as f:

        #with open(device_folder+'/'+self.hostname+'/show_mac_address-table.txt') as f:
        with open(device_folder + '/' + self.hostname + '/show_mac_address-table.txt', encoding='utf8', errors='ignore') as f:
        #with open(device_folder + '/'+self.hostname + '/show_mac_address-table.txt', newline='', encoding='utf16') as f:
            data = f.read()
        pprint.pprint("Parsing show mac address-table from "+ self.hostname)
        parsed_output = self.dev.parse('show mac address-table',output=data)
        #pprint.pprint(parsed_output)
        log(parsed_output)
        for vlan , vlan_data in parsed_output['mac_table']['vlans'].items():
            #log("ignoring internal mac addresses shown as CPU ")
            if 'all' not in vlan:
                for mac_address, mac_address_data in vlan_data['mac_addresses'].items():

                    try:
                        for interface in mac_address_data["interfaces"]:
                            if 'thernet' in interface:

                                log("found physical interface ")
                                physical_interface = interface
                                # log("Ignoring duplicate mac addresses learnt over trunk interfaces ")
                                if physical_interface not in self.ignore_trunks:

                                    endpoint = Endpoint(mac_address)
                                    endpoint.interface = physical_interface
                                    endpoint.vlan = 'Vlan' + vlan
                                    endpoint.switch = self.hostname
                                    try:
                                        endpoint.vendor = MacLookup().lookup(mac_address)
                                    except:
                                        endpoint.vendor = 'Vendor Not Found'
                                    # log("Collecting information about " + mac_address +"__"+ endpoint.vendor+"on " + "Vlan" + vlan)
                                    self.endpoints.append(endpoint)
                    except:
                        log("Did not find any drop for "+ mac_address)

                        endpoint = Endpoint(mac_address)
                        endpoint.interface = "Interface Not Found/ Drop"
                        endpoint.vlan = 'Vlan' + vlan
                        endpoint.switch = self.hostname
                        try:
                            endpoint.vendor = MacLookup().lookup(mac_address)
                        except:
                            endpoint.vendor = 'Vendor Not Found'
                            # log("Collecting information about " + mac_address +"__"+ endpoint.vendor+"on " + "Vlan" + vlan)
                        self.endpoints.append(endpoint)




    def get_cdp_neighbors(self):
        try:
            log("Parsing show cdp neighbor from " + self.hostname)
            file_location = 'configs/' + self.hostname + '/show_cdp_neighbors.txt'
            with open(device_folder + '/' + self.hostname + '/show_cdp_neighbors.txt') as f:
                # with open(device_folder + '/'+self.hostname + '/show_cdp_neighbors.txt', newline='', encoding='utf16') as f:
                data = f.read()
            log("printing cdp neighbor")
            # log(data)
            pprint.pprint("Parsing show cdp neighbor from " + self.hostname)
            parsed_output = self.dev.parse('show cdp neighbor', output=data)

            log(parsed_output)
            for endpoint in self.endpoints:
                for cdp_neighbor_index, cdp_neighbor_data in parsed_output['cdp']['index'].items():
                    if cdp_neighbor_data['local_interface'] == endpoint.interface:
                        endpoint.cdp_platform = cdp_neighbor_data['platform']
                        endpoint.cdp_hostname = cdp_neighbor_data['device_id']
                        log("Updating cdp information for " + endpoint.mac + "as " + endpoint.cdp_platform)
        except Exception as e:
            log("Found Exception in CDP ")
            log(str(e))

class Endpoint():

    def __init__(self,mac):
        self.mac = mac
        self.vlan = None
        self.ip = None
        self.interface = None
        self.switch = None
        self.entry_type = None
        self.cdp_hostname = None
        self.device_type = None
        self.cdp_platform = None
        self.vendor = None

    def info(self):
        endpoint = { 'mac' : self.mac,  'vlan' : self.vlan, 'vendor' : self.vendor}
        return endpoint



def log(message):
        with open('Reports/'+site+'_endpoints_' + date_time_now + '.log', 'a') as f:
            f.write(
                "--------------------------------------------------------------------------------------------------------------------- \n")
            if type(message) != str:
                f.write(pprint.pformat(message))
                f.write("\n")

            else:
                f.write(message)
            f.write(
                "\n---------------------------------------------------------------------------------------------------------------------- \n")

def aide_telemetry():
            project_id = input(" Enter Project ID (pid) ")
            print(total_endpoints)
            potential_savings = (total_endpoints ) * 0.05
            print("Approximate hours saved ", potential_savings)
            try:
                aide.submit_statistics(
                    pid=project_id,  # This should be a valid PID
                    tool_id= 53661,
                    metadata={
                        "potential_savings" : potential_savings,  # Hours
                        "report_savings" : True,
                    },
                )
            except Exception:
                pass


if __name__ == '__main__':
    discover = Discover()
    discover.generate_report()

    #aide_telemetry()


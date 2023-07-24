#!/usr/bin/env python
__version__ = "0.0.1"
__author__ = "Utkarsh Mahar"
__author_email__ = "umahar@cisco.com"
__copyright__ = "Copyright (c) 2021 Cisco Systems. All rights reserved."
__license__ = "MIT"


import sys
from openpyxl import Workbook
from genie.conf.base import Device
import pprint
from mac_vendor_lookup import MacLookup
import csv
import yaml
import pprint
import os
from datetime import datetime
import ipaddress
#import aide
from webexteamssdk import WebexTeamsAPI
date_time_now =  datetime.now().strftime("%d_%m_%M")

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
        self.l3_interfaces = {}



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

    def get_l3hop_svis(self):

        for l3_switch in self.l3_switches:

            log("Fetching layer 3 info from " + l3_switch['hostname'])
            switch = Switch(l3_switch)
            l3_ips = switch.get_l3_ip_mask()

            for l3_ip in l3_ips:
             try:
                    network_address = ipaddress.IPv4Network(l3_ip, strict=False)
             except:
                    log("Cannot find network of " + l3_ip)
             count = 0
             for endpoint in self.endpoints:

                try:
                   endpoint_ip = ipaddress.IPv4Address(endpoint.ip)
                   if endpoint_ip in network_address:
                      log(endpoint.ip + " part of " + l3_ip)
                      count = count + 1
                except:
                    pass
             l3_ips[l3_ip]["endpoint_count"] = count


            self.l3_interfaces[l3_switch["hostname"]]  = l3_ips
            log("Updated L3 interfaces for " + l3_switch["hostname"])
            log(self.l3_interfaces[l3_switch["hostname"]])




    def generate_report(self):

       self.update_layer2_information()
       self.update_layer3_information()
       self.get_l3hop_svis()


       with open(report_folder+'/'+self.site+'_endpoints.csv', 'w') as f:
           global total_endpoints
           total_endpoints= len(self.endpoints)

           log("writing all endpoints to endpoints.csv")
           fieldnames = ['SWITCH','MAC','INTERFACE','VLAN','INTERFACE_SPEED','INTERFACE_TYPE','IP','VENDOR','CDP_PLATFORM','CDP_HOSTNAME','STATIC IP or DHCP','Cisco Comments','Customer Comments','Fabric IP (Old/New/Remove)']
           writer = csv.DictWriter(f, fieldnames=fieldnames)
           writer.writeheader()
           for endpoint in self.endpoints :
               dict = {'SWITCH': endpoint.switch,
                       'MAC': endpoint.mac,
                       'INTERFACE': endpoint.interface,
                       'INTERFACE_SPEED': endpoint.interface_speed,
                       'INTERFACE_TYPE': endpoint.interface_type,
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
       self.csv_to_xlsx(report_folder+'/'+self.site+'_endpoints.csv',report_folder + '/' + self.site + '_endpoints.xlsx')
       with open(report_folder+'/'+self.site+'_l3_interfaces.csv', 'w') as f:
           log("writing all l3 interfaces to l3_interfaces.csv")
           fieldnames = ['SWITCH','INTERFACE','DESCRIPTION','IP',"ENDPOINT_COUNT"]
           writer = csv.DictWriter(f, fieldnames=fieldnames)
           writer.writeheader()
           for key, data in self.l3_interfaces.items():

             for key1,data1 in data.items():

               dict = {'SWITCH': key,
                       'INTERFACE': data1["interface"],
                       'DESCRIPTION': data1["description"],
                       'IP': key1,
                       'ENDPOINT_COUNT': data1["endpoint_count"]
                       }

               # log("writing endpoint information about "+endpoint.mac)
               writer.writerow(dict)
       self.csv_to_xlsx(report_folder + '/' + self.site + '_l3_interfaces.csv',report_folder + '/' + self.site + '_l3_interfaces.xlsx')
       i = input(" Publish report via Webex Integration ? Y/N ")
       if i == 'Y':
           print("publishing Reports ")
           self.publish_gen_configs()
       else :
               print("Output generated in Reports folder ")


    def csv_to_xlsx(self,csv_file, xlsx_file):
        try:
            # Create a new Workbook and select the active sheet
            wb = Workbook()
            sheet = wb.active

            # Read the CSV file and write its contents to the XLSX file
            with open(csv_file, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row_index, row in enumerate(csv_reader, start=1):
                    for col_index, cell_value in enumerate(row, start=1):
                        sheet.cell(row=row_index, column=col_index, value=cell_value)

            # Save the data to the XLSX file
            wb.save(xlsx_file)

            log(f"Conversion successful. Data written to {xlsx_file}")
        except FileNotFoundError:
            log("Error: CSV file not found.")
        except Exception as e:
            log(f"Error: {e}")
    def publish_gen_configs(self):
       #os.system("zip -r "+config_dir+".zip "+ config_dir)
       try:
        webex_api = WebexTeamsAPI(access_token=self.topology['webex']['bot_token'])
        webex_api.messages.create(roomId=self.topology['webex']['webex_room'], markdown="Publishing files for site " + site )
        webex_api.messages.create(roomId=self.topology['webex']['webex_room'], files=['Reports/'+site+'_endpoints.csv'])
        webex_api.messages.create(roomId=self.topology['webex']['webex_room'], files=['Reports/'+site+'_endpoints_' + date_time_now + '.log'])
       except:
           print("Error in publishing report")
class Switch():


    def __init__(self,switch):

         self.hostname = switch['hostname']
         self.endpoints = []
         self.dev = Device(name='aName', os='ios')
         self.dev.custom.abstraction = {'order': ['os']}
         self.layer3_info = {}
         self.interfaces = {}
         self.l3_interfaces = {}
         try:
             self.ignore_trunks = switch['trunks_to_ignore_for_mac_learn']
         except:
             pass


    def get_layer2_information(self):
        self.get_interface_status()
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
                                        if 'trunk' != self.interfaces['interfaces'][physical_interface]['vlan'] or 'routed' != self.interfaces['interfaces'][physical_interface]['vlan']:
                                            endpoint.interface_type = 'access'
                                        else:
                                            endpoint.interface_type = self.interfaces['interfaces'][physical_interface]['vlan']
                                        endpoint.interface_speed = self.interfaces['interfaces'][physical_interface]['port_speed']
                                    except:
                                        endpoint.interface_speed = "not found"
                                        endpoint.interface_type = "not found"
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
                        endpoint.interface_speed = "Interface Not Found/ Drop"
                        endpoint.interface_type = "Interface Not Found/ Drop"
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

    def get_interface_status(self):
            log("Parsing show interface status from " + self.hostname)
            file_location = 'configs/' + self.hostname + '/show_interface_status.txt'
            with open(device_folder + '/' + self.hostname + '/show_interface_status.txt') as f:
                # with open(device_folder + '/'+self.hostname + '/show_cdp_neighbors.txt', newline='', encoding='utf16') as f:
                data = f.read()
            log("printing interface")
            # log(data)
            pprint.pprint("Parsing show  interface from " + self.hostname)
            self.interfaces = self.dev.parse('show interfaces status', output=data)
            log(self.interfaces)

    def get_l3_ip_mask(self):
        log("Parsing show interface from " + self.hostname)
        file_location = 'configs/' + self.hostname + '/show_interface.txt'
        with open(device_folder + '/' + self.hostname + '/show_interface.txt') as f:
            # with open(device_folder + '/'+self.hostname + '/show_cdp_neighbors.txt', newline='', encoding='utf16') as f:
            data = f.read()
        log("printing interface")
        # log(data)
        pprint.pprint("Parsing show  interface from " + self.hostname)
        detail_interfaces = self.dev.parse('show interfaces', output=data)
        log(detail_interfaces)
        for key,data in detail_interfaces.items():

           interface = key
           description = None
           ip_addresses = None
           try:
            ip_addresses = data["ipv4"]
           except:
               pass
           try:
            description = data["description"]
           except:
               pass
           if ip_addresses:
               for ip_address in ip_addresses:
                   self.l3_interfaces[ip_address] = {"interface":interface,"description":description}

        return self.l3_interfaces

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
        self.interface_speed = None
        self.interface_type = None

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


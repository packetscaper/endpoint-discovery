# Endpoint Discovery 

<p align="center">
<a href="https://cxtools.cisco.com/cxestore/#/toolDetail/53661"><img alt="CX eStore Tool ID" src="https://img.shields.io/badge/TOOL%20ID-53661-blue"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>
Discovery and analysis of endpoints is an essential step in planning migrations of networks from legacy environments to SDA.
This script helps in gathering endpoint information from legacy network

More details [here]( https://cisco-my.sharepoint.com/:p:/r/personal/umahar_cisco_com/Documents/Presentations/Endpoint-Discovery/endpoint-discover.pptx?d=w7c9755a9419c422695a893fcb34481af&csf=1&web=1&e=HDL17e )


## Getting Started

Follow below instructions to setup the environment for running the script.

## Prerequisites

Python <= 3.10.X

```
pip3 install -r requirements.txt 

```
## Usage

### 

```
python3 discover.py -h
usage: discover.py [-h] --site SITE --file FILE [--webex WEBEX] [--ssh_options SSH_OPTIONS] [--offline]

options:
  -h, --help                                         show this help message and exit
  --site SITE                                        Site name
  --file FILE                                         Input filename
  --webex WEBEX                             Webex file for publishing
  --ssh_options  SSH_OPTIONS      SSH Options for old ciphers
  --offline                                           Offline sites


```

### Example 1 - Standard scenario

```
python3 discover.py --site site_name --file seed_file.xlsx 

```


### Example 2 - No ability to run the script in customer's environment

-  Create a folder under offline_sites. Folder name should be the same as the site name
-  Copy outputs of the devices. Follow the format of the test site - cml_labs. 
   



```
python3 discover.py --site site_name --file seed_file.xlsx --offline 

```

### Example 3 - Publish reports using webex apis in a webx teamspace

```
python3 discover.py --site site_name --file seed_file.xlsx --webex webex.yaml 

```

webex.yaml 

```
  WEBEX:
      WEBEX_BOT_TOKEN: N2NlMjQyZjEtNDViNC00NDQyLTg2NWUtNjhjYTFiNzM0ZDBhYTc2N2VmZDktOWU1_PF84_1ed
      WEBEX_ROOM: dL1JPT00vNjI1YjdlYTAtNDdmZi0xMWVlLWFiMjUtZmI1ZDNmYWNlMmVk
```


### Example 4 - SSH to devices running old IOS or older ciphers

- Use --ssh_options " "
- Try various options to see what works in your environment
- Below example works for IOS and NXOS devices in CML 

```
python3 discover.py --site site_name --file seed_file.xlsx  --ssh_options " -o KexAlgorithms=+diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1 -o HostkeyAlgorithms=+ssh-rsa"
```


## Offline site - cml_lab

Test Site

![Alt text](https://imgur.com/GLCiDI2.png) 


CML Topology

![Alt text](https://imgur.com/9rACpj0.png) 


## Reports generated


### Endpoint Report

 <!-- TABLE_GENERATE_START -->

| SWITCH     | MAC            | INTERFACE          | INTERFACE_SPEED | INTERFACE_TYPE | VLAN | IP          | VENDOR           | CDP_PLATFORM | CDP_HOSTNAME | STATIC IP or DHCP | Cisco Comments | Customer Comments | Post-Migration-IP | Critical Endpoint |
|------------|----------------|--------------------|-----------------|----------------|------|-------------|------------------|--------------|--------------|-------------------|----------------|-------------------|-------------------|-------------------|
| l3_iosxe_1 | 5254.0015.ce16 | GigabitEthernet0/2 | auto            | trunk          | 1    | 10.10.55.1  | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_iosxe_1 | 5254.0016.4925 | GigabitEthernet1/0 | auto            | 100            | 100  | 10.100.10.6 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_iosxe_1 | 5254.0013.2603 | GigabitEthernet1/1 | auto            | 200            | 200  | 10.200.10.3 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_iosxe_1 | 5254.0015.ce16 | GigabitEthernet0/2 | auto            | trunk          | 300  | 10.20.10.0  | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.000d.2708 | Port-channel23     | auto            | trunk          | 1    |             | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.0019.2a8e | Port-channel23     | auto            | trunk          | 1    |             | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.0009.94e7 | GigabitEthernet1/0 | auto            | 100            | 100  | 10.100.10.3 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.0009.cb0e | GigabitEthernet1/1 | auto            | 100            | 100  | 10.100.10.4 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.000d.742e | GigabitEthernet1/2 | auto            | 100            | 100  | 10.100.10.5 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.0010.a31a | Port-channel23     | auto            | trunk          | 100  | 10.100.10.7 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.0013.0485 | Port-channel23     | auto            | trunk          | 100  | 10.100.10.8 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_iosxe_1 | 5254.000f.d7c2 | GigabitEthernet2/1 | auto            | 200            | 200  | 10.200.10.2 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_nxos_1  | 5254.000a.415a | Ethernet1/4        | 1000            | 200            | 200  | 10.200.10.6 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_nxos_2  | 5254.001c.cf91 | Ethernet1/4        | 1000            | 101            | 101  | 10.101.10.2 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_nxos_2  | 5254.000d.42ed | Ethernet1/6        | 1000            | 201            | 201  | 10.201.10.3 | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l3_nxos_2  | 5254.0001.4e17 | Ethernet1/2        | 1000            | trunk          | 300  | 10.20.10.6  | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_nxos_2  | 5254.0012.9850 | Ethernet1/3        | 10g             | full           | 1    |             | Vendor Not Found |              |              |                   |                |                   |                   |                   |
| l2_nxos_2  | 5254.0011.b7d7 | Port-channel23     | 1000            | trunk          | 101  | 10.101.10.4 | Vendor Not Found |              |              |                   |                |                   |                   |                   |


<!-- TABLE_GENERATE_END -->


#### Layer 3 Switch Report


| SWITCH     | INTERFACE     | DESCRIPTION     | IP               | ENDPOINT_COUNT |
|------------|---------------|-----------------|------------------|----------------|
| l3_iosxe_1 | Vlan1         |                 | 10.10.55.35/24   | 1              |
| l3_iosxe_1 | Vlan100       | data_vlan       | 10.100.10.253/24 | 6              |
| l3_iosxe_1 | Vlan200       | voice_vlan      | 10.200.10.253/24 | 2              |
| l3_iosxe_1 | Vlan300       | wan_link        | 10.20.10.1/31    | 1              |
| l3_iosxe_2 | Port-channel1 | datacenter_link | 10.20.20.0/31    | 0              |
| l3_iosxe_2 | Vlan1         | management      | 10.10.55.36/24   | 1              |
| l3_iosxe_2 | Vlan100       | data_vlan       | 10.100.10.254/24 | 6              |
| l3_iosxe_2 | Vlan200       | voice_vlan      | 10.200.10.254/24 | 2              |
| l3_iosxe_2 | Vlan300       | wan_link        | 10.20.10.3/31    | 0              |
| l3_nxos_1  | port-channel1 | office_network  | 10.20.20.1/31    | 0              |
| l3_nxos_1  | Vlan11        | management      | 10.11.23.253/24  | 0              |
| l3_nxos_1  | Vlan101       | r&d             | 10.101.10.253/24 | 2              |
| l3_nxos_1  | Vlan201       | prod            | 10.201.10.253/24 | 3              |
| l3_nxos_1  | Vlan300       | wan_link        | 10.20.10.5/31    | 0              |
| l3_nxos_2  | Vlan11        | management      | 10.11.23.254/24  | 0              |
| l3_nxos_2  | Vlan101       | r&d             | 10.101.10.254/24 | 2              |
| l3_nxos_2  | Vlan201       | r&d             | 10.201.10.254/24 | 3              |
| l3_nxos_2  | Vlan300       | wan_link        | 10.20.10.7/31    | 1              |

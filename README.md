# Endpoint Discovery 


Discovery and analysis of endpoints is an essential step in planning migrations of networks from legacy environments to SDA.
This script helps in gathering endpoint information from legacy network


 <!-- TABLE_GENERATE_START -->

|SWITCH| MAC  | INTERFACE | VLAN| IP|  Vendor   | CDP_PLATFORM | CDP_HOSTNAME |
| -------|------ | ------------- | ---------|------|----|----------|----------|
|switch01| 001e.f728.1c3e| TwoGigabitEthernet1/0/3|402|Cisco Systems, Inc| 192.22.4.1|IP Phone|  SEP001EF7281C3E | 
|switch02|683b.78f9.3ff2|TenGigabitEthernet1/0/48|302|Cisco Systems, Inc|192.22.5.33 |AIR-AP380| BND-AP02|

<!-- TABLE_GENERATE_END -->

## Getting Started

Follow below instructions to setup the environment for running the script.

## Prerequisites

Python 3.x

```
pip3 install -r requirements.txt 

```
## Usage

### Step 1 - Populate topology.yaml

Fill topology.yaml in the below format 

```
---

sites:
  site1:
     devices:
         l3_hops:
           - hostname: site1_switch1
         l2_switches:
           - hostname: site1_switch1
             trunks_to_ignore_for_mac_learn
                - Port-Channel1
           - hostname: site1_switch2
             trunks_to_ignore_for_mac_learn
                - Port-Channel1
             
  site2
      l3_hops:
           - hostname: site2_swi01
         l2_switches:
           - hostname: site2_swi01
             trunks_to_ignore_for_mac_learn
                - N/A
```

### Step 2 - Populate Device Outputs
In the folder Device_Outputs create a folder per site. The folder name should match the site names in the topology.yaml file.
Each site folder will contain files names as below with the outputs from the device. 

l2_switches 
 
    - show_mac_address-table.txt
    - show_cdp_neighbors.txt

l3_hops

    - show_arp.txt
    
    
### Step 3 - Run the script

```

python3 discovery.py site1


```

2 files will be generated in the Reports folder
1. site1_endpoints.csv 
2. site1_endpoints_<date>.log 


````



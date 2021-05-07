# Endpoint Discovery 

<p align="center">
<a href="https://cxtools.cisco.com/cxestore/#/toolDetail/53661"><img alt="CX eStore Tool ID" src="https://img.shields.io/badge/TOOL%20ID-53661-blue"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>
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

### There are 2 versions of the script

#### direct access 

Customers which allow running the script directly in their environment. 

#### offline version 

Customers which do not allow running the script directly.
The show outputs are taken from the devices and the script is run offline. 



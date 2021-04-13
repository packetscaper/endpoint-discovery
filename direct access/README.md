## Usage

### Step 1 - Initialize topology.yaml 

Initialize the topology.yaml 


### Step 2 - Populate topology.yaml

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

### Step 2 - Initialize topology.yaml 

Initialize the topology.yaml 
    
### Step 3 - Run the script

```

python3 discovery.py site1


```

2 files will be generated in the Reports folder

````
1. site1_endpoints.csv 
2. site1_endpoints_<date>.log 


````


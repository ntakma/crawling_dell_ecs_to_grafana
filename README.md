# dell_emc_ecs

## install dependencies
``` 
pip install -r requirements.txt
```
### config telegraf 
```

[[inputs.exec]]
        commands = [ "/usr/bin/python3 **/PATH_TO_SCRIPT/**getdata_dell_ecs.py" ]
        name_override = "dell_ecs"
        timeout = "11s"
        data_format = "influx"

```

## data output example 

```
ecs_emc numNodes=6,numGoodNodes=6,numBadNodes=0,numDisks=270,numGoodDisks=270,numBadDisks=0,diskSpaceTotalCurrent=3015900,diskSpaceFreeCurrent=2890560,diskSpaceAllocatedCurrent=125339,alertsNumUnackError=0,alertsNumUnackCritical=0

```

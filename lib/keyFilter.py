def keyFilter(type, keyFilter, key):
    if keyFilter == "None":
        return True
    
    if type == 'ASSET':
        if keyFilter == 'orange':
            if key == "zona1":
                return False
            if "_" in key:
                return False
            if "zona" in key:
                return True

    if type == 'DEVICE':
        if keyFilter == 'orange':
            if key == "none":
                return False
            
            if key == "PS":
                return False
            
            if "SECCIONADOR" in key:
                return False
            
            if "GRENERAL" in key:
                return False

            if "LA FINCA" in key:
                return False    

            if key in [
                "EDAILY1",
                "EDAILY2",
                "EDAILY3",
                "ETOTAL1",
                "ETOTAL2",
                "ETOTAL3",
                "R2",
                "R1",
                "PUE",
                "ACTIVE POWER",
                "POWER FACTOR",
                "ALARM_COUNT",
                "T_EXT",
                "kW CON",
                "kW USO",
                "PUF",
                "DC CURRENT",
                "INPUT POWER",
                "CO2 REDUCTION",
                "PLANT STATUS",
                "E TOTAL",
                "E DAILY",
                "DAILY POWER GEN DURATION",
                "none"
            ]:
                return False
            
            return True

    return False
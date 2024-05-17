import json

def postDataFormat(data, key):
    def apply(x):
        y = dict()
        y["ts"] = x["ts"]
        y["values"] = dict()
        y["values"][key] = x["value"]
        return y

    try:        
        return json.dumps(list(map(apply, data[key])))
    except Exception as exception:
        print("An error occoured seting up post data:", exception)

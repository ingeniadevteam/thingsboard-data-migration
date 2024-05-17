import sys

def checkTarget(sourceAssets, targetAssets):
    for asset in sourceAssets:
        targetAsset = next((x for x in targetAssets if x['name'] == asset['name']), None)
        if targetAsset is None:
            print("Error:", asset['name'], "not found in target")
            sys.exit()

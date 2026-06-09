import json

with open("/Users/jungmin/Desktop/gripic_sorbonne/gripic-sorbonne.github.io/GRIPIC_last_publis.json", "r") as f:
    json_data = json.load(f)

    print(json_data)
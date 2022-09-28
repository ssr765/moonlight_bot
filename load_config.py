import json

class config:
    def __init__(self):
        with open("config/bot_config.json", "r") as f:
            d = json.load(f)
        
        # Prefix
        if d["prefix"] != "":
            self.prefix = d["prefix"]
            
        else:
            self.prefix = "$"
        
        # Embed color
        if d["embed_color"] != "":
            self.embed_color = int(d["embed_color"], base=16)
            
        else:
            self.embed_color = 0xdcdcdc
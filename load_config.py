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

        # Configuración de gambling
        class apuestas_config:
            def __init__(self, d):
                
                # Puntos iniciales
                if d["puntos_iniciales"] != None:
                    self.puntos_iniciales = d["puntos_iniciales"]
                
                else:
                    self.puntos_iniciales = 5000
        
        # Apuestas
        self.apuestas = apuestas_config(d["apuestas"])

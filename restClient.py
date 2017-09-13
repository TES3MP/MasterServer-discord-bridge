import requests
import json
import config

class RestClient:

    def __init__(self, name, passw):
        self.content = []
        self.login(name, passw)

    def login(self, name : str, passw : str):
        self.content.append({'command': 'login', 'login': name, 'passMD5': passw})

    def ban(self, address : str, reason : str):
        self.content.append({'command': 'ban', 'address': address, 'reason': reason})

    def unban(self, address : str):
        self.content.append({'command': 'unban', 'address': address})

    def banlist(self):
        self.content.append({'command': 'banlist'})

    def savebans(self):
        self.content.append({'command': 'savebans'})

    def send(self):
        r = requests.post(config.serverAddr, cert=config.cert, data=json.dumps({'content': self.content}), verify=config.rootCA)
        print(json.dumps({'content': self.content}))
        return {'code': r.status_code, 'response': r.text}


if __name__ == "__main__":
    rest = RestClient(*config.accounts['178539252563443712'])

    rest.banlist()
    print(rest.send())
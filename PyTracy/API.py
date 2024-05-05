import requests as req
import re
from SECRETS import API_KEY


class PyTracyDataFetcher:

    def __init__(self, url: str, payload: dict|None = None, headers: dict|None = None, req_auth: bool = False, param_info: dict|None = None):
        self.base_url = url
        self.payload = payload if payload else {}
        self.headers = headers if headers else {}
        self.req_auth = req_auth
        self.auth = ''
        self.param_info = param_info
        if self.param_info:
            for k in self.param_info.keys():
                assert isinstance(self.param_info[k]['type'], type), f"{k} should be of type {self.param_info[k]['type']}"
                assert isinstance(self.param_info[k]['format'], (str)), f"{k} should be of format {self.param_info[k]['format']}"

        if req_auth:
            if 'auth' in url or 'token' in url:
                self.base_url = self.base_url.replace(":auth", API_KEY)
                self.base_url = self.base_url.replace(":token", API_KEY)
                self.auth = 'in URL'
            else:
                self.headers['Authorization'] = f"Bearer {API_KEY}"
                self.auth = 'in headers'


    def __str__(self) -> str:
        return f"""
            API Format: {self.base_url}
            Payload: {self.payload}
            Headers: {self.headers}
            Auth: {self.req_auth} {self.auth}
            Parameters:
        """ + '\t' + (", ".join([i.strip('/') for i in self.base_url.split(":")[2:]]) if not self.param_info else  '\n\t\t'.join([f"{k}: {v}" for k,v in param_info.items()]))


    def fetch(self, fields: dict) -> dict:
        constructed_url = self.base_url
        for k in fields.keys():
            assert isinstance(fields[k], self.param_info[k]['type']), f"{k} should be of type {self.param_info[k]['type']}"
            assert re.fullmatch(self.param_info[k]['format'], fields[k]), f"{k} should be of format {self.param_info[k]['format']}"
            constructed_url = constructed_url.replace(f":{k}", fields[k])

        response = req.request("GET", constructed_url, headers=self.headers, data=self.payload)
        return response.json()



if __name__ == '__main__':
    headers = {
    'Accept': 'application/json'
    }
    param_info = {'instrument_key': {'type': str, 'format': r'.*'}, 'interval': {'type': str, 'format': r'1minute|30minute|day|week|month}'}, 'to_date': {'type': str, 'format': r'\d{4}-\d{2}-\d{2}'}, 'from_date': {'type': str, 'format': r'\d{4}-\d{2}-\d{2}'}}
    fetcher = PyTracyDataFetcher('https://api.upstox.com/v2/historical-candle/:instrument_key/:interval/:to_date/:from_date', headers=headers, param_info=param_info)
    print(fetcher.fetch({'instrument_key': 'NSE_INDEX%7CNifty%2050', 'interval': '1minute', 'to_date': '2023-12-31', 'from_date': '2023-12-29'}))
    print(fetcher)

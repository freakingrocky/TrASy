import requests as req
import re
from .SECRETS import API_KEY


class PyTraSyDataFetcher:

    def __init__(self, url: str, payload: dict = {}, headers: dict = {}, req_auth: bool = False, param_info: dict|None = None):
        """
        Initialize a PyTraSyDataFetcher object.

        Parameters:
            url (str): The base URL of the API endpoint.
            payload (dict, optional): The payload to be sent with the request. Defaults to an empty dictionary.
            headers (dict, optional): The headers to be sent with the request. Defaults to an empty dictionary.
            req_auth (bool, optional): A flag indicating whether authentication is required for the API. Defaults to False.
            param_info (dict, optional): A dictionary containing information about the parameters required by the API. Defaults to None.

        Returns:
            None
        """
        # Type Checking to ensure no silent errors
        _NoneType = type(None)
        isinstance(url, str), "url should be of type str"
        isinstance(payload, dict), "payload should be of type dict"
        isinstance(headers, dict), "headers should be of type dict"
        isinstance(req_auth, bool), "req_auth should be of type bool"
        isinstance(param_info, (_NoneType, dict)), "param_info should be of type dict or must be None"


        self.base_url = url
        self.payload = payload
        self.headers = headers
        self.req_auth = req_auth
        self.auth = ''
        self.param_info = param_info
        if self.param_info:
            # Type Checking param_info to ensure no silent errors
            for k in self.param_info.keys():
                assert isinstance(self.param_info[k]['type'], type), f"{k} should be of type {self.param_info[k]['type']}"
                assert isinstance(self.param_info[k]['format'], (str)), f"{k} should be of format {self.param_info[k]['format']}"

        # If the API requires authentication, then the API key should be in the URL or assumed to be in the headers.
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
        """
        Fetch data from the API endpoint using the provided fields.

        Parameters:
            fields (dict): A dictionary containing the values for the parameters required by the API endpoint.
                        The keys of the dictionary should match the parameter names in the URL.
                        The values should be of the types and formats specified in the param_info dictionary.

        Returns:
            dict: A dictionary containing the response data from the API endpoint.

        Raises:
            AssertionError: If a field value does not match the specified type or format in the param_info dictionary.
        """
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
    fetcher = PyTraSyDataFetcher('https://api.upstox.com/v2/historical-candle/:instrument_key/:interval/:to_date/:from_date', headers=headers, param_info=param_info)
    print(fetcher.fetch({'instrument_key': 'NSE_INDEX%7CNifty%2050', 'interval': '1minute', 'to_date': '2023-12-31', 'from_date': '2023-12-29'}))
    print(fetcher)

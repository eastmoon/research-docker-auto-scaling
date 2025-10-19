# Import libraries
import sys
import re
import requests
import time

# Declare class
class Service:
    ## Declare member variable
    ### Publish
    container = None
    manager = None
    ### Private
    __config = None
    __module = None
    ## Declare constructor
    def __init__(self, config, module):
        self.__config = config
        self.__module = sys.modules[module]
        if 'container' in config:
            self.container = config['container']
        if 'sys.attributes' in config:
            self.container['sys'] = config['sys.attributes'].copy()
        if 'sys.manager' in config:
            self.manager = config['sys.manager']

    ## Declare member method
    def run(self):
        if 'container' in self.__config and hasattr(self.__module, 'container'):
            self.__module.container(self, self.__config['container'])
        if 'authorize' in self.__config and hasattr(self.__module, 'authorize'):
            self.__module.authorize(self, self.__config['authorize'])
        if 'secure' in self.__config and hasattr(self.__module, 'secure'):
            self.__module.secure(self, self.__config['secure'])
        if 'command' in self.__config:
            for cmd_object in self.__config['command']:
                match cmd_object['cmd']:
                    case 'template':
                        self.template(cmd_object)
                    case 'api':
                        self.api(cmd_object)
                    case 'exec':
                        self.exec(cmd_object)
                    case 'restart':
                        self.restart(cmd_object)
                    case 'sleep':
                        self.sleep(cmd_object)
                    case _:
                        if hasattr(self.__module, 'command'):
                            self.__module.command(self, cmd_object)
        default_keys = ['module', 'container', 'authorize', 'secure', 'command']
        for key in self.__config:
            if key not in default_keys:
                if hasattr(self.__module, key):
                    target_function = getattr(self.__module, key)
                    target_function(self, self.__config[key])

    def template(self, config):
        print(f"Execute : {config['msg']}")
        if 'data' in config and 'file' in config['data']:
            conf = config['data']
            try:
                # Declare path variable
                source_file_path = f"{self.container['sys']['APP_I_DIR']}/{self.container['name']}/template/{conf['file']}"
                destination_file_path = f"{self.container['sys']['APP_I_DIR']}/{self.container['name']}/{conf['to']}" if 'to' in conf else f"/tmp/{conf['file']}"
                # Read the file's content
                with open(source_file_path, 'r') as file:
                    file_content = file.read()
                # Replace the old string with the new string
                if 'keys' in conf:
                    for key in conf['keys']:
                        modified_content = file_content.replace(f"{{{key}}}", conf['keys'][key])
                # Write the modified content back to the file
                with open(destination_file_path, 'w') as file:
                    file.write(modified_content)
                return destination_file_path
            except Exception as e:
                raise e
        else:
            raise Exception(f"Template file generate parameter not given.")

    def api(self, config):
        print(f"Execute : {config['msg']}")
        if 'data' in config and 'url' in config['data'] and 'method' in config['data']:
            conf = config['data']
            try:
                url = conf['url']
                method = conf['method']
                if re.match(r"^http[s]*://", url) == None:
                    url = f"http://{self.container['name']}:{self.container['port']}/{url}"
                data = conf['data'] if 'data' in conf else None
                headers = conf['headers'] if 'headers' in conf else None
                r = requests.request(method, url, data=data, headers=headers)
                print(r.json())
            except Exception as e:
                raise e
        else:
            raise Exception(f"Call RestAPI parameter not given.")
        return None

    def sleep(self, config):
        print(f"Execute : {config['msg']}")
        if 'time' in config:
            time.sleep(config['time'])
        else:
            raise Exception(f"Sleep parameter not given.")

    def exec(self, config):
        print(f"Execute : {config['msg']}")
        if self.manager != None:
            if 'name' in self.container and 'data' in config:
                self.manager.exec(self.container['name'], config['data'])
            else:
                raise Exception(f"Docker container execute parameter not given.")
        else:
            raise Exception(f"Docker manager object was none.")

    def restart(self, config):
        print(f"Execute : {config['msg']}")
        if self.manager != None:
            if 'name' in self.container:
                self.manager.restart(self.container['name'])
            else:
                raise Exception(f"Docker container execute parameter not given.")
        else:
            raise Exception(f"Docker manager object was none.")

    ## Declare accessor
    @property
    def config(self):
        return self.__config

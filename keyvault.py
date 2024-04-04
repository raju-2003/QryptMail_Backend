#use azure key to save keys
from azure.identity import EnvironmentCredential
from azure.keyvault.secrets import SecretClient
import logging

class Keygen:
    # bearer=""
    # scopes=["offline_access", "Mail.Send", "Mail.ReadWrite"]
    code=""
    credential=None
    client=None
    vault_url="https://comradefault.vault.azure.net/"
    logger=None
    def __init__(self):
      self.logger = logging.getLogger('azure')
      self.logger.setLevel(logging.INFO)
        

    def connect_vault(self):
        print("[+]connecting to key vault")
        self.credential = EnvironmentCredential(filename='keyvault.log',logging_enable=True)
        self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
    def get_fresh_key(self):
        #list the keys and check if disabled string is present
        print("[+]Getting fresh key from azure vault")
        key_list=self.client.list_properties_of_secrets()
        print("[+]Requesting to "+key_list.properties.vault_url+", key names fetched: ",len(key_list))
        for key in key_list:
          #  print(key.name)
           if not self.get_secret(key.name).value.startswith("DISABLED-"):
               print("key found",key.name)
               return key
    
    def get_secret(self,name):
      # print("[+]fetching secret value for keyid:"+name)
      a= self.client.get_secret(name,logging_enable=True)
      
      # print(a.properties)
      return a
      # print(self.client.)
    def disable_secret(self, name):
        # To "disable" a secret, you can create a new version with a different value
        # This effectively rotates the key
        print("[+]disableing keyid:"+name)
        current_secret = self.client.get_secret(name)
        new_secret_version = self.client.set_secret(name, "DISABLED-" + current_secret.value)
        
    def set_secret(self,name,value):
      secret = self.client.set_secret(name,value)
    def delete_secret(self,name):
      deleted_secret = self.client.begin_delete_secret(name).result()

    def get_keys(self,length):
        n=length//32+(1 if length%32 else 0)
        keys=[]
        keys.append(self.get_fresh_key())
        var=int(keys[3:])
        for i in range(1,n):
          keys.append("key"+
                      str(var+i))
            
        return keys
       
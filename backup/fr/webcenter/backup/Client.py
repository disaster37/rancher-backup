import cattle

class Client(object):


    def __init__(self, url, key, secret):

        Client._client = cattle.Client(url=url, access_key=key, secret_key=secret)


    @staticmethod
    def getClient():

        if Client._client is None:
            raise Exception("You must init the connexion first")

        return Client._client


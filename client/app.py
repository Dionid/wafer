#!/usr/bin/env python3
import http.client
import argparse
from uuid import getnode as get_mac
import json

def connect_to_server(server, port):
    return http.client.HTTPConnection(server, port)

#request to internet
def request_internet(connection, mac):
    connection.request("GET", '/request', body=json.dumps({'mac': mac}))
    res = connection.getresponse()
    print(res.read())


def use_traffic(connection, mac, amount):
    connection.request("GET", '/use_traffic', body=json.dumps({'mac': mac, 'amount': amount}))
    res = connection.getresponse()
    print(res.read())


def sign_request(request):
    pass

def send_signed_request(connection, signed_request):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', dest='server', default='34.208.247.57')
    parser.add_argument('--port', '-p', dest='port', default='8484')
    parser.add_argument('--abuse', '-a', dest='abuse', default=False)
    parser.add_argument('--use', '-u', dest='use_traffic_amount')

    args = parser.parse_args()

    mac = get_mac()
    mac_str = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    print("mac adress is {}".format(mac_str))

    connection = connect_to_server(args.server, args.port)
    if args.abuse:
        return



    if args.use_traffic_amount is not None:
        use_traffic(connection, mac, args.use_traffic_amount)
        return

    request = request_internet(connection, mac)

    # signed_request = sign_request(request)
    #
    # if signed_request is None:
    #     return
    #
    # send_signed_request(connection, signed_request)





if __name__ == "__main__":
    main()

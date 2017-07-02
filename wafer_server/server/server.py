#!/usr/bin/env python3
import netifaces as nif
from flask import Flask, request
import json
import os.path
import time
import threading

app = Flask(__name__)


class Contract(object):
    def __init__(self, router, mac, traffic = 100):
        self.id = router.max_id
        router.max_id+=1
        self.address = None
        self.isSigned = True
        self.binary = None
        self.client_mac = mac
        self.used_traffic = 0
        self.traffic = traffic
        self.last_connect_time = time.time()


class Router(object):
    def __init__(self):
        self.address_filename = ".router_address"
        self.initial_value = 100
        if os.path.isfile(self.address_filename):
            with open(self.address_filename, "r") as text_file:
                self.address = text_file.read()
                print("load router adress {}".format(self.address))
        else:
            self.address = "test_address"
            with open(self.address_filename, "w") as text_file:
                text_file.write(self.address)
                print("register router adress {}".format(self.address))

        self.max_id = 0
        self.contracts = []
        self.mac_address_white_list = []
        self.timeout = 60*60




    def check_contracts_state(self):
        for contract in self.contracts:
            if contract.address is None:
                contract.address = self.get_address_of_contract(contract.id)
                if contract.address is not None:
                    self.mac_address_white_list.append(contract.client_mac)

    def get_address_of_contract(self, id):
        print("check contract {}".format(id))
        return "test_address"

    def check_mac_table(self, mac):
        return mac in self.mac_address_white_list

    def send_contract_for_sign(self, contract):
        contract.isSigned = True
        return True

    def send_signed_contract_to_chain(self, contract):
        return True

    def create_contract(self, mac):
        return Contract(self, mac)

    def add_contract(self, contract):
        self.contracts.append(contract)

    def check_contract_proceed(self, mac):
        for contract in self.contracts:
            if contract.client_mac == mac:
                if contract.address is None:
                    return True
                else:
                    self.mac_address_white_list.append(mac)
                    print('error, mac was not added before {}'.format(mac))
                    return True
        return False

    def check_contracts_timeout(self):
        i = len(self.contracts) - 1
        while i >= 0:
            contract = self.contracts[i]
            if (time.time() - contract.last_connect_time)>self.timeout:
                print('contract delete by timeout {}'.format(contract.client_mac))
                self.close_contract(contract) #TODO if contract not approved?
                self.contracts.remove(contract)
            i-=1

    def get_contract(self, mac):
        res_contract = None
        for contract in self.contracts:
            if contract.client_mac == mac:
                res_contract = contract
                break
        return res_contract


    def use_traffic(self, contract, amount):
        contract.used_traffic+=amount
        if contract.traffic <= contract.used_traffic:
            self.close_contract(contract)
            self.contracts.remove(contract)
            return self.create_session(contract.client_mac)
        return "OK", 200

    def close_contract(self, contract):
        self.mac_address_white_list.remove(contract.client_mac)

    def create_session(self, mac):
        contract = self.create_contract(mac)

        if not self.send_contract_for_sign(contract):
            return "Contract not sended for sign", 500

        if not contract.isSigned:
            return "Contract not signed", 200

        if not self.send_signed_contract_to_chain(contract):
            return "Contract not sended to chain", 500

        self.add_contract(contract)

        return "OK", 200

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

@app.route('/')
def hello_world():
    return 'install waffle client!'


@app.route('/request')
def request_auth():
    router = app.config['router']

    req = request.get_json(force=True)
    if 'mac' not in req:
        return "Mac not found in request", 500

    mac = req['mac']
    mac_str = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    print("Mac address is {}".format(mac_str))

    if router.check_mac_table(mac):
        return "Mac already alowed", 200

    if router.check_contract_proceed(mac): #contract wait to be prooved
        return "Wait to proceed", 201

    return router.create_session(mac)


@app.route('/use_traffic')
def use_traffic():
    router = app.config['router']
    req = request.get_json(force=True)

    if 'mac' not in req:
        return "Mac not found in request", 500
    mac = req['mac']

    if 'amount' not in req:
        return "Amount not found in request", 500
    traffic_amount = int(req['amount'])


    contract = router.get_contract(mac)
    if contract is None:
        return "Contract not found in request", 500
    if contract.address is None:
        return "Contract not prooved yet", 500

    return router.use_traffic(contract, traffic_amount)




if __name__ == '__main__':
    router = Router()
    app.config['router'] = router
    contracts_state_checker = RepeatedTimer(30, router.check_contracts_state)
    contracts_sessions_checker = RepeatedTimer(30, router.check_contracts_timeout)
    app.run(debug=True, host='0.0.0.0', use_reloader=False)

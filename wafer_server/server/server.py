#!/usr/bin/env python3
import netifaces as nif
from flask import Flask, request, jsonify
import json
import os.path
import time
import threading
from functools import wraps
from utils import is_valid_address, form_data
from binascii import hexlify
from hashlib import sha256
from node import Node
import web3

app = Flask(__name__)


def acquires_node(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        node = Node(host='34.208.247.57', port='8485')
        return f(node, *args, **kwargs)
    return decorator


@acquires_node
def create_new_router(node, from_address, private_key, credit):

    tx_hash = node.sendRawTransaction(
        to_address=app.config['FACTORY_ADDRESS'],
        from_address=from_address,
        private_key=private_key,
        value=0,
        gas=150000,
        data=form_data('createNewRouter(uint256)', credit)
    )

    if tx_hash is None: return error_response()
    return success_response(tx_hash)


@acquires_node
def close_session(node, contract_address, from_address, private_key, identificator, money_for_router):

    tx_hash = node.sendRawTransaction(
        to_address=contract_address,
        from_address=from_address,
        private_key=private_key,
        value=0,
        gas=150000,
        data=form_data('closeSession(uint256, uint256)', identificator, money_for_router)
    )

    if tx_hash is None: return error_response()
    return success_response(tx_hash)


def error_response(message='Something went wrong. Transaction wasn\'t sent'):
    return jsonify({
        'success': False,
        'tx_hash': None,
        'message': message
    })


def success_response(tx_hash=None):
    return jsonify({
        'success': True,
        'tx_hash': tx_hash,
        'message': None
    })



class Contract(object):
    def __init__(self, router, mac, traffic=100):
        self.id = router.max_id
        router.max_id += 1
        self.address = None
        self.isSigned = True
        self.binary = None
        self.client_mac = mac
        self.used_traffic = 0
        self.traffic = traffic
        self.last_connect_time = -1

    def initialize_closing(self):
        if self.last_connect_time != -1:
            return
        self.last_connect_time = time.time()

class Router(object):
    def __init__(self, private_key, wallet):
        self.private_key = private_key
        self.wallet = wallet
        self.address_filename = ".router_address"
        self.initial_value = 100
        if os.path.isfile(self.address_filename):
            with open(self.address_filename, "r") as text_file:
                self.address = text_file.read()
                print("load router adress {}".format(self.address))
        else:
            response_json = create_new_router(self.wallet, self.private_key, self.initial_value)
            tx_hash = response_json["tx_hash"]
            if tx_hash is None:
                print("something goes wrong when creating router ;(")
            else:
                self.address = web3.eth.getTransactionReceipt(tx_hash).logs[0].args.contractAddress
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
        return self.address

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
            if contract.last_connect_time == -1:
                continue
            if (time.time() - contract.last_connect_time) > self.timeout:
                print('contract delete by timeout {}'.format(contract.client_mac))

                if self.close_contract(contract): #TODO if contract not approved?
                    self.contracts.remove(contract)
            i -= 1

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
        msg = close_session(self.address, self.wallet, self.private_key, contract.id, contract.used_traffic)

        if not msg['success']:
            print("I can't close session", contract.id)
            return False

        self.mac_address_white_list.remove(contract.client_mac)
        return True

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
    return 'install wafer client!'


@app.route('/request')
def request_auth():
    router = app.config['router']

    #req = request.get_json(force=True)
    req = request.args
    if 'mac' not in req:
        return "Mac not found in request", 500

    mac = int(req['mac'])
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
    #req = request.get_json(force=True)
    req = request.args

    if 'mac' not in req:
        return "Mac not found in request", 500
    mac = int(req['mac'])

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
    router = Router("83c14ddb845e629975e138a5c28ad5a72a49252ea65b3d3ec99810c82751cc3a",
                    "0xaec3ae5d2be00bfc91597d7a1b2c43818d84396a")
    app.config['router'] = router
    contracts_state_checker = RepeatedTimer(30, router.check_contracts_state)
    contracts_sessions_checker = RepeatedTimer(30, router.check_contracts_timeout)
    app.run(debug=True, host='0.0.0.0', use_reloader=False)

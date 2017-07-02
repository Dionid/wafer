pragma solidity ^0.4.0;


contract Router {

    /*
    Every router in the system have it's Router contract. In order to get traffic,
    client have to send fixed for each contract initial payment. After payment
    router should start sharing wi-fi with contributor on conditions they've
    discussed without block chain. This conditions may be cost per mb, so we need
    to be able to return a part of initial paymen to contributor. To solve this problem,
    router need to call closeSession. This function will initialize process of payment
    from contract to router and contributor in proportions, given by router. This process
    will public propotions, and after some delay router will be able to call
    makeDelayedPayment to complete payment. If contributor do not agree with propotions,
    he can call complaint on particular session. This will send customers part of money,
    but leave router's part on contract. Also this option can be used before
    initialasin session closing, in this case nobody will resive money.

    */

    address routerAddress;
    uint initialCredit;
    uint constant paymentDelay = 86400;

    mapping (uint => address) private clientOpenAdresses;
    mapping (uint => address) private clientClosingAdresses;
    mapping (uint => uint) private closingTime;
    mapping (uint => bool) private usedIds;
    mapping (uint => uint) public closingMoney;


    event sessionCreationEvent(address clientAdress, uint identificator);
    event sessionClosingEvent(address clientAdress, uint identificator);
    event complaintEvent(address clientAdress, uint identificator);
    event contractCreatoinEvent(address routerAddress, uint initialCredit);


    modifier onlyRouter() {
        require(msg.sender == routerAddress);
        _;
    }

    function Router(address _routerAddress, uint _initialCredit) {
        routerAddress = _routerAddress;
        initialCredit = _initialCredit;
        contractCreatoinEvent(routerAddress, initialCredit);
    }


    function getAddress() returns (address){
        return this;
    }


    function newSession(uint identificator) payable {
        require(msg.value == initialCredit);
        require(usedIds[identificator] == false);
        clientOpenAdresses[identificator] = msg.sender;

        sessionCreationEvent(msg.sender, identificator);
    }


    function closeSession(uint identificator, uint moneyForRouter) onlyRouter {
        require(moneyForRouter <= initialCredit);
        closingMoney[identificator] = moneyForRouter;
        clientClosingAdresses[identificator] = clientOpenAdresses[identificator];
        delete clientOpenAdresses[identificator];
        closingTime[identificator] = block.timestamp;

        sessionClosingEvent(msg.sender, identificator);
    }

    function complaint(uint identificator) {
        //require(usedIds[identificator] == true);
        require(clientClosingAdresses[identificator] == msg.sender);

        address clientAdress = clientClosingAdresses[identificator];
        clientAdress.send(initialCredit - closingMoney[identificator]);

        delete clientOpenAdresses[identificator];
        delete clientClosingAdresses[identificator];
        delete usedIds[identificator];
        delete closingTime[identificator];
        delete closingMoney[identificator];

        complaintEvent(msg.sender, identificator);
    }


    function makeDelayedPayment(uint identificator) onlyRouter {
        require(usedIds[identificator] == true);
        require(block.timestamp - closingTime[identificator] >= paymentDelay);
        require(clientClosingAdresses[identificator] != 0);

        address clientAdress = clientClosingAdresses[identificator];

        routerAddress.send(closingMoney[identificator]);
        clientAdress.send(initialCredit - closingMoney[identificator]);

        delete clientClosingAdresses[identificator];
        delete usedIds[identificator];
        delete closingTime[identificator];
        delete closingMoney[identificator];

    }



}

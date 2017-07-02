pragma solidity ^0.4.0;


contract Router {
   
    address routerAddress;
    uint initialCredit;
    uint constant paymentDelay = 86400;
   
    mapping (uint => address) private clientOpenAdresses;
    mapping (uint => address) private clientClosingAdresses;
    mapping (uint => uint) private closingTime;
    mapping (uint => bool) private usedIds;
    mapping (uint => uint) private closingMoney;
   
   
    event sessionCreationEvent(address clientAdress, address routerAddress , uint identificator);
    event sessionClosingEvent(address clientAdress, uint identificator);
    event complaintEvent(address clientAdress, uint identificator);
    event contractCreatoin(address routerAddress, uint initialCredit);
   
   
    modifier onlyRouter() {
        require(msg.sender == routerAddress);
        _;
    }
   
    function Router(address _routerAddress, uint _initialCredit) {
        routerAddress = _routerAddress;
        initialCredit = _initialCredit;
        contractCreatoin(routerAddress, initialCredit);
    }
   
 
   
    function getAddress() returns (address){
        return this;
    }
   
    function newSession(uint identificator) payable {
        require(msg.value == initialCredit);
        require(usedIds[identificator] == false);
        clientOpenAdresses[identificator] = msg.sender;
       
        sessionCreationEvent(msg.sender,routerAddress, identificator);
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
        require(usedIds[identificator] == true);
        require(clientClosingAdresses[identificator] == msg.sender);
        delete clientClosingAdresses[identificator];
        delete usedIds[identificator];
        delete closingTime[identificator];
       
        complaintEvent(msg.sender, identificator);
    }
   
   
    function makeDelayedPayment(uint identificator)  {
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
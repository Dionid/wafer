pragma solidity ^0.4.0;

import "./Router.sol";

contract RouterFabric {
    /*
    Fabric for contract creation. In order to join system, router should  call
    createNewRouter with the only argument corresponding to initial client's
    deposit to start new session.
    */


    event newRouterEvent(address routerAddress, address contractAddress, uint credit);

    function createNewRouter(uint credit) {
        Router newRouter = new Router(msg.sender, credit);
        address contractAddress = newRouter.getAddress();

        newRouterEvent(msg.sender, contractAddress, credit);
    }


}

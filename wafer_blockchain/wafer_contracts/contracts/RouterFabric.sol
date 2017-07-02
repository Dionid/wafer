pragma solidity ^0.4.0;

import "./Router.sol";

contract RouterFabric {
    event newRouterEvent(address routerAddress, address contractAddress, uint credit);
   
    function createNewRouter(uint credit) public returns (address){
        Router newRouter = new Router(msg.sender, credit);
        address contractAddress = newRouter.getAddress();
       
        newRouterEvent(msg.sender, contractAddress, credit);
       
        return contractAddress;
    }
 
}
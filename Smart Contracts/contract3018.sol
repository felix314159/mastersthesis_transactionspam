// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// spam BALANCE
contract Contract {
	
	function main() public view {
		
		uint gas_left = gasleft();
        while (gas_left > 9000)
        {
        	
        	// convert gasleft uint to address
            address _addr = address(uint160(gas_left));
               
			// get balance of this address
			_addr.balance;

			gas_left = gasleft(); 
		} 
        
	}
	
}


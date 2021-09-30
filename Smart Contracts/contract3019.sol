// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// spam EXTCODEHASH
contract Contract {
	
	function main() public view {
		
		uint gas_left = gasleft();
        while (gas_left > 9000)
        {
        	// convert gasleft uint to address
            address _addr = address(uint160(gas_left));
               
			// extcodehash (return hash of given address code, if addr is not contract -> returns 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470, if acc has not been used -> returns 0x0
 			assembly { 
				let hash := extcodehash(_addr) 
				
			}
            
            gas_left = gasleft(); 
		}
        
	}
}


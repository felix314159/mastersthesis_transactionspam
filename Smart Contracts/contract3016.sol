// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// repeatedly spam EXTCODESIZE operation, generate addresses using gasLeft
// crashes remix when calling main() function
contract Contract {
	
	function main() public view  {
	    uint gas_left = gasleft();

        while (gas_left > 9000)
        {
	
        	address _addr = address(uint160(gas_left));
            
            assembly {
                let size := extcodesize(_addr)

            }
			// update gas_left so that while loop ends when gas is too low to execute another iteration
            gas_left = gasleft(); 
		}
        
	}

}

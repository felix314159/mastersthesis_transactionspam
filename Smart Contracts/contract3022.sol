// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// spam CALL
contract Contract {
	
	function main() public {
		
		uint gas_left = gasleft();
        while (gas_left > 5000)
        {
        		// convert uint from gasleft to bytes using abi.encodePacked
                bytes memory gas_value = abi.encodePacked(gas_left);

                // form valid address by extracting 20 bytes from gas
                address _addr;
				assembly {
					_addr := mload(add(gas_value, 20))
				}

				// spam CALL
				_addr.call(gas_value);

                // update gas_left value
		    	gas_left = gasleft(); 

		}
        
	}

}


// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// uses gasleft to generate addresses which i use for spamming EXTCODECOPY
contract Contract {
    
	function main() public view {
		uint gas_left = gasleft();
        while (gas_left > 9000)
        {

        	// convert gasleft uint to address
            address _addr = address(uint160(gas_left));
            
            // now use extcodecopy with that address
            function_extcodecopy(_addr);
                
		    gas_left = gasleft(); 
		} 
        
	}
    
    // source of this function: https://ethereum.stackexchange.com/questions/1906/can-a-contract-access-the-code-of-another-contract (answer of ETH)
	// Accessed (June 17, 2021)
    function function_extcodecopy(address _addr) public view returns (bytes memory o_code) {
        assembly {
            let size := extcodesize(_addr)
            o_code := mload(0x40)
            mstore(0x40, add(o_code, and(add(add(size, 0x20), 0x1f), not(0x1f))))
            mstore(o_code, size)
            extcodecopy(_addr, add(o_code, 0x20), 0, size)
        }
    }
	

}


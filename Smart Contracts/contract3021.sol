// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// spam SLOAD

contract Contract {
	constructor() {
        main();   
    }
	
	function main() public view  {
	    uint gas_left = gasleft();

         for (uint i=0; i<80000; i++) {
		 	if (gasleft() > 25000) {
				// spam sload: i is storage key, 1 is storage slot
				assembly {
				    mstore(0, i)
				    mstore(32, 1)
				    let kec_hash := keccak256(0, 64)
				    let final := sload(kec_hash)
				} 

				// update gas_left so that while loop ends when gas is too low to execute another iteration
		        gas_left = gasleft(); 
			}
			else {
				break;
			}
		}
	}

}


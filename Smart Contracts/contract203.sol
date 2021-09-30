// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// this contract is based on the idea to bloat the state of the blockchain by sending ETH to many different addresses

contract Contract {
		// idea: use loop to increase number, hash the number, cut hash length down to address length and then use this address to create non-empty accounts by sending small amounts of wei to them
	constructor() payable {
        main();   
    }
	
	function main() public payable {
        // every deployment of this contract sends 1 wei to 400 addresses, you manually have to adjust the intervals though (0-400, 400-800, etc)
        for (uint i=0; i<400; i++) {
		    if (gasleft() > 10000) {
		        
		        // convert uint256 to bytes memory
		        bytes memory bytes_val = new bytes(32);
                assembly {
                    mstore(add(bytes_val, 32), i) 
                    
                }
		        
        		// hash the value, then store as bytes32
        		bytes32 seed = keccak256(bytes_val);
        
        		// convert bytes32 to a payable address
        		address payable addr = payable(address(uint160(uint256(seed))));
        			
        		// now send small amount of wei to this address
        		// when testing with remix, remember to set "value" in remix to atleast 1 (since this is a payable contract)
        		addr.transfer(1);
		    }
		
			// break when gas is too low for more iterations
		    else {
		        break;
		    }
		    
        }
	}

}


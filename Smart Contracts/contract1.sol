// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

// this is just an example contract where I tested if the python code works and I tested how events work in Solidity

// this contracts code is a slightly modified version of the contract found here https://github.com/ethereum/ethereum-org/blob/master/views/content/greeter.md (Accessed June 1, 2021)
contract Contract {
	string public greeting;
	event greet_event(string asdf);
	event constructor_event(string asdf);

	constructor() {
        	greeting = 'Hello World!';
			string memory creation_message = "Contract has been deployed successfully :)";
			emit constructor_event(creation_message);
    }

    function setGreeting(string memory _greeting) public {
    	greeting = _greeting;
    }

    function greet() public returns (string memory) {
        string memory log_message = "greet function has been called :)";
		emit greet_event(log_message);
        return greeting;
    }
}

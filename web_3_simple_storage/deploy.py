import json
from web3 import Web3
from solcx import compile_standard, install_solc


with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    install_solc("0.6.0")

    # Solidity source code
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evm.bytecode",
                            "evm.bytecode.sourceMap",
                        ]
                    }
                }
            },
        },
        solc_version="0.6.0",
    )

    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    # get bytecode to deploy  this is walking down the compiled_code json contracts/simpleStorage.sol/simplestorage/evm

    # get bytecode
    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]

    # get abi

    abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
    # for connecting to ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    chain_id = 1337
    my_address = "0x6a8dC9455DE3aCc588bfAA4AEf9d51a81D055e50"
    private_key = "f213e8c020d6584e92b38ab83bf90803f7dd1b70c0702afedc71e828ca10fefb"

    # Create the contract in python
    SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the latest transaction
    nonce = w3.eth.getTransactionCount(my_address)
    print(nonce)
    # Submit the transaction that deploys the contract
    transaction = SimpleStorage.constructor().buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
        }
    )
    print(transaction)

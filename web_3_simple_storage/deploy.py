import json
from web3 import Web3
from solcx import compile_standard, install_solc

import os

from dotenv import load_dotenv

load_dotenv()


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
    w3 = Web3(
        Web3.HTTPProvider(
            "https://rinkeby.infura.io/v3/e9d3fa03c3e84a2e96ebdf45916b39f7"
        )
    )
    chain_id = 4
    my_address = "0xae5452452eab048E5A7319AAbeD2D101Ec4f5745"
    private_key = os.getenv("PRIVATE_KEY")

    # Create the contract in python
    SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the latest transaction
    nonce = w3.eth.getTransactionCount(my_address)
    # print(nonce)
    # Submit the transaction that deploys the contract
    transaction = SimpleStorage.constructor().buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
        }
    )

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    # print(signed_txn)
    # Send this signed transaction
    print("Deploying Contract")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Deployed Contract")
    # Working with the contract, you always need
    # Contract Address
    # Contract ABI

    simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    # call -> simulate making the call anding getting return a value
    # transact -> actual state change
    print(simple_storage.functions.retrieve().call())
    print("Updating Contract")
    # print(simple_storage.functions.store(15).call())
    # create
    store_transaction = simple_storage.functions.store(15).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce + 1,
        }
    )
    # sign
    signed_store_txn = w3.eth.account.sign_transaction(
        store_transaction, private_key=private_key
    )
    # send
    send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
    # recipet wait to finsh
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
    print("updated")
    print(simple_storage.functions.retrieve().call())

import asyncio
import json

import forta_agent
from forta_agent import get_json_rpc_url
from web3 import Web3
from src.findings import UUPSUpgradeableFindings
from src.utils import extract_argument, can_be_selfdestructed

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
with open("./src/abi.json", 'r') as abi_file:  # get abi from the file
    abi = json.load(abi_file)

# "OwnershipTransferred(address,address)" in the json format
ownership_transferred_abi = next((x for x in abi if x.get('name', "") == "OwnershipTransferred"), None)
# "Upgraded(address)" in the json format
upgraded_abi = next((x for x in abi if x.get('name', "") == "Upgraded"), None)
# "owner()" function in the json format
owner_abi = next((x for x in abi if x.get('name', "") == "owner"), None)


async def detect_logic_contract_not_initialized(transaction_event: forta_agent.transaction_event.TransactionEvent, w3):
    """
    This function detects delegatecall that target address has an owner with an address
    0x0000000000000000000000000000000000000000
    :param transaction_event: forta_agent.transaction_event.TransactionEvent
    :param w3: web3 object, it was added here to be able to insert web3 mock and test the function
    :return: findings: list
    """
    findings = []
    for trace in transaction_event.traces:  # get the traces from the transaction events
        if trace.type == "delegatecall":  # get delegatecall trace
            target_address = trace.action.to  # get the address for which call was delegated
            contract = w3.eth.contract(address=Web3.toChecksumAddress(target_address), abi=[owner_abi])
            # alert if an owner of this address is "0x0000000000000000000000000000000000000000" that means contract is
            if contract.functions.owner().call(  # not initialized
                    transaction_event.block_number) == "0x0000000000000000000000000000000000000000":
                findings.append(await
                                UUPSUpgradeableFindings.contract_not_initialized_finding(transaction_event.hash,
                                                                                         target_address,
                                                                                         trace.action.from_))
    return findings


async def detect_contract_initialized(transaction_event: forta_agent.transaction_event.TransactionEvent):
    """
    This function detect "OwnershipTransferred(address,address)" and provides alert if previous owner has address
    0x0000000000000000000000000000000000000000
    :param transaction_event: forta_agent.transaction_event.TransactionEvent
    :return: findings: list
    """
    findings = []
    # get "OwnershipTransferred(address,address)" events
    for event in transaction_event.filter_log(json.dumps(ownership_transferred_abi)):
        old_owner = await extract_argument(event, 'previousOwner')  # get the previous owner
        # alert if the previous owner is 0x0000000000000000000000000000000000000000 that means contract was initialized
        if old_owner == "0x0000000000000000000000000000000000000000":
            findings.append(
                await UUPSUpgradeableFindings.contract_was_initialized_finding(transaction_event.hash,
                                                                               await extract_argument(event,
                                                                                                      "newOwner"),
                                                                               transaction_event.to))
    return findings


async def detect_main_exploit(transaction_event: forta_agent.transaction_event.TransactionEvent, w3):
    """
    This function detects when an attacker could trigger a selfdestruct of a UUPS implementation contract, leaving
    a proxy contract permanently broken.
    :param transaction_event: forta_agent.transaction_event.TransactionEvent
    :param w3: web3 object, it was added here to be able to insert web3 mock and test the function
    :return: findings: list
    """
    findings = []

    for event in transaction_event.filter_log(json.dumps(upgraded_abi)):  # get "Upgraded(address)" events
        new_implementation = await extract_argument(event, "implementation")  # extract the new implementation address
        contact_code = w3.eth.get_code(Web3.toChecksumAddress(new_implementation),  # get its byte-code
                                       block_identifier=transaction_event.block_number)
        if not contact_code:  # alert if the byte-code is empty
            findings.append(await UUPSUpgradeableFindings.main_exploit_finding(transaction_event.hash,
                                                                               new_implementation,
                                                                               transaction_event.from_))
        elif await can_be_selfdestructed(contact_code):  # else check is selfdestruct method reachable in the byte-code
            findings.append(await
                            UUPSUpgradeableFindings.new_logic_contract_can_be_selfdestructed_finding(
                                transaction_event.hash,
                                new_implementation))
    return findings


async def main(transaction_event: forta_agent.transaction_event.TransactionEvent, w3):
    """
    This function is used to start detect-functions in the different threads and then gather the findings
    """
    return await asyncio.gather(
        detect_logic_contract_not_initialized(transaction_event, w3),
        detect_contract_initialized(transaction_event),
        detect_main_exploit(transaction_event, w3)
    )


def provide_handle_transaction(w3):
    def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent) -> list:
        return [finding for findings in asyncio.run(main(transaction_event, w3)) for finding in findings]

    return handle_transaction


real_handle_transaction = provide_handle_transaction(web3)


def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent):
    return real_handle_transaction(transaction_event)
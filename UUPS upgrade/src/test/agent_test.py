import eth_abi
from eth_utils import keccak, encode_hex
from forta_agent import create_transaction_event, get_json_rpc_url, FindingSeverity, FindingType
from src.agent import provide_handle_transaction
from src.test.web3_mock import Web3Mock
from web3 import Web3

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))

upgraded = "Upgraded(address)"
ownership_transferred = "OwnershipTransferred(address,address)"
OLD_OWNER_NOT_INITED = "0x0000000000000000000000000000000000000000"
NEW_IMPLEMENTATION_ADDRESS = "0x1111111111111111111111111111111111111111"
CONTRACT_ADDRESS = "0x2222222222222222222222222222222222222222"
NEW_OWNER = "0x3333333333333333333333333333333333333333"
MALICIOUS_SENDER = "0x4444444444444444444444444444444444444444"
DESTRUCTED_CONTRACT_CODE = b''
CONTRACT_CAN_BE_SELFDESTRUCTED = '0x1111111254fb6c44bAC0beD2854e76F90643097d'
CODE_WITH_SELFDESTRUCT = web3.eth.get_code(Web3.toChecksumAddress(CONTRACT_CAN_BE_SELFDESTRUCTED))
CONTRACT_CAN_NOT_BE_SELFDESTRUCTED = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b'
CODE_WITHOUT_SELFDESTRUCT = web3.eth.get_code(Web3.toChecksumAddress(CONTRACT_CAN_NOT_BE_SELFDESTRUCTED))

# ----------------------------- Upgraded(address) MOCK ----------------------------- #
hash = keccak(text=upgraded)
data = eth_abi.encode_abi([], [])
data = encode_hex(data)
implementation = eth_abi.encode_abi(["address"], [NEW_IMPLEMENTATION_ADDRESS])
implementation = encode_hex(implementation)
topics = [hash, implementation]
log_upgraded = {'topics': topics,
                'data': data,
                'address': CONTRACT_ADDRESS}

# -------------------- OwnershipTransferred(address,address) MOCK -------------------- #
hash = keccak(text=ownership_transferred)
data = eth_abi.encode_abi([], [])
data = encode_hex(data)
previousOwner = eth_abi.encode_abi(["address"], [OLD_OWNER_NOT_INITED])
previousOwner = encode_hex(previousOwner)
newOwner = eth_abi.encode_abi(["address"], [NEW_OWNER])
newOwner = encode_hex(newOwner)
topics = [hash, previousOwner, newOwner]
log_ownership_transferred = {'topics': topics,
                             'data': data,
                             'address': CONTRACT_ADDRESS}


class TestUUPSUpgradeableAgent:

    def test_returns_main_exploit_finding(self):
        w3 = Web3Mock(MALICIOUS_SENDER, DESTRUCTED_CONTRACT_CODE)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0"
            },
            'block': {
                'number': 0
            },
            'receipt': {
                'logs': [log_upgraded]}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        finding = next((x for x in findings if x.alert_id == 'UUPS-EXPLOIT'), None)
        assert finding
        assert finding.description == 'New logic contact was self-destructed'
        assert finding.severity == FindingSeverity.Critical
        assert finding.type == FindingType.Exploit
        assert finding.metadata.get('tx_hash') == "0"
        assert finding.metadata.get('new_implementation') == NEW_IMPLEMENTATION_ADDRESS
        assert finding.metadata.get('attacker_address') == MALICIOUS_SENDER

    def test_returns_finding_if_logic_contract_not_initialized(self):
        w3 = Web3Mock(OLD_OWNER_NOT_INITED, DESTRUCTED_CONTRACT_CODE)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0",
                'to': CONTRACT_ADDRESS
            },
            'block': {
                'number': 0
            },
            'traces': [
                {'type': 'delegatecall',
                 'action': {
                     'to': CONTRACT_ADDRESS,
                     'from': CONTRACT_ADDRESS
                 }
                 }
            ],
            'receipt': {
                'logs': []}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        finding = next((x for x in findings if x.alert_id == 'LOGIC-NOT-INIT'), None)
        assert finding
        assert finding.description == 'It looks like Proxy delegated call to the not initialized logic contract'
        assert finding.severity == FindingSeverity.High
        assert finding.type == FindingType.Unknown
        assert finding.metadata.get('tx_hash') == "0"
        assert finding.metadata.get('contract') == CONTRACT_ADDRESS
        assert finding.metadata.get('proxy') == CONTRACT_ADDRESS

    def test_returns_finding_if_new_logic_contract_can_be_selfdestructed(self):
        w3 = Web3Mock(OLD_OWNER_NOT_INITED, CODE_WITH_SELFDESTRUCT)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0",
            },
            'block': {
                'number': 0
            },
            'receipt': {
                'logs': [log_upgraded]}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        finding = next((x for x in findings if x.alert_id == 'LOGIC-CAN-SELFDESTRUCT'), None)
        assert finding
        assert finding.description == 'selfdestruct method found in the new logic contract bytecode'
        assert finding.severity == FindingSeverity.High
        assert finding.type == FindingType.Unknown
        assert finding.metadata.get('tx_hash') == "0"
        assert finding.metadata.get('new_implementation') == NEW_IMPLEMENTATION_ADDRESS

    def test_returns_finding_if_contract_was_initialized(self):
        w3 = Web3Mock(OLD_OWNER_NOT_INITED, DESTRUCTED_CONTRACT_CODE)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0",
                'to': CONTRACT_ADDRESS
            },
            'block': {
                'number': 0
            },
            'receipt': {
                'logs': [log_ownership_transferred]}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        finding = next((x for x in findings if x.alert_id == 'CONTRACT-INIT'), None)
        assert finding
        assert finding.description == f'Contract {CONTRACT_ADDRESS} was initialized'
        assert finding.severity == FindingSeverity.Medium
        assert finding.type == FindingType.Info
        assert finding.metadata.get('tx_hash') == "0"
        assert finding.metadata.get('new_owner') == NEW_OWNER
        assert finding.metadata.get('contract') == CONTRACT_ADDRESS

    def test_returns_zero_finding_if_upgraded_event_is_correct_and_code_cant_selfdestruct(self):
        w3 = Web3Mock(OLD_OWNER_NOT_INITED, CODE_WITHOUT_SELFDESTRUCT)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0",
            },
            'block': {
                'number': 0
            },
            'receipt': {
                'logs': [log_upgraded]}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        assert not findings

    def test_returns_zero_finding_if_logic_contract_is_initialized_already(self):
        w3 = Web3Mock(NEW_OWNER, DESTRUCTED_CONTRACT_CODE)
        tx_event = create_transaction_event({
            'transaction': {
                'from': MALICIOUS_SENDER,
                'hash': "0",

            },
            'block': {
                'number': 0
            },
            'traces': [
                {'type': 'delegatecall',
                 'action': {
                     'to': CONTRACT_ADDRESS
                 }
                 }
            ],
            'receipt': {
                'logs': []}
        })

        findings = provide_handle_transaction(w3)(tx_event)
        assert not findings
from forta_agent import FindingSeverity, FindingType, create_transaction_event, Transaction, TransactionEvent
from agent import handle_transaction

# 2018-01-15-T-04-30-14-930Z
# https://etherscan.io/tx/0xce1cf623814118aae3e1caaac7bb409fcdd1e48f0794e11b86500260e13d6bb4
MESSAGE_1 = '0x323031382d30312d31352d542d30342d33302d31342d3933305a'

# you are such a looser for making scam contracts lmao hope you burn in hell one day jeet
# https://etherscan.io/tx/0x4989fa9d76a0f1a54236e6fb59823827ce98e063047b909308ed7552a739fef0
MESSAGE_2 = '0x796f752061726520737563682061206c6f6f73657220666f72206d616b696e67207363616d20636f6e747261637473206c6d616f20686f706520796f75206275726e20696e2068656c6c206f6e6520646179206a656574'

TX_HASH = "0x4989fa9d76a0f1a54236e6fb59823827ce98e063047b909308ed7552a739fef0"
ZERO_ETHER = "0x0"
NOT_EQUAL_TO_ZERO = "0x2bc6cb30ec2000"

# CALL CONTRACT DATA
# https://etherscan.io/tx/0xfba4c700815a9fee055889b06ec00b1b3fb89ed3c4a33a3bba2e32711c757dc0
CALL_CONTRACT_DATA = "0xe63d38ed000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000001000000000000000000000000e4c808592a4f60b09350c20151b5f17ee2437564000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000470de4df820000"

EMPTY_MESSAGE = "0x20"

MESSAGE_3 = "0x00500072006500700061007200650064002000620079002000630072007900700074006f0061007000690073002e0069006f"

LOW_MESSAGE = '0x496e206163636f7264616e636520776974682074686520552e532e205472616e736d697474616c206f662046756e647320526567756c6174696f6e732c2074686520201c54726176656c2052756c65201d2c2074686520726563656976696e6720696e737469747574696f6e206d617920636f6e7461637420636d6f727120696e632e20776974682061207265717565737420746f2072656365697665207468652066756c6c207472616e736d697474616c206f726465722e20546f20636f6e7461637420636d6f727120796f75206d75737420312e2062652074686520726563656976696e6720696e737469747574696f6e2c20322e20626520796f757220696e737469747574696f6e2019732033313428622920636f6e7461637420706572736f6e2c20332e20656d61696c20636f6d706c69616e636540636d6f72712e636f6d2c20342e2070726f7669646520796f7572203331342862292d726567697374726174696f6e206c65747465722066726f6d2046696e43454e2e0d0a636d6f727120197320436f6d706c69616e6365204f6666696365722077696c6c2076657269667920796f7572206964656e74697479206469726563746c7920616e642070726f7669646520696e737472756374696f6e7320666f7220726563656976696e6720746865207472616e736d697474616c206f7264657220666f7220616e79207472616e73616374696f6e206861736865732070726f76696465642e205472616e736d697474616c206f72646572732077696c6c206f6e6c792062652070726f766964656420746f20552e532e20656e7469746965732e205375636820696e666f726d6174696f6e206d6179206f6e6c792062652070726f766964656420746f20637573746f6469616c2077616c6c65742070726f7669646572732077686f20686176652072656365697665642061207472616e73666572206469726563746c792066726f6d20636d6f727120696e632e'
HIGH_MESSAGE = '0x4e69636520776f726b2e20416e79206368616e636520796f75206361726520746f2072657475726e2068616c66206f66207468652073746f6c656e2066756e64733f'
FANTOM_MSG = '0x57386225'

EMPTY_MESSAGE_V2 = '0x0000000000000000000000000000000000000000'

ONE_ADDRESS = "0x1111111111111111111111111111111111111111"
TWO_ADDRESS = "0x2222222222222222222222222222222222222222"

ALERT_ID_FOR_HIGH = 'forta-text-messages-possible-hack'
ALERT_ID_FOR_LOW = 'forta-text-messages-agent'


class TestMessagesAgent:

    def test_returns_empty_findings_if_logs_not_empty(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0"
            },
            'receipt': {
                'logs': [{

                }]}})

        findings = handle_transaction(tx_event)
        print(findings)
        assert len(findings) == 0

    def test_returns_empty_findings_if_sent_empty_data(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0",
                'value': NOT_EQUAL_TO_ZERO
            },
            'receipt': {
                'logs': []}})

        findings = handle_transaction(tx_event)
        print(findings)
        assert len(findings) == 0

    def test_returns_empty_findings_if_sent_empty_msg(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0",
                'value': ZERO_ETHER,
                'data': EMPTY_MESSAGE_V2
            },
            'receipt': {
                'logs': []}})

        findings = handle_transaction(tx_event)
        print(findings)
        assert len(findings) == 0

    def test_returns_empty_findings_if_not_utf_data(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0",
                'value': ZERO_ETHER,
                'data': CALL_CONTRACT_DATA
            },
            'receipt': {
                'logs': []}})

        findings = handle_transaction(tx_event)
        assert len(findings) == 0

    def test_returns_empty_findings_if_exist_forbidden_symbol_keywords(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0",
                'value': NOT_EQUAL_TO_ZERO,
                'data': '0x44432d4c353a5946676d6c74756549434c6d4d345a5878596c45756f36536d4d786b51316a3739527439777573776737413d'
            },
            'receipt': {
                'logs': []}})

        findings = handle_transaction(tx_event)

        assert len(findings) == 0

    def test_returns_severity_high_findings(self):
        tx_event = create_transaction_event({
            'transaction': {
                'from': ONE_ADDRESS,
                'to': TWO_ADDRESS,
                'hash': "0",
                'value': NOT_EQUAL_TO_ZERO,
                'data': HIGH_MESSAGE
            },
            'receipt': {
                'logs': []}})

        findings = handle_transaction(tx_event)

        assert len(findings) == 1
        finding = findings[0]
        assert finding.severity == FindingSeverity.High
        assert finding.alert_id == ALERT_ID_FOR_HIGH

from forta_agent import Finding, FindingType, FindingSeverity, get_web3_provider
import forta_agent
import re

EMPTY_DATA = '0x'
EMPTY_MESSAGE = ['0x0000000000000000000000000000000000000000',
                 '0x0000000000000000000000000000000000000000000000000000000000000000']
REVERTRED = 'Reverted'
ZERO_VALUE = 0
MIN_TEXT_LEN = 5
MAX_NUM_OF_DIGITS_IN_MSG = 0.2
MAX_EMPTY_SYMBOL_IN_MSG = 0.3

stop_symbol = ['&', '%', '}', '{', '>', '<', '|', '[', '^', ')', 'Ҿ', '⻱', '΢',
               '', 'Ĭ', '', '', '', '', 'ҁ', 'ˣ', '', '', '', '', '޺', '', '',
               '', '', '', '', '', '']

words = ["stolen", "steal", "stole", "stealing", "looser", "scam", "lmao", "nitwit", "fuck", "suck", "fucking", "cunt",
         "bullshit",
         "bitch", "gay", "ass", "bastard", "faggot", "shit", "stupid", "asshole", "virgin", "penis", "exploit",
         "exploiter", "hijack", "seize", "robber", "captor", "kidnap", "abduct", "abductor", "abducting", "burglar",
         "thief", "kidnapper", "pilferer", "rogue", "scoundrel", "brat", "yobbo", "blighter", "stinker",
         "vermin", "conman", "fraud", "crud", "whore", "hussy",
         "exploitation", "exploiter", "exploiting", "exploited", "exploitative", "exploitable", "hacker", "hack",
         "hacked", "hacker", "hacking", "cheated", "cheating", "cheat", "whale", "fishing", "attack", "attackable",
         "attacking", "attacker", "attacked", ]

ALERT_ID_FOR_HIGH = 'forta-text-messages-possible-hack'
ALERT_ID_FOR_LOW = 'forta-text-messages-agent'


def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent):
    findings = []

    # The contract was called. This doesn't fit
    if len(transaction_event.logs) > 0:
        return findings

    # empty data
    if transaction_event.transaction.data is None or transaction_event.transaction.data == EMPTY_DATA or \
            transaction_event.transaction.data in EMPTY_MESSAGE:
        return findings

    text_msg = tx_data_to_text(transaction_event.transaction.data)

    if text_msg is None or text_msg == "" or len(text_msg) < MIN_TEXT_LEN or text_msg is not None and (
            check_forbidden_symbol(
                text_msg) or not msg_is_text(text_msg)):
        return findings

    severity = get_severity(text_msg)

    findings.append(Finding({
        'name': 'A text message has been sent',
        'description': text_msg,
        'alert_id': ALERT_ID_FOR_HIGH if severity == FindingSeverity.High else ALERT_ID_FOR_LOW,
        'type': FindingType.Info,
        'severity': severity,
    }))

    return findings


def get_severity(text_msg):
    for word in words:
        if word in text_msg:
            return FindingSeverity.High
        else:
            continue

    return FindingSeverity.Low


def check_forbidden_symbol(text_msg):
    msg_in_bytes = text_msg.encode('ascii')
    empty_symbol_count = sum(1 for c in msg_in_bytes if c == 0)

    if empty_symbol_count / len(msg_in_bytes) > MAX_EMPTY_SYMBOL_IN_MSG:
        return True

    for word in stop_symbol:
        if word in text_msg:
            return True
        else:
            continue

    return False


# if the percentage of digits in the message is greater than a certain value, then this is not a text message.
def msg_is_text(text_msg):
    length_of_numeric = 0
    space_count = 0

    for t in re.findall('[0-9]+', text_msg):
        length_of_numeric += len(t)

    for t in re.findall(r'\s', text_msg):
        space_count += len(t)

    # 1001-707212
    # DC-L5:YFgmltueICLmM4ZXxYlEuo6SmMxkQ1j79Rt9wuswg7A=
    if length_of_numeric / len(text_msg) > MAX_NUM_OF_DIGITS_IN_MSG or space_count == 0 and len(text_msg) > 10:
        return False

    return True


def tx_data_to_text(data):
    try:
        web3_provider = get_web3_provider()
        return web3_provider.toText(data).strip()
    except:
        return None

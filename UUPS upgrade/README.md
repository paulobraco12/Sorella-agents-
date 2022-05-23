This agent detects when an attacker could trigger a selfdestruct of a UUPS implementation contract, leaving a proxy contract permanently broken. The agent is separated into three threads:

First thread detects contracts that are not initialized.
Second thread detects the main exploit and tries to anticipate it - if new contract logic exists but selfdestruct method is reachable in the byte-code - this thread will provide the alert too.
Third thread detects when a contract is initialized by TransferOwnership event where the previous owner was 0x0000000000000000000000000000000000000000

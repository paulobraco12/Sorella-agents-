const { Finding, FindingSeverity, FindingType } = require("forta-agent");

const ERC20_TRANSFER_EVENT =
  "event Transfer(address indexed from, address indexed to, uint256 value)";
const ETH_Adress = "0x2170ed0880ac9a755fd29b2688956bd959f933f8";
const ETH_DECIMALS = 6;
let findingsCount = 0;

const handleTransaction = async (TransactionEvent) => {
  const findings = [];
 

  // filter the transaction logs for ETH transfer events
  const ETHTransferEvents = TransactionEvent.filterLog(
    ERC20_TRANSFER_EVENT,
    ETH_Adress
  );

  ETHTransferEvents.forEach((TransferEvent) => {
    // extract transfer event arguments
    const { to, from, value } = TransferEvent.args;
    // shift decimals of transfer value
    const normalizedValue = value.div(10 ** ETH_DECIMALS);

    
    if (normalizedValue.gt(10000)) {
      findings.push(
        Finding.fromObject({
          name: "High Ethereum Transfer",
          description: `High amount of ETH transferred: ${normalizedValue}`,
          alertId: "FORTA-1",
          severity: FindingSeverity.Medium,
          type: FindingType.Info,
          metadata: {
            to,
            from,
          },
        })
      );
    }
  });

  return findings;
};

 const handleBlock = async (blockEvent) => {
   const findings = [];  // detect some block condition
  return findings;
 };

module.exports = {
  handleTransaction,
   handleBlock,
  ERC20_TRANSFER_EVENT, // exported for unit tests
  ETH_Adress, // exported for unit tests
  ETH_DECIMALS, // exported for unit tests
};

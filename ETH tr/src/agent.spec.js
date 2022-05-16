const {
  FindingType,
  FindingSeverity,
  Finding,
  createTransactionEvent,
  ethers,
} = require("forta-agent");
const {
  handleTransaction,
  ERC20_TRANSFER_EVENT,
  ETH_Adress,
  ETH_DECIMALS,
} = require("./agent");

describe("high ethereum transfer agent", () => {
  describe("handleTransaction", () => {
    const mockTxEvent = createTransactionEvent({});
    mockTxEvent.filterLog = jest.fn();

    beforeEach(() => {
      mockTxEvent.filterLog.mockReset();
    });

    it("returns empty findings if there are no ETH transfers", async () => {
      mockTxEvent.filterLog.mockReturnValue([]);

      const findings = await handleTransaction(mockTxEvent);

      expect(findings).toStrictEqual([]);
      expect(mockTxEvent.filterLog).toHaveBeenCalledTimes(1);
      expect(mockTxEvent.filterLog).toHaveBeenCalledWith(
        ERC20_TRANSFER_EVENT,
        ETH_Adress
      );
    });

    it("returns a finding if there is a Ethereum transfer over 10000", async () => {
      const mockETHTransferEvent = {
        args: {
          from: "0xabc",
          to: "0xdef",
          value: ethers.BigNumber.from("10000000000"), //10000  with 6 decimals
        },
      };
      mockTxEvent.filterLog.mockReturnValue([mockETHTransferEvent]);

      const findings = await handleTransaction(mockTxEvent);

      const normalizedValue = mockETHTransferEvent.args.value.div(
        10 ** ETH_DECIMALS
      );
      expect(findings).toStrictEqual([
        Finding.fromObject({
          name: "High Ethereum Transfer",
          description: `High amount of ETHtransferred: ${normalizedValue}`,
          alertId: "FORTA-1",
          severity: FindingSeverity.Medium,
          type: FindingType.Info,
          metadata: {
            to: mockETHTransferEvent.args.to,
            from: mockETHTransferEvent.args.from,
          },
        }),
      ]);
      expect(mockTxEvent.filterLog).toHaveBeenCalledTimes(1);
      expect(mockTxEvent.filterLog).toHaveBeenCalledWith(
        ERC20_TRANSFER_EVENT,
        ETH_Adress
      );
    });
  });
});

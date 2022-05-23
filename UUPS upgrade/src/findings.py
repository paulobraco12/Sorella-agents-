from forta_agent import Finding, FindingType, FindingSeverity


class UUPSUpgradeableFindings:

    @staticmethod
    async def main_exploit_finding(tx_hash: str, new_implementation: str,
                                   attacker_address: str) -> Finding:
        return Finding({
            'name': 'UUPSUpgradeable Exploit Alert',
            'description': f'New logic contact was self-destructed',
            'alert_id': 'UUPS-EXPLOIT',
            'type': FindingType.Exploit,
            'severity': FindingSeverity.Critical,
            'metadata': {
                'tx_hash': tx_hash,
                'new_implementation': new_implementation,
                'attacker_address': attacker_address,
            }
        })

    @staticmethod
    async def contract_not_initialized_finding(tx_hash: str, contract: str, proxy: str, ) -> Finding:
        return Finding({
            'name': 'Logic Contract Not Initialized',
            'description': f'It looks like Proxy delegated call to the not initialized logic contract',
            'alert_id': 'LOGIC-NOT-INIT',
            'type': FindingType.Unknown,
            'severity': FindingSeverity.High,
            'metadata': {
                'tx_hash': tx_hash,
                'contract': contract,
                'proxy': proxy,
            }
        })

    @staticmethod
    async def new_logic_contract_can_be_selfdestructed_finding(tx_hash: str,
                                                               new_implementation: str) -> Finding:
        return Finding({
            'name': 'New Logic Contract Can Be Self-Destructed',
            'description': f'selfdestruct method found in the new logic contract bytecode',
            'alert_id': 'LOGIC-CAN-SELFDESTRUCT',
            'type': FindingType.Unknown,
            'severity': FindingSeverity.High,
            'metadata': {
                'tx_hash': tx_hash,
                'new_implementation': new_implementation,
            }
        })

    @staticmethod
    async def contract_was_initialized_finding(tx_hash: str, new_owner: str, contract: str) -> Finding:
        return Finding({
            'name': 'Contract Was Initialized',
            'description': f'Contract {contract} was initialized',
            'alert_id': 'CONTRACT-INIT',
            'type': FindingType.Info,
            'severity': FindingSeverity.Medium,
            'metadata': {
                'tx_hash': tx_hash,
                'new_owner': new_owner,
                'contract': contract
            }
        })
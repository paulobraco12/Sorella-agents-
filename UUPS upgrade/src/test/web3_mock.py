class Web3Mock:
    def __init__(self, owner, contract_code):
        self.eth = EthMock(owner, contract_code)


class EthMock:
    def __init__(self, owner, contract_code):
        self.contract = ContractMock(owner)
        self.contract_code = contract_code

    def get_code(self, *_, **__):
        return self.contract_code


class ContractMock:
    def __init__(self, owner):
        self.functions = FunctionsMock(owner)

    def __call__(self, address, *args, **kwargs):
        return self


class FunctionsMock:
    def __init__(self, owner):
        self.return_value = owner

    def owner(self):
        return self

    def call(self, *_, **__):
        return self.return_value
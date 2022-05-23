async def can_be_selfdestructed(bytecode):
    """
    This function returns true if SELFDESTRUCT code is reachable in the byte-code
    It is the python implementation of the solution created by MrLuit
    https://github.com/MrLuit/selfdestruct-detect
    :param bytecode
    :return: bool
    """
    STOP = ord(u'\x00')
    JUMPDEST = ord(u'\x5b')
    PUSH1 = ord(u'\x60')
    PUSH32 = ord(u'\x7f')
    RETURN = ord(u'\xf3')
    REVERT = ord(u'\xfd')
    INVALID = ord(u'\xfe')
    SELFDESTRUCT = ord(u'\xff')

    def is_halting(opcode_local):
        return opcode_local in [STOP, RETURN, REVERT, INVALID, SELFDESTRUCT]

    def is_push(opcode_local):
        return PUSH1 <= opcode_local <= PUSH32

    bytecode_len = len(bytecode)
    i = 0
    halted = False
    while True:
        if i >= bytecode_len:
            return False
        opcode = bytecode[i]
        if opcode == SELFDESTRUCT and not halted:
            return True
        elif opcode == JUMPDEST:
            halted = False
        elif is_halting(opcode):
            halted = True
        elif is_push(opcode):
            i += opcode - PUSH1 + 1
        i += 1


async def extract_argument(event: dict, argument: str) -> any:
    """
    the function extract specified argument from the event
    :param event: dict
    :param argument: str
    :return: argument value
    """
    return event.get('args', {}).get(argument, "")
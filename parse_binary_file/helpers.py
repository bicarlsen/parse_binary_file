import io


def read_until(
    stream: io.RawIOBase,
    start: int = 0,
    terminator: bytes = b'\x00',
    with_terminator: bool = False
) -> bytes:
    """
    Read stream until terminator or end of stream.

    :param stream: Stream to read.
    :param start
    :param terminator: Termination string. [Default: b'\x00']
    :param with_terminator: Return value with the terminator string. [Default: False]
    :returns bytes: Byte string.
    """
    word = b''
    i = start
    while True:
        c = stream.read(1)
        if c is None:
            # end of file
            break

        word += c
        if word.endswith(terminator):
            if not with_terminator:
                word = word[:-len(terminator)]

            break

        i += 1

    return word

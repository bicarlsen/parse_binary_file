import io


def read_until(
    stream: io.IOBase,
    terminator: bytes = b'\x00',
    with_terminator: bool = True
) -> bytes:
    """
    Read stream until terminator or end of stream.

    :param stream: Stream to read.
    :param terminator: Termination string. [Default: b'\x00']
    :param with_terminator: Return value with the terminator string.
        [Default: True]
    :returns bytes: Byte string.
    """
    word = b''
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

    return word

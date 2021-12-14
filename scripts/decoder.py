"""Local decoder and encoder, keeping around b/c potentially useful in python later."""

decoder = {
    "/": "A",
    "$": "B",
    "|": "C",
    "8": "D",
    "_": "E",
    "?": "F",
    "#": "G",
    "%": "H",
    "^": "I",
    "~": "K",
    ":": "K",
    "Q": "L",
    "W": "M",
    "E": "N",
    "R": "O",
    "T": "P",
    "Y": "Q",
    "U": "R",
    "I": "S",
    "O": "T",
    "P": "U",
    "A": "V",
    "S": "W",
    "D": "X",
    "F": "Y",
    "G": "Z",
    " ": " ",
}
encoder = {v: k for k, v in decoder.items()}


def decode(message: str) -> str:
    return " ".join([decoder.get(c) for c in message])


def encode(message: str) -> str:
    return " ".join([encoder.get(c) for c in message if c in encoder])


message = ":__T OR FRPUI_Q? 8R ERO I%/U_ WPIO :__T I%RUO ORR WP|% W/E^TPQ/O^RE Q_/8I OR |RUU_|O^RE S^QQ $_ ^E ORP|%"
print(decode(message))

# Automatically generated by pb2py
# fmt: off
import protobuf as p


class DebugLinkLog(p.MessageType):
    MESSAGE_WIRE_TYPE = 104

    def __init__(
        self,
        level: int = None,
        bucket: str = None,
        text: str = None,
    ) -> None:
        self.level = level
        self.bucket = bucket
        self.text = text

    @classmethod
    def get_fields(cls):
        return {
            1: ('level', p.UVarintType, 0),
            2: ('bucket', p.UnicodeType, 0),
            3: ('text', p.UnicodeType, 0),
        }

embed_string = (
    "KQQQQQQQQQ"
    + "FEHGBAQQQQ"
    + "PONMLKJIHG"
    + "CDABGHEFKL"
    + "LKJIPONMDC"
    + "HGFEDCBAPO"
    + "OPMNKLIJGH"
    + "BADCFEHGJI"
)


class GearIDCodec:
    def encode(self, gear_id: int) -> str:
        embedding = ""
        secret = self.secret

        for offset in range(7, -1, -1):
            embedding = secret[offset][gear_id % 10] + embedding
            gear_id = gear_id // 10

        return embedding

    def decode(self, embedding: str) -> int:
        gear_id = 0
        secret = self.secret
        for idx, char in enumerate(embedding):
            gear_id *= 10
            gear_id += secret[idx].find(char)

        return gear_id

    @property
    def secret(self):
        return [
            "KQQQQQQQQQ",
            "FEHGBAQQQQ",
            "PONMLKJIHG",
            "CDABGHEFKL",
            "LKJIPONMDC",
            "HGFEDCBAPO",
            "OPMNKLIJGH",
            "BADCFEHGJI",
        ]

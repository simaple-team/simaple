from requests.cookies import RequestsCookieJar


def get_cookie() -> RequestsCookieJar:
    jar = RequestsCookieJar()
    jar.set("EGC", "")
    jar.set("EGCMP", "")
    jar.set("EGC2", "")
    jar.set("EGCGM", "")

    jar.set("MSGENC", "")

    jar.set("introskip", "")
    jar.set("PCID", "15506531395384481524433")
    jar.set("NXGID", "FA7E6FD8784D7D5CC769344440567194")
    jar.set(
        "NXLW",
        "AA7B15B02F2FB38651342AB38213B3B5&PTC=https:&DOM=maplestory.nexon.com&ID=&CP=",
    )
    jar.set(
        "SID",
        "AA7B15B02F2FB38651342AB38213B3B5&PTC=https:&DOM=maplestory.nexon.com&ID=&CP=",
    )

    jar.set("NXPID", "1634DBE8C02218725ED4E7DF3692BAAF")

    jar.set("NLWGID", "0")

    jar.set("_ga", "GA1.2.983869668.1550653140")
    jar.set("_gid", "GA1.2.1000610741.1550653140")
    jar.set("isCafe", "false")

    jar.set("_fbp", "fb.1.1550653140169.1162462771")
    jar.set("A2SK", "act04:1615649118491891216")
    jar.set("introdayoff", "1")
    jar.set(
        "A2SR",
        "https%253A%252F%252Fmaplestory.nexon.com%252FCommon\
            %252FCharacter%252FDetail%252F%2525ec%252583%25259d%2525eb%2525b6%252584%2525ec%25259e%252590%252F\
                Equipment%253Fp%253DmikO8qgdC4hElCwBGQ6GOx8CmO11EvduZkV0bRbPAhad5gzlD\
                    %25252fH30vgr7QFpImK2Gl2k%25252bs1OQHDhwMxbXKfkjVbdzEYe9wCRH\
                        %25252feGMeahUGSOq2pA75n823dJ%25252bUKMsBl7fgrnAmgIt\
                            %25252boc37L50miIoCe9353MT%25252fWyUJFqW35HwAQ\
                                %25253d%3A1550653159926%3A0",
    )

    return jar

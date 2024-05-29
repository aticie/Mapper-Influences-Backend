import aiohttp


session = aiohttp.ClientSession()


def get_request_session():
    return session

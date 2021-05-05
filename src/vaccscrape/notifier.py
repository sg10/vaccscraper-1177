from vaccscrape.examine import examine
from vaccscrape.pushsafer import send_notification


async def notifier():
    examine_result = await examine()

    if examine_result:
        send_notification(examine_result, important=True)

from vaccscrape.examine import examine
from vaccscrape.pushsafer import send_notification


async def notifier():
    examine_result = await examine()
    if not examine_result:
        return

    assert len(examine_result) == 2

    service_name, msg = examine_result

    send_notification(service_name, msg, important=True)

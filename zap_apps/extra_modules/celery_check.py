from celery.events.snapshot import Polaroid
from celery import Celery
import requests

def main(app, freq=500.0):
    state = app.events.State()
    def test(event):
        if event['type'] == 'worker-offline':
            nums = ["9092892879", "9895685141"]
            for i in nums:
                url = "http://bhashsms.com/api/sendmsg.php?user=Zapyle&pass=zapyle@123&sender=ZAPYLE&phone={}&text={}&priority=ndnd&stype=normal".format(
                    i, "Celery worker {} is shut down now.".format(event['hostname'])
                )
                requests.get(url)
    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={'worker-offline': test, 'worker-online': test})
        with Polaroid(state, freq=freq):
            recv.capture(limit=None, timeout=None)
if __name__ == '__main__':
    app = Celery(broker='amqp://guest:guest@127.0.0.1:5672//')
    main(app)
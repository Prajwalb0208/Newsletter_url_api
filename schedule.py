from qstash.client import QStash

client = QStash.from_env()

API_ENDPOINT = 

CRON_EXPR = "0 */5 * * *"

schedule = client.schedule.create(
    destination=API_ENDPOINT,
    cron=CRON_EXPR,
)

print("QStash schedule created:\n", schedule)

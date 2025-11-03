from qstash.client import QStash

client = QStash.from_env()

API_ENDPOINT = "https://newsletterurlapi-production.up.railway.app/search_resources/"

CRON_EXPR = "0 */5 * * *"

schedule = client.schedule.create(
    destination=API_ENDPOINT,
    cron=CRON_EXPR,
)

print("QStash schedule created:\n", schedule)

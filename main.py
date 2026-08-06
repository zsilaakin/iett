from db import client

result = client.query("SELECT version()")

print(result.result_rows)
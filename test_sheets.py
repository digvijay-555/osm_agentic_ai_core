from app.services.sheets import append_row, read_all

append_row([
    "uuid-1",
    "Test Company",
    "Test Address",
    "9999999999",
    "https://example.com",
    "test@example.com"
])

data = read_all()
print("Rows in sheet:")
print(data)

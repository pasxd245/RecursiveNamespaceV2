from RecursiveNamespace import RecursiveNamespace

# Creating a simple recursive namespace
data = {
    'name': 'John Doe',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'Anytown'
    }
}

rn = RecursiveNamespace(data)

print(rn.name)  # Output: John Doe
print(rn.address.street)  # Output: 123 Main St

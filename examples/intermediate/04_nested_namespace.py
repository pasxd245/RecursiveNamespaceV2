from recursivenamespace import recursivenamespace

# Creating a nested recursive namespace
data = {
    "employee": {
        "name": "Jane Smith",
        "details": {"position": "Developer", "department": "IT"},
    }
}

rn = recursivenamespace(data)

print(rn.employee.name)  # Output: Jane Smith
print(rn.employee.details.position)  # Output: Developer

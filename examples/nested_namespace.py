from RecursiveNamespace import RecursiveNamespace

# Creating a nested recursive namespace
data = {
    'employee': {
        'name': 'Jane Smith',
        'details': {
            'position': 'Developer',
            'department': 'IT'
        }
    }
}

rn = RecursiveNamespace(data)

print(rn.employee.name)  # Output: Jane Smith
print(rn.employee.details.position)  # Output: Developer

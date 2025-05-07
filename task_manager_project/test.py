from passlib.context import CryptContext

# Initialize the password context (matching the bcrypt scheme from the logs)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# The password hash from the logs
stored_hash = "$2b$12$VfHzeOHpewYE7Tmhj7iFpul7lmI3n2vRKPI/Gdzod82rXpSgeYq.W"

# Replace this with the password you think was used during registration
test_password = "test123"

# Verify the password against the stored hash
is_valid = pwd_context.verify(test_password, stored_hash)

# Print the result
print(f"Password verification result: {is_valid}")
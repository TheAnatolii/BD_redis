# Установите PassLib, если ещё не сделали:
# pip install passlib[bcrypt]

from passlib.context import CryptContext

# Настраиваем CryptContext на работу с bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_string(s: str) -> str:
    """
    Хеширует строку s через bcrypt и возвращает результат.
    """
    return pwd_context.hash(s)

if __name__ == "__main__":
    original = "test123"
    hashed = hash_string(original)
    print(f"Оригинал: {original}")
    print(f"Хеш:     {hashed}")

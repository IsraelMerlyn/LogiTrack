import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from typing import Optional, Dict, Any

SECRET_KEY = "logitrack-jwt-secret-key-super-segura-m7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

ph = PasswordHasher(
    time_cost=3,       # 3 iteraciones
    memory_cost=65536, # 64 MB RAM por hash
    parallelism=4      # 4 hilos
)

def hash_password(password: str) -> str:
    """Genera hash Argon2id seguro con salt aleatorio automatizado."""
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash Argon2id en tiempo constante."""
    try:
        return ph.verify(hashed_password, password)
    except (VerifyMismatchError, VerificationError):
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Emite un JWT firmado con el Subject (email) y Claims de Rol y Expiración."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica y valida la firma y vigencia del JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

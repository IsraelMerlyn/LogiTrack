from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import List
from security import hash_password, verify_password, create_access_token, decode_access_token

app = FastAPI(
    title="LogiTrack Security API — Spike 7.5",
    description="Autenticación JWT con Argon2id y Autorización RBAC"
)

security_bearer = HTTPBearer()

class RolUsuario(str, Enum):
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"
    CLIENTE = "CLIENTE"

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    rol: RolUsuario

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

db_usuarios = {}

@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def registrar_usuario(user: UserRegister):
    if user.email in db_usuarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya se encuentra registrado"
        )
    
    db_usuarios[user.email] = {
        "email": user.email,
        "password_hash": hash_password(user.password),
        "rol": user.rol.value
    }
    return {"message": "Usuario registrado exitosamente", "email": user.email, "rol": user.rol.value}

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    user = db_usuarios.get(credentials.email)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de acceso inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = create_access_token(data={"sub": user["email"], "rol": user["rol"]})
    return {"access_token": token, "token_type": "bearer"}

class RoleChecker:
    def __init__(self, roles_permitidos: List[RolUsuario]):
        self.roles_permitidos = [r.value for r in roles_permitidos]

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_rol = payload.get("rol")
        if user_rol not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: Se requiere alguno de los siguientes roles: {self.roles_permitidos}"
            )
        
        return payload

@app.get("/api/v1/flota/admin-only", dependencies=[Depends(RoleChecker([RolUsuario.ADMIN]))])
def panel_administrador():
    return {"status": "ok", "message": "Bienvenido al Panel de Control Exclusivo de Administrador"}

@app.get("/api/v1/flota/monitoreo", dependencies=[Depends(RoleChecker([RolUsuario.ADMIN, RolUsuario.OPERADOR]))])
def monitoreo_flota():
    return {"status": "ok", "message": "Acceso permitido a Monitoreo de Flotas (Admin/Operador)"}

if __name__ == "__main__":
    import uvicorn
    # CAMBIAMOS AL PUERTO 8005 PARA EVITAR CONFLICTOS
    uvicorn.run(app, host="127.0.0.1", port=8005, log_level="error")

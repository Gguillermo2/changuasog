from pydantic import BaseModel
from typing import Optional

class AdminUser(BaseModel):
    username: str
    ContresañUser: str 
    password_2fa: Optional[str] = None 
   
    fernet_key_salt: str

class Login(BaseModel):
    Nombre_user: str
    password : str  
    code : Optional[int] = None 


class Cuentas(BaseModel):
    plataforma: str
    correo_o_usuario : str
    contraseña : str


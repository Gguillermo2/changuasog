from pydantic import BaseModel


class AdminUser(BaseModel):
    username: str
    ContresañUser: str
    password_2fa: str | None = None


class Login(BaseModel):
    Nombre_user: str
    password : str  
    codigo : int | None = None


class Cuentas(BaseModel):
    plataforma: str
    correo_o_usuario : str
    contraseña : str


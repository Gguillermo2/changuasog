from pydantic import BaseModel


class AdminUser(BaseModel):
    username: str
    ContresañUser: str


class Login(BaseModel):
    Nombre_user: str
    password : str  
    codigo : int


class Cuentas(BaseModel):
    plataforma: str
    correo_o_usuario : str
    contraseña : str


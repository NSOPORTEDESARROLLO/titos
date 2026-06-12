import random
import string

from src.modules.lhc2otobo.schemas import AdditionalDataItem

_MAGIC_PREFIXES: list[tuple[str, str, str]] = [
    ("/9j/", "image/jpeg", "jpg"),
    ("iVBOR", "image/png", "png"),
    ("R0lGOD", "image/gif", "gif"),
    ("UklGR", "image/webp", "webp"),
]


def detect_image_info(file_data: str) -> tuple[str, str, str]:
    for prefix, mime, ext in _MAGIC_PREFIXES:
        if file_data.startswith(prefix):
            return mime, file_data, ext
    return "image/png", file_data, "png"


def get_additional_value(data: list[AdditionalDataItem], key: str) -> str | None:
    for item in data:
        if item.key == key:
            return item.value
    return None


def build_body(data: list[AdditionalDataItem]) -> str:
    menu = get_additional_value(data, "menu_principal")
    if menu == "3":
        return (
            f"Medidor : {get_additional_value(data, 'numero_medidor') or ''}\n"
            f"Telefono : {get_additional_value(data, 'numero_telefono') or ''}\n"
            f"Nombre: {get_additional_value(data, 'nombre_usuario') or ''}\n"
            f"Descripcion: {get_additional_value(data, 'descripcion_averia') or ''}"
        )
    if menu == "4":
        return (
            f"Suscriptor : {get_additional_value(data, 'numero_suscriptor') or ''}\n"
            f"Telefono : {get_additional_value(data, 'numero_telefono') or ''}\n"
            f"Nombre: {get_additional_value(data, 'nombre_usuario') or ''}\n"
            f"Descripcion: {get_additional_value(data, 'descripcion_averia') or ''}"
        )
    return ""


def extract_filename(data: list[AdditionalDataItem], ext: str) -> str:
    raw = get_additional_value(data, "averia_imagen_file")
    if not raw:
        raw = "".join(random.choices(string.ascii_letters, k=12))
    else:
        raw = raw.removeprefix("[").removesuffix("]")
        if raw.startswith("file="):
            raw = raw.removeprefix("file=")
    return f"{raw}.{ext}"

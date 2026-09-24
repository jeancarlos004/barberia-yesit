from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

from apps.catalogo.models import Bloqueo, Horario


def weekday_domingo_cero(d: date) -> int:
    """Python: lun=0 … dom=6  →  spec: dom=0 … sáb=6."""
    return (d.weekday() + 1) % 7


def to_min(t: time) -> int:
    return t.hour * 60 + t.minute


def from_min(minutes: int) -> time:
    return time(minutes // 60, minutes % 60)


def hora_str(t: time) -> str:
    return t.strftime("%H:%M")


def _overlap(start: int, end: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start < r1 and end > r0 for r0, r1 in ranges)


def rangos_bloqueos(fecha: date) -> list[tuple[int, int]]:
    return [(to_min(b.desde), to_min(b.hasta)) for b in Bloqueo.objects.filter(fecha=fecha)]


def rangos_ocupados(fecha: date, exclude_id=None) -> list[tuple[int, int]]:
    from .models import Turno

    qs = Turno.objects.filter(fecha=fecha).exclude(estado=Turno.Estado.CANCELADO).select_related("servicio")
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    out = []
    for turno in qs:
        start = to_min(turno.hora)
        out.append((start, start + turno.servicio.duracion))
    return out


def slots_libres(fecha: date, duracion: int, exclude_id=None) -> list[str]:
    horario = Horario.objects.filter(dia=weekday_domingo_cero(fecha)).first()
    if not horario or not horario.abierto:
        return []

    step = getattr(settings, "SLOT_MINUTES", 30)
    now = timezone.localtime()
    hoy = now.date()
    now_min = now.hour * 60 + now.minute

    ocupados = rangos_ocupados(fecha, exclude_id=exclude_id)
    bloqueos = rangos_bloqueos(fecha)
    cierre = to_min(horario.hasta)
    libres: list[str] = []
    minute = to_min(horario.desde)
    while minute + duracion <= cierre:
        fin = minute + duracion
        pasado = fecha < hoy or (fecha == hoy and minute <= now_min)
        if not pasado and not _overlap(minute, fin, bloqueos) and not _overlap(minute, fin, ocupados):
            libres.append(hora_str(from_min(minute)))
        minute += step
    return libres


def siguiente_cupo(duracion: int, dias: int = 30) -> dict | None:
    start = timezone.localdate()
    for i in range(dias):
        fecha = start + timedelta(days=i)
        huecos = slots_libres(fecha, duracion)
        if huecos:
            return {"fecha": fecha.isoformat(), "hora": huecos[0]}
    return None


def parse_hora(value) -> time:
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    text = str(value)
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    raise ValueError("Hora inválida")

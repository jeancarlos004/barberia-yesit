from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from .models import Turno


@shared_task
def enviar_recordatorios_turnos():
    """
    Envía recordatorios de turnos para el día siguiente
    Se ejecuta diariamente a las 8 AM
    """
    mañana = timezone.now().date() + timedelta(days=1)
    turnos_mañana = Turno.objects.filter(
        fecha=mañana,
        estado=Turno.Estado.CONFIRMADO
    ).select_related('usuario', 'servicio')
    
    for turno in turnos_mañana:
        try:
            # Template de email de recordatorio
            subject = f"Recordatorio de turno - Barbería YESIT - {turno.fecha}"
            message = render_to_string(
                'email/recordatorio_turno.html',
                {
                    'turno': turno,
                    'servicio': turno.servicio,
                    'fecha': turno.fecha,
                    'hora': turno.hora
                }
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [turno.usuario.email],
                html_message=message,
                fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando recordatorio para turno {turno.id}: {e}")
    
    return f"Enviados {turnos_mañana.count()} recordatorios"


@shared_task
def limpiar_tokens_expirados():
    """
    Limpia tokens de recuperación de contraseña expirados
    Se ejecuta semanalmente
    """
    from apps.usuarios.models import PasswordResetToken
    
    tokens_eliminados = PasswordResetToken.objects.filter(
        used=False,
        expires_at__lt=timezone.now()
    ).delete()
    
    return f"Eliminados {tokens_eliminados[0]} tokens expirados"


@shared_task
def cancelar_turnos_no_confirmados():
    """
    Cancela turnos pendientes que no fueron confirmados después de 24 horas
    Se ejecuta cada hora
    """
    hace_24_horas = timezone.now() - timedelta(hours=24)
    turnos_cancelados = Turno.objects.filter(
        estado=Turno.Estado.PENDIENTE,
        creado__lt=hace_24_horas
    ).update(estado=Turno.Estado.CANCELADO)
    
    return f"Cancelados {turnos_cancelados} turnos no confirmados"

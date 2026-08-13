# Configuración de GitHub Actions para Cronjob

## Opciones disponibles

Tienes dos formas de ejecutar el scraper automáticamente:

### Opción 1: Sin Docker (Recomendado)
**Workflow:** `scraper-cronjob.yml`

Ventajas:
- ✅ Más rápido (sin overhead de Docker)
- ✅ Ideal para cronjobs simples
- ✅ Usa directamente el runtime de GitHub Actions

**Scheduling:**
```cron
0 2 * * *  # Ejecuta diariamente a las 2:00 AM UTC
```

Edita el cron en el archivo `.github/workflows/scraper-cronjob.yml` para cambiar el horario.

### Opción 2: Con Docker
**Workflow:** `scraper-docker-cronjob.yml`

Ventajas:
- ✅ Entorno aislado y reproducible
- ✅ Fácil de probar localmente
- ✅ Mejor para proyectos complejos

## Cómo configurar

1. **Push a GitHub:**
   ```bash
   git add .github/workflows/ Dockerfile
   git commit -m "Add GitHub Actions cronjob"
   git push
   ```

2. **Verifica en GitHub:**
   - Ve a tu repositorio → Actions
   - Deberías ver el workflow listado
   - Puedes ejecutarlo manualmente haciendo clic en "Run workflow"

3. **(Opcional) Permisos:**
   - Ve a Settings → Actions → General
   - Asegúrate que "Allow GitHub Actions to create and approve pull requests" esté habilitado si quieres que haga commits

## Cambiar el horario

En el archivo YAML del workflow que uses, modifica la línea `cron`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Cambia esto
```

Ejemplos:
- `0 * * * *` → Cada hora
- `0 0 * * *` → Diariamente a medianoche UTC
- `0 9 * * MON-FRI` → Lunes a viernes a las 9 AM UTC

## Monitoreo

- Ve a Actions para ver el historial de ejecuciones
- Cada ejecución muestra logs detallados
- Los commits se harán automáticamente si hay cambios en `data.json`

## Notas importantes

- El schedule en GitHub Actions usa **UTC**
- El workflow necesita permisos de escritura para hacer commits (usa `GITHUB_TOKEN`)
- Si el scraper falla, recibirás una notificación en GitHub

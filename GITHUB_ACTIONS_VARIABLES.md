# Variables de GitHub Actions en el Workflow

## 1. `git config --local user.email` y `git config --local user.name`

Estas líneas configuran **quién hace el commit**:

```yaml
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
```

### ¿Qué hacen?
- **user.email**: Email del "autor" del commit (aparece en el historio de git)
- **user.name**: Nombre del "autor" del commit
- **--local**: Aplica solo al repositorio actual (no globalmente)

### En GitHub Actions:
- Estos commits aparecerán como hechos por "GitHub Action" en el historial
- El avatar será el logo de GitHub Actions

### Personalizarlo:
Puedes cambiar el nombre y email si quieres:
```yaml
git config --local user.email "tu-email@example.com"
git config --local user.name "Mi Bot"
```

---

## 2. `secrets.GITHUB_TOKEN`

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### ¿Qué es?
Un **token automático y seguro** que GitHub genera para cada workflow. Te permite hacer operaciones como:
- ✅ Hacer commits y push
- ✅ Crear PRs
- ✅ Comentar en issues
- ✅ Descargar artefactos

### Importante:
- ⚠️ **No debes crear tu propio token** — GitHub lo genera automáticamente
- ⚠️ **No aparece en los logs** — es enmascarado automáticamente
- ⚠️ **Solo vive durante la ejecución del workflow** — se invalida después
- ⚠️ **Es diferente de tu PAT** (Personal Access Token)

### Permisos por defecto:
El `GITHUB_TOKEN` tiene permisos en tu repositorio actual:
```
- contents: read/write
- pull-requests: read/write
- issues: read/write
```

### ¿Por qué lo necesitas en nuestro caso?
Para que el workflow pueda hacer `git push`:

```yaml
- name: Commit and push changes
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"
    git add data.json
    git commit -m "Update recipe data"
    git push  # ← Esto necesita autenticación → Usa GITHUB_TOKEN
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Flujo completo:

1. **Workflow se ejecuta** en GitHub Actions
2. **Ejecuta el scraper** → genera `data.json` actualizado
3. **Configura git** con nombre y email
4. **Hace commit** de los cambios
5. **Usa GITHUB_TOKEN** para autenticarse en el push
6. **Push a main** (o la rama que uses)

---

## Configuración de permisos en GitHub

Para que esto funcione, GitHub necesita permitir que Actions haga commits:

### En tu repositorio:
1. Ve a **Settings** → **Actions** → **General**
2. Busca **Workflow permissions**
3. Selecciona: **Read and write permissions**
4. Marca: **Allow GitHub Actions to create and approve pull requests** (opcional)

O puedes especificar permisos en el YAML:
```yaml
permissions:
  contents: write
  pull-requests: write
```

---

## Alternativa: Usar tu propio token (PAT)

Si prefieres usar tu token personal en lugar de `GITHUB_TOKEN`:

### Crear un Personal Access Token (PAT):
1. GitHub → Settings → Developer settings → Personal access tokens
2. Crear nuevo token con permisos: `repo`
3. Guardarlo como secret en el repositorio

### Usar en el workflow:
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.MY_PERSONAL_TOKEN }}
```

**Ventajas:**
- Mejor control y auditoría
- Persiste entre workflows

**Desventajas:**
- Más manual de configurar
- Necesitas renovar el token periódicamente

---

## Seguridad: Mejores prácticas

✅ **Usa `GITHUB_TOKEN`** por defecto (automático y seguro)
✅ **Limita permisos** a solo lo que necesitas
✅ **Usa `git config --local`** (no global)
✅ **Mantén el email genérico** o con dominio de tu organización
❌ **Nunca hardcodees credenciales** en el YAML
❌ **Nunca expongas tokens** en logs o error messages


# QA — Propuestas de Mejora

## [2026-04-20] Protocolo "inicio de jornada": `git fetch` antes de trabajar

### Problema observado

Durante la jornada del 20/04/2026 el agente ejecutó el inicio de jornada
sin verificar el estado remoto primero. Resultado:

- Se trabajó sobre una base desincronizada con `origin/main`.
- `origin/main` tenía 14 commits empujados autónomamente por otros agentes.
- Al cerrar la jornada y hacer `git add + commit`, el local divergió del remoto.
- Fue necesario un `git rebase` manual con resolución de conflictos.

### Causa raíz

El trigger "inicio de jornada" en `copilot-instructions.md` indicaba
`git pull` (operación destructiva si hay commits locales), y no incluía
un paso de diagnóstico previo.

### Mejora propuesta

Agregar al protocolo de "inicio de jornada" un paso explícito **antes**
de cualquier acción:

```bash
git fetch origin
git status
git log --oneline -5
```

Con las siguientes reglas de decisión:

| Estado detectado | Acción |
|---|---|
| Local == origin | Continuar normalmente |
| origin adelante, local limpio | Informar commits nuevos, preguntar si integrar |
| Divergencia (ambos tienen commits) | **STOP** — no actuar, informar al usuario |
| Local adelante de origin | Informar, preguntar si pushear al cierre |

### Por qué `fetch` y no `pull`

`git pull` = `git fetch` + `git merge` (o rebase) automático.
Si ya existe trabajo local, el merge puede crear conflictos sin aviso
o un commit de merge no deseado en el historial.
`git fetch` solo descarga metadata — no modifica el árbol local.

### Estado

- [ ] Pendiente de aprobación para incorporar a `copilot-instructions.md`

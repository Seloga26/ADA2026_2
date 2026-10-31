# Informe

Fuente LaTeX del informe técnico. Cada sección vive en `secciones/` y tiene un responsable.

## Compilar

Desde esta carpeta:

```
latexmk main.tex
```

El PDF queda en `build/main.pdf`, que no se versiona.

## Reglas

- Cada integrante edita solo sus secciones; `main.tex` y `preambulo.tex` cambian en PR dedicados.
- Las figuras se generan con los scripts y se toman de `resultados/`.
- Las referencias van en `referencias.bib`.
- El PDF final se versiona solo en la entrega.

# Plataforma Kubernetes de Alta Disponibilidad — II Unidad (Sistemas Operativos II)

Diseño de una plataforma de orquestación de contenedores con Kubernetes (3 nodos de control con etcd apilado,
3 workers, balanceo con HAProxy + Keepalived, Cilium, MetalLB + Traefik, Longhorn, CloudNativePG) sobre 3 hosts
Proxmox VE. El diseño se deriva de la revisión bibliográfica de la I Unidad.

## Estructura

```
.
├── src/             Código que genera diagramas, documento técnico y presentación
│   ├── datos.py         Costos y cronograma (fuente única para diagramas, documento y presentación)
│   ├── c_*.py           Contenido del documento por secciones (1–4, 5–7, 8–9, 10–14 y anexo)
│   ├── refs.py          Referencias bibliográficas
│   ├── docx_*.py        Construcción del .docx sobre la plantilla institucional
│   ├── diagramas.py · build_doc.py · build_ppt.py   Puntos de entrada
│   ├── word_pdf.ps1 · ppt_pdf.ps1                   Exportación a PDF con Office (Windows)
│   └── assets/          Logo usado en la portada de la presentación
├── diagramas/       Diagramas técnicos en PNG (arquitectura, red, seguridad, despliegue, flujos, cronograma, TCO)
├── Entregables/     Salida generada: documento técnico (.docx) y presentación (.pptx) — no se versiona
├── Referencias/     Artículos y plantilla del curso — no se versiona
├── requirements.txt
└── README.md
```

## Regenerar los entregables

```bash
pip install -r requirements.txt
python src/diagramas.py     # diagramas/*.png
python src/build_doc.py     # Entregables/Documento_Tecnico_II_Unidad.docx
python src/build_ppt.py     # Entregables/Presentacion_II_Unidad.pptx
```

Notas:
- `build_doc.py` necesita la plantilla `Referencias/Plantilla_portada.docx` (no se versiona).
- El índice del `.docx` se actualiza en Word (clic derecho → Actualizar campos) o con `src/word_pdf.ps1`, que además exporta a PDF
  (requiere Word en Windows). `src/ppt_pdf.ps1` hace lo mismo con PowerPoint.
- Los diagramas usan la fuente *Segoe UI* (Windows); en otros sistemas se usa *DejaVu Sans*.
- Los costos del documento son estimaciones referenciales del equipo y deben validarse con cotizaciones.

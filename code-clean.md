# Informe de Limpieza y Mejoras de Código Base

A continuación se detalla el análisis de los archivos y modelos de la base de datos identificados como "código muerto", y propuestas de refactorización para alinear la carga de datos con los estándares y convenciones de Django.

---

## 1. Archivos y Modelos Identificados como "Código Muerto"

### A. Modelos y scripts de mapeo de genes (RefSeq / Symbol)
*   **Archivos implicados**: La carpeta entera `modulector/mappers/` (que incluye `ref_seq_mapper.py` y `gene_mapper.py`), `modulector/utils/gene_translator` y `modulector/utils/input.txt`.
*   **Modelos de Base de Datos implicados**: `OldRefSeqMapping` y `GeneSymbolMapping` (definidos en `models.py`).
*   **Contexto**: Todos estos scripts y mappers fueron creados hace tiempo para poblar las tablas `modulector_oldrefseqmapping` y `modulector_genesymbolmapping` con traducciones y mapeos de genes extraídos de NCBI/RefSeq.
*   **¿Se usan estas tablas actualmente?**: **¡NO!**. Tras revisar exhaustivamente todo el código base, se confirmó que los modelos `OldRefSeqMapping` y `GeneSymbolMapping` **no son consultados por ninguna vista, serializador, ni lógica de negocio en toda la aplicación**. 
*   **Acción propuesta**: Eliminar todo este conjunto de código y destruir los modelos de `models.py`. Esto último requerirá crear una nueva migración (`python manage.py makemigrations`) que ejecutará un `DROP TABLE` de ambas tablas, limpiando definitivamente la base de datos.

### B. El resto del directorio `modulector/mappers/`
*   **`pubmed_mapper.py`**: Es un script obsoleto que lee un Excel que ya no existe y su función `execute()` no es llamada desde ninguna parte del código base.
*   **`mature_mirna_mapper.py`**: Solía usarse para cargar los alias de miRNAs a partir de un archivo de texto, pero esto ya se hace oficialmente desde la migración `0036` leyendo el archivo `mature.fa` y `0042` leyendo el archivo `mirna_mature.txt`
*   **Conclusión**: Toda la carpeta `modulector/mappers/` es código muerto y puede ser borrada por completo.

### C. `modulector/processors/sequence_processor.py`
*   **Por qué borrarlo**: Utilizado originalmente para extraer las secuencias del archivo `mature.fa` y poblar la tabla `Mirna`. Actualmente es obsoleto porque su funcionalidad fue reemplazada idénticamente en la migración de datos oficial `0036_auto_20230116_2049.py`.

---

## 2. El Modelo `GeneAliases` y su Procesador

### A. Contexto y Uso
*   **¿Para qué se usan estos datos?**: Estos datos son **muy importantes**. Se usan en `modulector/views.py` (específicamente en `__get_gene_aliases`). Cuando el usuario o la API realiza una búsqueda por un gen, este método consulta la tabla `GeneAliases` para encontrar todos los "sinónimos" históricos de ese gen. Esto permite que la búsqueda arroje resultados completos, incluso si en otras tablas el gen está indexado con un nombre antiguo.
*   **¿De dónde sale `hgnc_complete_set.txt` y está documentado?**: **NO está documentado**. No hay instrucciones en `DEPLOYING.md` sobre de dónde descargar este archivo ni cómo cargarlo. 

### B. Propuesta de Solución para `GeneAliases`
1.  **Documentar el origen**: Se debe investigar y documentar en `DEPLOYING.md` los pasos exactos para que un administrador descargue el archivo `hgnc_complete_set.txt`.
2.  **Migrar el código**: Mover la lógica de carga (actualmente en `modulector/processors/gene_alias_processor.py`) a una **Migración de Datos Oficial de Django**, para que todo sea manejado por `python manage.py migrate`.

---

## 3. Mejoras para `drugs_processor.py`

*   **Contexto**: El archivo `drugs.xls` no se distribuye por problemas de licencias, por lo que el usuario debe conseguirlo por su cuenta e incorporarlo al proyecto. 
*   **Propuesta**: Al igual que con `GeneAliases`, se puede mover la lógica de `drugs_processor.py` a una migración de Django validando primero si el archivo existe (ej. `if not os.path.isfile(filepath): return`). Este es el **mismo patrón** que el proyecto ya utiliza de manera exitosa en la migración `0036` con la base de `mirDIP`.

---

## 4. Mantenimiento del Historial de Migraciones (Squashing)

*   **El Problema**: El proyecto ha acumulado decenas de migraciones (muchas de ellas alterando los mismos modelos repetidas veces), lo cual ralentiza el despliegue inicial de bases de datos.
*   **La Solución**: Utilizar la herramienta nativa **Squashing** (`python manage.py squashmigrations modulector`).
*   **Beneficio**: Comprime el largo historial en unas pocas migraciones ultra-optimizadas, eliminando pasos intermedios. Ideal para bases de datos estables en producción.
# CreateExpediente AI Assistant Instructions

## Project Overview
This is a specialized Python package that generates **visual diagrams and Word documentation** for academic system integration flows between three components:
- **GestorMapeos** (enrollment mapping system) 
- **ERP Académico** (academic ERP system)
- **Expedientes** (student records system)

The package creates both PNG diagrams and detailed DOCX documents showing API flows for two scenarios: "Primera Matrícula" (first enrollment) and "Ampliación" (enrollment extensions).

## Architecture & Key Files

### Core Module Structure
- **`diagrama.py`**: Main logic - generates PIL-based diagrams and python-docx documents
- **`__init__.py`**: Package interface exposing `generate_diagram()` and `main()`
- **`__main__.py`**: Entry point for `python -m CreateExpediente` execution
- **`tests/test_diagrama.py`**: Unit tests verifying file generation

### Key Function: `generate_diagram(output_dir=None)`
- Returns tuple: `(img_path, doc_path)`
- Creates `output/` subdirectory by default within package
- Generates two files:
  - `diagram_expedientes_flow.png` - PIL-drawn flow diagram
  - `Esquema_Flujos_GestorMapeos_ERP_Expedientes.docx` - comprehensive documentation

## Domain-Specific Patterns

### API Endpoints (hardcoded in business logic)
```python
# ERP Académico endpoints
https://erpacademico.unir.net/api/v1/migrar  # First enrollment
https://erpacademico.unir.net/api/v1/migrar/ampliacion  # Extensions

# Expedientes endpoints  
https://expedientesacademico.unir.net/api/v1/expedientes-alumnos  # Create/update
https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/{id}/por-integracion  # Update existing
https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/matricula-realizada  # Enrollment notification
```

### Color Coding System
```python
color_gestor = (14, 82, 160)        # Dark blue for GestorMapeos
color_erp = (54, 126, 223)          # Medium blue for ERP Académico  
color_expedientes = (142, 199, 125) # Green for Expedientes
```

### Font Fallback Pattern
Uses DejaVu fonts with graceful fallback to PIL defaults when fonts unavailable.

## Development Workflows

### Running the Package
```powershell
python -m CreateExpediente  # Preferred module execution
python -c "from CreateExpediente import main; main()"  # Alternative
```

### Testing
```powershell
python -m unittest discover CreateExpediente/tests -v
```

### Dependencies
- **Pillow**: PNG diagram generation with custom drawing
- **python-docx**: DOCX document creation with embedded images

## Code Conventions

### Function Organization
- **Private functions**: `_load_fonts()` for internal utilities
- **Public API**: `generate_diagram()` as main interface, `main()` for CLI
- **Nested helpers**: `draw_box()`, `draw_arrow()` defined inside `generate_diagram()`

### Error Handling
Font loading uses try/except with PIL default fallback - this pattern should be maintained for robustness.

### Output Structure
All generated files go to `output/` subdirectory with predictable naming for integration scenarios.

When modifying this codebase, preserve the academic domain terminology and the specific API endpoint references, as these represent real integration points in the UNIR academic system.
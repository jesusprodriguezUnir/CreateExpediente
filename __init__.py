"""CreateExpediente package

Exposes generate_diagram(output_dir) which creates the PNG and DOCX and returns their paths.
Also provides generate_png_only() and generate_word_only() for separate generation.
"""
from .diagrama import generate_diagram, generate_png_only, generate_word_only, main

__all__ = ["generate_diagram", "generate_png_only", "generate_word_only", "main"]

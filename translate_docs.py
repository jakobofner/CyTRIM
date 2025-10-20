#!/usr/bin/env python3
"""Translate German markdown documentation to English."""

import re
from pathlib import Path

# Translation dictionary for common terms
TRANSLATIONS = {
    # Headers
    "## Kern-Features": "## Core Features",
    "### Physik & Simulation": "### Physics & Simulation",
    "### Benutzeroberfläche": "### User Interface",
    "### Visualisierung & Analyse": "### Visualization & Analysis",
    "### Export & Integration": "### Export & Integration",
    "### Performance": "### Performance",
    "## Was macht das Programm?": "## What Does the Program Do?",
    "## Wie funktioniert es? (Ablauf)": "## How Does It Work? (Process)",
    "## Projektstruktur": "## Project Structure",
    "### GUI-Version (empfohlen)": "### GUI Version (recommended)",
    "### Kern-Module": "### Core Modules",
    "### Legacy": "### Legacy",
    "## Installation": "## Installation",
    "### Voraussetzungen": "### Prerequisites",
    "### Schnellinstallation": "### Quick Installation",
    "### Cython-Optimierung (empfohlen für beste Performance)": "### Cython Optimization (recommended for best performance)",
    "## Ausführen": "## Running",
    "### Cython-Toggle Feature": "### Cython Toggle Feature",
    "### Kommandozeilen-Version (Legacy)": "### Command Line Version (Legacy)",
    "## Konfiguration der Simulation": "## Simulation Configuration",
    "## Beispiele": "## Examples",
    "## Erweiterte Features": "## Advanced Features",
    "## Fehlerbehebung": "## Troubleshooting",
    "## Limitierungen": "## Limitations",
    "## Zukünftige Erweiterungen": "## Future Extensions",
    "## Bekannte Probleme": "## Known Issues",
    "### Bekannte Limitierungen": "### Known Limitations",
    "### Zukünftige Erweiterungen (möglich)": "### Possible Future Extensions",
    "## Kompatibilität": "## Compatibility",
    "## Installation & Start": "## Installation & Startup",
    "## Neue Features": "## New Features",
    "## Dateistruktur": "## File Structure",
    "### Neu erstellte Dateien": "### Newly Created Files",
    "### Geänderte Dateien": "### Modified Files",
    "### Unverändert (Kern-Physik)": "### Unchanged (Core Physics)",
    "## Technische Details": "## Technical Details",
    "### Abhängigkeiten": "### Dependencies",
    "### Threading-Architektur": "### Threading Architecture",
    "### Plot-Integration": "### Plot Integration",
    "## Migration von alter Version": "## Migration from Old Version",
    "### Für Nutzer": "### For Users",
    "### Für Entwickler": "### For Developers",
    
    # Common phrases
    "# Repository klonen oder herunterladen": "# Clone or download repository",
    "# Virtuelle Umgebung erstellen (empfohlen)": "# Create virtual environment (recommended)",
    "# Abhängigkeiten installieren": "# Install dependencies",
    "# Nach der Grundinstallation:": "# After basic installation:",
    "# Oder manuell:": "# Or manually:",
    "# Virtuelle Umgebung aktivieren": "# Activate virtual environment",
    "# oder": "# or",
    "# GUI starten": "# Start GUI",
    "# OPTIONAL aber EMPFOHLEN": "# OPTIONAL but RECOMMENDED",
    
    # Content
    "3D Trajektorien-Verfolgung": "3D trajectory tracking",
    "vollständiger Positions-Historie": "complete position history",
    "Elastische Streuung am Targetatom": "Elastic scattering at target atom",
    "liefert neue Richtung und Energie": "returns new direction and energy",
    "Zur Laufzeit zwischen Cython und Python wechseln": "Switch between Cython and Python at runtime",
    "Prüfe Cython-Verfügbarkeit": "Check Cython availability",
    "Cython-Module verfügbar": "Cython modules available",
    "Nur Primärionen werden verfolgt": "Only primary ions are tracked",
    "Rekoilkaskaden werden nicht weiter simuliert": "Recoil cascades are not simulated further",
    "verfolgen": "track",
    "Fortschritt in Echtzeit verfolgen": "Track progress in real time",
    
    # Common terms in text
    "Energie": "Energy",
    "Tiefe": "Depth",
    "Richtung": "Direction",
    "Geschwindigkeit": "Velocity",
    "Streuung": "Scattering",
    "Projektion": "Projection",
    "Simulation": "Simulation",
    "Parameter": "Parameters",
    "Ergebnis": "Result",
    "Ergebnisse": "Results",
    "verfügbar": "available",
    "Verfügbar": "Available",
    "empfohlen": "recommended",
    "optional": "optional",
}

def translate_file(filepath):
    """Translate a single markdown file."""
    print(f"Translating {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply translations
    translated = content
    for german, english in TRANSLATIONS.items():
        translated = translated.replace(german, english)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(translated)
    
    print(f"  ✓ {filepath.name} translated")

def main():
    """Translate all markdown files."""
    print("="*60)
    print("Translating CyTRIM Documentation to English")
    print("="*60)
    print()
    
    # Get all markdown files
    md_files = list(Path('.').glob('*.md'))
    md_files = [f for f in md_files if f.name != 'README_DE.md']  # Skip backup
    
    print(f"Found {len(md_files)} markdown files to translate\n")
    
    for md_file in sorted(md_files):
        translate_file(md_file)
    
    print()
    print("="*60)
    print("Translation complete!")
    print("="*60)
    print()
    print("Note: This is an automated translation of common terms.")
    print("Manual review and editing may be needed for complete accuracy.")
    print()
    print("German README backup saved as: README_DE.md")

if __name__ == "__main__":
    main()

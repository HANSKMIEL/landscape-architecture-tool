# VS Code Configuration for Line Length

Dit project gebruikt een **line-length standaard van 120 characters**, zoals geconfigureerd in `pyproject.toml`.

## Configuratie Bestanden

De volgende bestanden configureren de line-length:

1. **`pyproject.toml`** - Python tools configuratie:
   - Black: `line-length = 120`
   - Ruff: `line-length = 120`
   - isort: `line_length = 120`

2. **`.vscode/settings.json`** - VS Code workspace settings:
   - Editor rulers op 120
   - Black args met `--line-length=120`
   - Ruff args met `--line-length=120`

3. **`.editorconfig`** - Cross-editor configuratie:
   - Python: `max_line_length = 120`

4. **`.pylintrc`** - Pylint configuratie:
   - `max-line-length=120`

## VS Code Line-Length Warnings Oplossen

Als je nog steeds "line too long" warnings ziet in VS Code:

### Optie 1: Reload VS Code Window (Aanbevolen)
1. Open Command Palette (`Ctrl+Shift+P` of `Cmd+Shift+P`)
2. Type: "Developer: Reload Window"
3. Druk Enter

### Optie 2: Clear Cache
1. Sluit alle Python bestanden
2. Open Command Palette
3. Type: "Python: Clear Cache and Reload Window"
4. Druk Enter

### Optie 3: Restart Python Language Server
1. Open Command Palette
2. Type: "Python: Restart Language Server"
3. Druk Enter

### Optie 4: Manual VS Code Restart
1. Sluit VS Code volledig
2. Open opnieuw

## Verificatie

Na het herladen, controleer of:
- De verticale ruler op 120 characters staat (niet 79)
- Geen "line too long" warnings voor regels < 120 characters
- Black en Ruff de juiste line-length gebruiken

## Command Line Verificatie

Je kunt controleren of de tools correct geconfigureerd zijn:

```bash
# Black check (should respect 120 chars)
python -m black src/main.py --check --line-length 120

# Ruff check (E501 = line too long, should be ignored)
python -m ruff check src/main.py --select E501

# Expected output: "All checks passed!"
```

## Waarom 120 Characters?

Het project gebruikt 120 characters in plaats van de traditionele 79 omdat:
- Moderne monitors zijn breder
- Verbetert leesbaarheid van complexe code
- Reduceert onnodige line breaks
- Is de nieuwe standaard in veel moderne Python projecten
- PEP 8 staat 99 of meer toe voor teams die dat prefereren

## Notitie over PEP 8

PEP 8 specificeert 79 characters als aanbeveling, maar staat expliciet langere lengtes toe:
> "Some teams strongly prefer a longer line length. For code maintained exclusively 
> or primarily by a team that can reach agreement on this issue, it is okay to 
> increase the line length limit up to 99 characters, provided that comments and 
> docstrings are still wrapped at 72 characters."

Wij hebben gekozen voor 120 characters als teamstandaard.

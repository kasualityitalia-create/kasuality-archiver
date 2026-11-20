![Kasuality Archiver](docs/social-preview.png)

# Kasuality Archiver — by Kasuality

Archiver desktop gratuito, veloce e senza pubblicità per Windows, pensato per sostituire WinZip e WinRAR nelle attività quotidiane di sviluppatori, designer e agenzie.

## Cosa offre in più rispetto a WinZip / WinRAR
- **100% Free, Zero Ads, Zero Nag Screen** (`by Kasuality` — [kasuality.com](https://kasuality.com))
- **Quick Look istantaneo**: anteprima di file di testo, codice e immagini direttamente in memoria senza estrarre su disco
- **Scansione Sicurezza Zero-Trust**: rileva path traversal, doppie estensioni sospette (es. `.pdf.exe`) e zip bomb prima di estrarre
- **Ricerca Full-Text negli archivi**: cerca parole o righe di codice dentro i file compressi senza scompattarli
- **Formati moderni**: crea ed estrae `.zip`, `.7z`, `.tar.zst` (Zstandard multi-thread) e `.tar.gz`, e legge `.tar`, `.tar.bz2`, `.tar.xz`, `.zst`
- **Smart Dev Exclude**: salta automaticamente `node_modules`, `.git`, `__pycache__`, `dist`, `.venv` durante la creazione
- **SHA-256 immediato**: calcola e copia l'hash di integrità per consegne sicure ai clienti

## Avvio rapido
Doppio clic su `launch.bat` oppure da terminale:
```powershell
python app.py
```

## Test automatici
```powershell
python -m unittest discover -s tests -v
```

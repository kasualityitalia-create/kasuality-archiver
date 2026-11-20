"""Internationalization strings (EN, IT, FR, ES, DE) for Kasuality Archiver."""

from __future__ import annotations

import locale

SUPPORTED_LANGS = ("en", "it", "fr", "es", "de")

TRANSLATIONS = {
    "en": {
        "app_title": "Kasuality Archiver — by Kasuality",
        "no_archive": "No archive open",
        "ready_status": "Ready. Open an archive or create a new one with Smart Dev Exclude.",
        "btn_open": "Open Archive",
        "btn_new": "New Archive",
        "btn_extract": "Safe Extract",
        "btn_security": "Security Report",
        "btn_sha": "Verify SHA-256",
        "mode_filename": "Filename",
        "mode_content": "Full-Text inside files",
        "btn_search": "Search",
        "col_path": "Path in archive",
        "col_size": "Size",
        "col_comp": "Compressed",
        "col_type": "Type",
        "folder": "Folder",
        "file": "File",
        "quick_look": "Quick Look (Preview without extracting)",
        "welcome_text": (
            "Select a text, code, or image file inside an archive\n"
            "to preview it instantly in memory without extracting to disk.\n\n"
            "Key advantages over traditional tools:\n"
            "- Automatic scan against path traversal and double extensions\n"
            "- Full-text search inside compressed files\n"
            "- Create .tar.zst (Zstandard), .7z, .zip, .tar.gz archives\n"
            "- Smart Dev Exclude (skips node_modules, .git, __pycache__, dist)\n"
            "- 100% Free, Zero Ads, Zero Nag Screen — by Kasuality"
        ),
        "footer_brand": "100% Free • Zero Ads • by Kasuality (kasuality.com)",
        "badge_safe": "SAFE ({n} files verified)",
        "badge_warn": "WARNING ({n} alerts)",
        "badge_danger": "DANGER ({n} threats)",
        "binary_preview": "Binary file ({size}).\nText preview unavailable.",
        "non_text_preview": "File: {name}\nSize: {size}\n\nNon-text extension: use 'Safe Extract' to open it.",
        "extract_done": "Extracted {count} items into:\n{path}",
        "new_title": "New Archive — by Kasuality",
        "source_label": "Source: {name}",
        "format_label": "Archive format:",
        "smart_dev_label": "Smart Dev Exclude (skip node_modules, .git, __pycache__, dist, .venv)",
        "level_label": "Compression level (1 = fast, 9 = max):",
        "btn_create": "Create Archive",
        "created_msg": "Created: {name}\nFiles included: {count}\nFinal size: {size}\n\nSHA-256:\n{sha}",
        "sha_copied": "File: {name}\n\nSHA-256:\n{sha}\n\n(Copied to clipboard)",
        "not_archive_prompt": "'{name}' is not a compressed archive.\nDo you want to compress it into a new archive now?",
        "extract_selected_prompt": "You selected {n} item(s).\n\nYes = Extract ONLY selected\nNo = Extract ALL files\nCancel = Abort",
        "ctx_extract_selected": "Extract selected only",
        "lang_label": "Lang:",
    },
    "it": {
        "app_title": "Kasuality Archiver — by Kasuality",
        "no_archive": "Nessun archivio aperto",
        "ready_status": "Pronto. Apri un archivio o creane uno nuovo con Smart Dev Exclude.",
        "btn_open": "Apri Archivio",
        "btn_new": "Nuovo Archivio",
        "btn_extract": "Estrai in Sicurezza",
        "btn_security": "Report Sicurezza",
        "btn_sha": "Verifica SHA-256",
        "mode_filename": "Nome",
        "mode_content": "Full-Text nei file",
        "btn_search": "Cerca",
        "col_path": "Percorso nell'archivio",
        "col_size": "Dimensione",
        "col_comp": "Compresso",
        "col_type": "Tipo",
        "folder": "Cartella",
        "file": "File",
        "quick_look": "Quick Look (Anteprima senza estrazione)",
        "welcome_text": (
            "Seleziona un file di testo, codice o immagine dentro un archivio\n"
            "per visualizzarlo istantaneamente in memoria senza estrarlo su disco.\n\n"
            "Vantaggi inclusi rispetto ai tool tradizionali:\n"
            "- Scansione automatica anti path-traversal e doppie estensioni\n"
            "- Ricerca full-text dentro i file compressi\n"
            "- Creazione archivi .tar.zst (Zstandard), .7z, .zip, .tar.gz\n"
            "- Smart Dev Exclude (salta node_modules, .git, __pycache__, dist)\n"
            "- 100% Gratuito, Zero Ads, Zero Nag Screen — by Kasuality"
        ),
        "footer_brand": "100% Free • Zero Ads • by Kasuality (kasuality.com)",
        "badge_safe": "SICURO ({n} file verificati)",
        "badge_warn": "ATTENZIONE ({n} avvisi)",
        "badge_danger": "PERICOLO ({n} blocchi)",
        "binary_preview": "File binario ({size}).\nAnteprima testuale non disponibile.",
        "non_text_preview": "File: {name}\nDimensione: {size}\n\nEstensione non testuale: usa 'Estrai in Sicurezza' per aprirlo.",
        "extract_done": "Estratti {count} elementi in:\n{path}",
        "new_title": "Nuovo Archivio — by Kasuality",
        "source_label": "Sorgente: {name}",
        "format_label": "Formato archivio:",
        "smart_dev_label": "Smart Dev Exclude (salta node_modules, .git, __pycache__, dist, .venv)",
        "level_label": "Livello compressione (1 = veloce, 9 = massimo):",
        "btn_create": "Crea Archivio",
        "created_msg": "Creato: {name}\nFile inclusi: {count}\nDimensione finale: {size}\n\nSHA-256:\n{sha}",
        "sha_copied": "File: {name}\n\nSHA-256:\n{sha}\n\n(Già copiato negli appunti)",
        "not_archive_prompt": "'{name}' non è un archivio compresso.\nVuoi comprimerlo in un nuovo archivio adesso?",
        "extract_selected_prompt": "Hai selezionato {n} file.\n\nSì = Estrai SOLO i file selezionati\nNo = Estrai TUTTO l'archivio\nAnnulla = Esci",
        "ctx_extract_selected": "Estrai solo selezionati",
        "lang_label": "Lingua:",
    },
    "fr": {
        "app_title": "Kasuality Archiver — by Kasuality",
        "no_archive": "Aucune archive ouverte",
        "ready_status": "Prêt. Ouvrez une archive ou créez-en une avec Smart Dev Exclude.",
        "btn_open": "Ouvrir Archive",
        "btn_new": "Nouvelle Archive",
        "btn_extract": "Extraction Sûre",
        "btn_security": "Rapport Sécurité",
        "btn_sha": "Vérifier SHA-256",
        "mode_filename": "Nom",
        "mode_content": "Texte intégral",
        "btn_search": "Rechercher",
        "col_path": "Chemin dans l'archive",
        "col_size": "Taille",
        "col_comp": "Compressé",
        "col_type": "Type",
        "folder": "Dossier",
        "file": "Fichier",
        "quick_look": "Quick Look (Aperçu sans extraction)",
        "welcome_text": (
            "Sélectionnez un fichier texte, code ou image dans une archive\n"
            "pour l'afficher instantanément en mémoire sans l'extraire.\n\n"
            "Avantages inclus :\n"
            "- Analyse automatique anti path-traversal et doubles extensions\n"
            "- Recherche plein texte dans les fichiers compressés\n"
            "- Création d'archives .tar.zst (Zstandard), .7z, .zip, .tar.gz\n"
            "- Smart Dev Exclude (ignore node_modules, .git, __pycache__, dist)\n"
            "- 100% Gratuit, Sans Pub — by Kasuality"
        ),
        "footer_brand": "100% Free • Zero Ads • by Kasuality (kasuality.com)",
        "badge_safe": "SÛR ({n} fichiers vérifiés)",
        "badge_warn": "ATTENTION ({n} alertes)",
        "badge_danger": "DANGER ({n} menaces)",
        "binary_preview": "Fichier binaire ({size}).\nAperçu texte indisponible.",
        "non_text_preview": "Fichier : {name}\nTaille : {size}\n\nUtilisez 'Extraction Sûre' pour l'ouvrir.",
        "extract_done": "{count} éléments extraits dans :\n{path}",
        "new_title": "Nouvelle Archive — by Kasuality",
        "source_label": "Source : {name}",
        "format_label": "Format d'archive :",
        "smart_dev_label": "Smart Dev Exclude (ignore node_modules, .git, __pycache__, dist, .venv)",
        "level_label": "Niveau de compression (1 = rapide, 9 = max) :",
        "btn_create": "Créer l'Archive",
        "created_msg": "Créé : {name}\nFichiers inclus : {count}\nTaille finale : {size}\n\nSHA-256 :\n{sha}",
        "sha_copied": "Fichier : {name}\n\nSHA-256 :\n{sha}\n\n(Copié dans le presse-papiers)",
        "not_archive_prompt": "'{name}' n'est pas une archive compressée.\nVoulez-vous le compresser dans une nouvelle archive maintenant ?",
        "extract_selected_prompt": "Vous avez sélectionné {n} élément(s).\n\nOui = Extraire UNIQUEMENT la sélection\nNon = Extraire TOUTE l'archive\nAnnuler = Quitter",
        "ctx_extract_selected": "Extraire uniquement la sélection",
        "lang_label": "Langue:",
    },
    "es": {
        "app_title": "Kasuality Archiver — by Kasuality",
        "no_archive": "Ningún archivo abierto",
        "ready_status": "Listo. Abre un archivo comprimido o crea uno con Smart Dev Exclude.",
        "btn_open": "Abrir Archivo",
        "btn_new": "Nuevo Archivo",
        "btn_extract": "Extracción Segura",
        "btn_security": "Informe Seguridad",
        "btn_sha": "Verificar SHA-256",
        "mode_filename": "Nombre",
        "mode_content": "Texto completo",
        "btn_search": "Buscar",
        "col_path": "Ruta en el archivo",
        "col_size": "Tamaño",
        "col_comp": "Comprimido",
        "col_type": "Tipo",
        "folder": "Carpeta",
        "file": "Archivo",
        "quick_look": "Quick Look (Vista previa sin extraer)",
        "welcome_text": (
            "Selecciona un archivo de texto, código o imagen dentro de un archivo\n"
            "para verlo al instante en memoria sin extraerlo al disco.\n\n"
            "Ventajas incluidas:\n"
            "- Escaneo automático contra path traversal y dobles extensiones\n"
            "- Búsqueda de texto completo dentro de archivos comprimidos\n"
            "- Creación de archivos .tar.zst (Zstandard), .7z, .zip, .tar.gz\n"
            "- Smart Dev Exclude (omite node_modules, .git, __pycache__, dist)\n"
            "- 100% Gratis, Sin Anuncios — by Kasuality"
        ),
        "footer_brand": "100% Free • Zero Ads • by Kasuality (kasuality.com)",
        "badge_safe": "SEGURO ({n} archivos verificados)",
        "badge_warn": "ADVERTENCIA ({n} avisos)",
        "badge_danger": "PELIGRO ({n} amenazas)",
        "binary_preview": "Archivo binario ({size}).\nVista previa de texto no disponible.",
        "non_text_preview": "Archivo: {name}\nTamaño: {size}\n\nUsa 'Extracción Segura' para abrirlo.",
        "extract_done": "{count} elementos extraídos en:\n{path}",
        "new_title": "Nuevo Archivo — by Kasuality",
        "source_label": "Origen: {name}",
        "format_label": "Formato de archivo:",
        "smart_dev_label": "Smart Dev Exclude (omite node_modules, .git, __pycache__, dist, .venv)",
        "level_label": "Nivel de compresión (1 = rápido, 9 = máx):",
        "btn_create": "Crear Archivo",
        "created_msg": "Creado: {name}\nArchivos incluidos: {count}\nTamaño final: {size}\n\nSHA-256:\n{sha}",
        "sha_copied": "Archivo: {name}\n\nSHA-256:\n{sha}\n\n(Copiado al portapapeles)",
        "not_archive_prompt": "'{name}' no es un archivo comprimido.\n¿Quieres comprimirlo en un nuevo archivo ahora?",
        "extract_selected_prompt": "Has seleccionado {n} elemento(s).\n\nSí = Extraer SOLO seleccionados\nNo = Extraer TODO el archivo\nCancelar = Salir",
        "ctx_extract_selected": "Extraer solo seleccionados",
        "lang_label": "Idioma:",
    },
    "de": {
        "app_title": "Kasuality Archiver — by Kasuality",
        "no_archive": "Kein Archiv geöffnet",
        "ready_status": "Bereit. Öffne ein Archiv oder erstelle eines mit Smart Dev Exclude.",
        "btn_open": "Archiv öffnen",
        "btn_new": "Neues Archiv",
        "btn_extract": "Sicher entpacken",
        "btn_security": "Sicherheitsbericht",
        "btn_sha": "SHA-256 prüfen",
        "mode_filename": "Dateiname",
        "mode_content": "Volltext in Dateien",
        "btn_search": "Suchen",
        "col_path": "Pfad im Archiv",
        "col_size": "Größe",
        "col_comp": "Komprimiert",
        "col_type": "Typ",
        "folder": "Ordner",
        "file": "Datei",
        "quick_look": "Quick Look (Vorschau ohne Entpacken)",
        "welcome_text": (
            "Wähle eine Text-, Code- oder Bilddatei in einem Archiv aus,\n"
            "um sie sofort im Speicher anzuzeigen, ohne sie zu entpacken.\n\n"
            "Enthaltene Vorteile:\n"
            "- Automatischer Scan auf Path-Traversal und doppelte Endungen\n"
            "- Volltextsuche innerhalb komprimierter Dateien\n"
            "- Erstellt .tar.zst (Zstandard), .7z, .zip, .tar.gz Archive\n"
            "- Smart Dev Exclude (überspringt node_modules, .git, __pycache__, dist)\n"
            "- 100% Kostenlos, Keine Werbung — by Kasuality"
        ),
        "footer_brand": "100% Free • Zero Ads • by Kasuality (kasuality.com)",
        "badge_safe": "SICHER ({n} Dateien geprüft)",
        "badge_warn": "WARNUNG ({n} Hinweise)",
        "badge_danger": "GEFAHR ({n} Bedrohungen)",
        "binary_preview": "Binärdatei ({size}).\nTextvorschau nicht verfügbar.",
        "non_text_preview": "Datei: {name}\nGröße: {size}\n\nNutze 'Sicher entpacken' zum Öffnen.",
        "extract_done": "{count} Elemente entpackt nach:\n{path}",
        "new_title": "Neues Archiv — by Kasuality",
        "source_label": "Quelle: {name}",
        "format_label": "Archivformat:",
        "smart_dev_label": "Smart Dev Exclude (überspringt node_modules, .git, __pycache__, dist, .venv)",
        "level_label": "Kompressionsstufe (1 = schnell, 9 = max):",
        "btn_create": "Archiv erstellen",
        "created_msg": "Erstellt: {name}\nDateien: {count}\nEndgröße: {size}\n\nSHA-256:\n{sha}",
        "sha_copied": "Datei: {name}\n\nSHA-256:\n{sha}\n\n(In Zwischenablage kopiert)",
        "not_archive_prompt": "'{name}' ist kein komprimiertes Archiv.\nMöchtest du es jetzt in ein neues Archiv komprimieren?",
        "extract_selected_prompt": "Du hast {n} Element(e) ausgewählt.\n\nJa = NUR ausgewählte entpacken\nNein = ALLES entpacken\nAbbrechen = Zurück",
        "ctx_extract_selected": "Nur ausgewählte entpacken",
        "lang_label": "Sprache:",
    },
}


def detect_default_lang() -> str:
    try:
        loc = locale.getlocale()[0] or ""
    except Exception:
        loc = ""
    short = loc[:2].lower()
    return short if short in SUPPORTED_LANGS else "en"


def tr(lang: str, key: str, **kwargs) -> str:
    table = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = table.get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**kwargs) if kwargs else template

"""Cifra los agregados de web/data/*.json en un único bundle protegido por contraseña.

Solo el archivo CIFRADO (web/secure/bundle.enc.json) se publica; el plaintext con
scores se queda local. Compatible con WebCrypto (PBKDF2-SHA256 + AES-256-GCM).

Uso:  OBS_PASSWORD='tu-passphrase-larga' python scripts/encrypt_web.py
La passphrase NO se guarda en ningún lado: quien la tenga puede descifrar en el navegador.
"""
from __future__ import annotations
import base64
import json
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web" / "data"
OUT = ROOT / "web" / "secure" / "bundle.enc.json"
ITER = 310_000


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def main() -> None:
    pw = os.getenv("OBS_PASSWORD")
    if not pw:
        sys.exit("Define OBS_PASSWORD (passphrase larga). Ej: OBS_PASSWORD='...' python scripts/encrypt_web.py")
    if len(pw) < 12:
        print("⚠️  Passphrase corta: el bundle es público; usa 16+ caracteres aleatorios.")

    bundle = {}
    for name in ("ice", "stats", "rotacion"):
        p = DATA / f"{name}.json"
        if not p.exists():
            sys.exit(f"Falta {p}. Corre antes: make etl && python scripts/export_web.py")
        bundle[name] = json.loads(p.read_text(encoding="utf-8"))
    plaintext = json.dumps(bundle, ensure_ascii=False).encode("utf-8")

    salt = os.urandom(16)
    iv = os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, plaintext, None)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "v": 1, "kdf": "PBKDF2", "hash": "SHA-256", "iter": ITER,
        "salt": b64(salt), "iv": b64(iv), "ct": b64(ct),
        "nota": "Datos preliminares cifrados. Sin la passphrase no son legibles.",
    }, indent=2), encoding="utf-8")
    print(f"✓ Cifrado: {OUT}  ({len(ct)} bytes ciphertext, {len(plaintext)} plaintext)")
    print("  El plaintext en web/data/ NO se publica (gitignored).")


if __name__ == "__main__":
    main()

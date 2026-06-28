"""Harvey LegalReviewer — PDF/DOCX text extraction + Ollama legal analysis.

Python equivalent of integrations/telegram/src/legal_review.ts (free portion).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.ollama import OllamaClient  # noqa: E402

log = logging.getLogger("harvey.legal")

USAGE_DIR = Path(os.getenv(
    "HARVEY_USAGE_DIR",
    Path("/var/lib/harvey/legal_usage"),
))
USAGE_DIR.mkdir(parents=True, exist_ok=True)

FREE_REVIEWS = int(os.getenv("HARVEY_FREE_REVIEWS", "2"))
MODEL = os.getenv("HARVEY_MODEL", "deepseek-r1:32b")
FALLBACK_MODEL = os.getenv("HARVEY_FALLBACK_MODEL", "qwen3:32b")
PAYMENT_LINK = os.getenv("STRIPE_PAYMENT_LINK", "")
MONTHLY_PRICE = os.getenv("LEGAL_MONTHLY_PRICE", "49€")
PER_DOC_PRICE = os.getenv("LEGAL_PER_DOC_PRICE", "9€")


SYSTEM_PROMPT = """Du bist Harvey, ein juristischer Berater im Stil von Harvey Specter.
Kalt, präzise, ergebnisorientiert.

Antwort-Format (Pflicht):
1. Risiko-Gesamt: <1-10>
2. Empfehlung: <Verteidigen / Vergleichen / Ignorieren / Eskalieren>
3. Behauptungen der Gegenseite (Liste)
4. Schwachstellen der Gegenseite (Liste)
5. Unsere Verteidigung (Liste)
6. Risiko-Tabelle (Markdown mit | # | Punkt | Risiko | Begründung |)
7. Vorgeschlagene Aktion (Schritte 1-3)
8. Disclaimer: "Keine Rechtsberatung. Indikation auf Basis der vorliegenden Dokumente."

Wenn unsicher: "Hier Anwalt einbinden". KEINE Halluzinationen bei Rechtsgrundlagen.
"""


class LegalReviewer:
    def __init__(self) -> None:
        self.ollama = OllamaClient()

    async def handle(self, payload: dict, intent: str) -> dict:
        user_id = str(payload.get("user_id", "unknown"))
        text = payload.get("text", "").strip()
        file_path = payload.get("file_path")
        doc_text = ""

        if file_path:
            doc_text = self._extract_text(Path(file_path))
        elif text:
            doc_text = text

        if not doc_text:
            return {
                "reply": "[Harvey] Kein Dokument oder Text bekommen.",
                "status": "no_input",
            }

        usage = self._load_usage(user_id)
        if not usage.get("paid", False) and usage.get("free_used", 0) >= FREE_REVIEWS:
            return {
                "reply": self._paywall_message(),
                "paywall": True,
                "free_used": usage.get("free_used", 0),
            }

        # Run review
        prompt = f"Bitte prüfe folgendes Dokument im Harvey-Format:\n\n{doc_text[:30_000]}"
        try:
            review = await self.ollama.chat(
                MODEL,
                [{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}],
                temperature=0.2,
            )
        except Exception as e:
            log.warning("Primary model %s failed, trying fallback: %s", MODEL, e)
            try:
                review = await self.ollama.chat(
                    FALLBACK_MODEL,
                    [{"role": "system", "content": SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
                    temperature=0.2,
                )
            except Exception as e2:
                return {"reply": f"[Harvey] LLM nicht erreichbar: {e2}", "status": "llm_down"}

        usage["free_used"] = usage.get("free_used", 0) + (0 if usage.get("paid") else 1)
        usage["review_count"] = usage.get("review_count", 0) + 1
        usage["last_review"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._save_usage(user_id, usage)

        return {
            "reply": review,
            "intent": intent,
            "free_used": usage["free_used"],
            "free_remaining": max(0, FREE_REVIEWS - usage["free_used"]),
            "paid": usage.get("paid", False),
            "status": "done",
        }

    def _extract_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(errors="replace")
        if suffix == ".pdf":
            return self._pdf_to_text(path)
        if suffix in (".docx", ".doc"):
            return self._docx_to_text(path)
        return path.read_text(errors="replace")

    def _pdf_to_text(self, path: Path) -> str:
        if shutil.which("pdftotext"):
            try:
                r = subprocess.run(
                    ["pdftotext", "-layout", str(path), "-"],
                    capture_output=True, text=True, timeout=60,
                )
                if r.returncode == 0:
                    return r.stdout
            except Exception as e:
                log.debug("pdftotext failed: %s", e)
        try:
            from pypdf import PdfReader  # type: ignore
            reader = PdfReader(str(path))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            log.warning("pypdf failed: %s", e)
            return ""

    def _docx_to_text(self, path: Path) -> str:
        try:
            import docx2txt  # type: ignore
            return docx2txt.process(str(path))
        except Exception as e:
            log.warning("docx2txt failed: %s", e)
            return ""

    def _usage_path(self, user_id: str) -> Path:
        return USAGE_DIR / f"{user_id}.json"

    def _load_usage(self, user_id: str) -> dict:
        p = self._usage_path(user_id)
        if not p.exists():
            return {"userId": user_id, "free_used": 0, "paid": False, "review_count": 0}
        try:
            return json.loads(p.read_text())
        except Exception:
            return {"userId": user_id, "free_used": 0, "paid": False, "review_count": 0}

    def _save_usage(self, user_id: str, data: dict) -> None:
        self._usage_path(user_id).write_text(json.dumps(data, indent=2))

    def _paywall_message(self) -> str:
        link = f"\n\n→ Zahlung: {PAYMENT_LINK}" if PAYMENT_LINK else ""
        return (
            f"[Harvey] Deine {FREE_REVIEWS} kostenlosen Reviews sind aufgebraucht.\n\n"
            f"Tarife:\n"
            f"• {MONTHLY_PRICE}/Monat — unbegrenzt\n"
            f"• {PER_DOC_PRICE} pro Dokument — Einzelkauf\n"
            f"{link}\n\n"
            f"Disclaimer: Keine Rechtsberatung. Indikation auf Basis vorliegender Dokumente."
        )

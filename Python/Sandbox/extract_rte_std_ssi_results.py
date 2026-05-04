from logger import logger_config
from docx import Document
from typing import Dict
import pandas as pd
import re


def main() -> None:
    with logger_config.application_logger():
        # Purpose: EXACT extraction per your rules
        # - Action: cell immediately to the RIGHT of the row containing "Action(s) :"
        # - Résultat attendu: cell immediately to the RIGHT of the row containing "Résultat attendu"
        # - Résultat observé: cell immediately to the RIGHT of the row containing "Résultat observé"

        path = r"C:\Users\fr232487\Downloads\RTE STD SSI pour IA.docx"
        doc = Document(path)

        rows = []
        current_test = None
        current_exigences = ""
        current_conclusion = ""

        def clean(t: str) -> str:
            return t.strip() if t else ""

        for table in doc.tables:
            full_text = " ".join(clean(cell.text) for row in table.rows for cell in row.cells)

            # Detect TEST_SECU_ARCH
            m = re.search(r"TEST_SECU_ARCH_\s*(\d+)", full_text)
            if m:
                current_test = f"TEST_SECU_ARCH_{m.group(1)}"

            # Exigences SSI
            if "Exigences SSI" in full_text or "Exigence SSI" in full_text:
                exigs = []
                for row in table.rows:
                    for cell in row.cells:
                        exigs += re.findall(r"SSI-\d+", cell.text)
                current_exigences = ", ".join(sorted(set(exigs)))

            # Conclusion globale (verbatim short cells)
            for row in table.rows:
                for cell in row.cells:
                    txt = clean(cell.text)
                    if txt in ["OK", "OKR", "OKP", "KO", "KO (design)"]:
                        current_conclusion = txt

            # --- PER-STEP maps ---
            actions: Dict[str, str] = {}
            attendus: Dict[str, str] = {}
            observes: Dict[str, str] = {}

            def extract_per_step(section_label: str, target_dict: Dict[str, str]) -> None:
                for i, row in enumerate(table.rows):
                    if section_label in row.cells[0].text:
                        # subsequent rows with step numbers
                        for r in table.rows[i + 1 :]:
                            step = clean(r.cells[0].text)
                            if not step or not step[0].isdigit():
                                break
                            # content is cell to the RIGHT of step number (or last cell if merged)
                            content = clean(r.cells[-1].text)
                            target_dict[step] = content
                        break

            extract_per_step("Action", actions)
            extract_per_step("Résultat attendu", attendus)
            extract_per_step("Résultat observé", observes)

            # --- Conformité résultat per step ---
            for i, row in enumerate(table.rows):
                if "Conformité résultat" in row.cells[0].text:
                    for r in table.rows[i + 2 :]:
                        step = clean(r.cells[0].text)

                        raw_OK_column = r.cells[1]
                        raw_OKR_column = r.cells[2]
                        raw_KO_column = r.cells[3]
                        if not step or not step[0].isdigit():
                            continue
                        commentaire = clean(r.cells[-1].text)
                        cl = commentaire.lower()

                        ok_present = bool(clean(raw_OK_column.text))
                        okr_present = bool(clean(raw_OKR_column.text))
                        ko_present = bool(clean(raw_KO_column.text))

                        if "non testé" in cl:
                            statut = "Non testé"
                        elif cl.startswith("ko"):
                            statut = "KO"
                        elif cl.startswith("okr"):
                            statut = "OKR"
                        elif cl.startswith("ok"):
                            statut = "OK"
                        else:
                            statut = ""

                        rows.append(
                            {
                                "Test": current_test,
                                "Étape": step,
                                "Action": actions.get(step, ""),
                                "Résultat attendu": attendus.get(step, ""),
                                "Résultat observé": observes.get(step, ""),
                                "Commentaire": commentaire,
                                "Statut": statut,
                                "OK": ok_present,
                                "OKR": okr_present,
                                "KO": ko_present,
                                "CFX à créer": "Oui" if "cfx" in cl else "Non",
                                "Non testé": "Oui" if "non testé" in cl else "Non",
                                "Exigences SSI": current_exigences,
                                "Conclusion du test": current_conclusion,
                            }
                        )

        # Export corrected Excel
        out = r"D:\Temp\resultats_tests_SSI_complet.xlsx"
        pd.DataFrame(rows).to_excel(out, index=False)
        out


if __name__ == "__main__":
    main()

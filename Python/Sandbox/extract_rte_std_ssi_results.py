from logger import logger_config
from docx import Document
import pandas as pd
import re


def main() -> None:
    with logger_config.application_logger():
        # Purpose: EXACT extraction per your rules
        # - Action: cell immediately to the RIGHT of the row containing "Action(s) :"
        # - Résultat attendu: cell immediately to the RIGHT of the row containing "Résultat attendu"
        # - Résultat observé: cell immediately to the RIGHT of the row containing "Résultat observé"

        path = r"C:\Users\fr232487\Downloads\RTE STD SSI pour IA light.docx"
        doc = Document(path)

        rows = []
        current_test = None
        current_exigences = ""
        current_conclusion = ""

        def clean(t: str) -> str:
            return t.replace("\n", " ").strip() if t else ""

        for table in doc.tables:
            # Detect TEST_SECU_ARCH
            full_text = " ".join(cell.text for row in table.rows for cell in row.cells)
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

            # Conclusion globale
            for row in table.rows:
                for cell in row.cells:
                    txt = clean(cell.text)
                    if txt in ["OK", "OKR", "OKP", "KO", "KO (design)"]:
                        current_conclusion = txt

            # === Extract block-level fields (NOT per step) ===
            action_bloc = ""
            resultat_attendu_bloc = ""
            resultat_observe_bloc = ""

            for row in table.rows:
                if "Action(s)" in row.cells[0].text and len(row.cells) > 1:
                    action_bloc = clean(row.cells[1].text)
                if "Résultat attendu" in row.cells[0].text and len(row.cells) > 1:
                    resultat_attendu_bloc = clean(row.cells[1].text)
                if "Résultat observé" in row.cells[0].text and len(row.cells) > 1:
                    resultat_observe_bloc = clean(row.cells[1].text)

            # === Conformité résultat (per step) ===
            for i, row in enumerate(table.rows):
                if "Conformité résultat" in row.cells[0].text:
                    for r in table.rows[i + 2 :]:
                        step = clean(r.cells[0].text)
                        if not step or not step[0].isdigit():
                            continue

                        commentaire = clean(r.cells[-1].text)
                        cl = commentaire.lower()

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
                                "Action": action_bloc,
                                "Résultat attendu": resultat_attendu_bloc,
                                "Résultat observé": resultat_observe_bloc,
                                "Commentaire": commentaire,
                                "Statut": statut,
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

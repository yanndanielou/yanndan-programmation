import pandas as pd
import matplotlib.pyplot as plt
import datetime

import cfx


# Charger les données depuis le fichier Excel
df = pd.read_excel("extract_cfx.xlsx")

entries = [cfx.ChampFXEntry(row) for _, row in df.iterrows()]


# Créer le tableau croisé dynamique
state_mapping = {
    "Submitted": "Submitted",
    "Analysed": "Analysed",
    "Assigned": "Resolved",
    "Resolved": "Resolved",
    "Rejected": "Resolved",
    "Postponed": "Resolved",
    "Verified": "Verified",
    "Validated": "Validated",
    "Closed": "Closed",
}
pivot_table = pd.DataFrame([entry.__dict__ for entry in entries])
pivot_table["State"] = pivot_table["state"].map(state_mapping)
pivot_table = pivot_table.pivot_table(index=["State", "year", "month"], aggfunc="size", fill_value=0)

# Tracer le graphique
fig, ax = plt.subplots(figsize=(12, 6))

for state in ["Submitted", "Analysed", "Resolved", "Verified", "Validated", "Closed"]:
    data = pivot_table.loc[state].unstack(fill_value=0)
    data.plot(kind="area", ax=ax, label=state)

ax.set_xlabel("Mois")
ax.set_ylabel("Nombre de CFX")
ax.set_title("Évolution du cycle de vie des CFX")
ax.legend()
plt.xticks(rotation=45)
plt.show()

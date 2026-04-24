import streamlit as st
import pandas as pd

st.set_page_config(page_title="Messrechner Netzwerkzonen", layout="wide")
st.title("🖥️ Messrechner – Netzwerkzonen")

st.markdown("### Deine Anforderungen")

ad_joined = st.checkbox(f"**AD-Join**: Mein Messrechner benötigt die Anmeldung mit einem AD Passwort", value=True)
os_update = st.checkbox(f"**OS-Update**: Mein Messrechner läuft mit einem fortlaufend aktualisiertem Betriebssystem", value=True)
cortex = st.checkbox(f"**Cortex**: Mein Messrechner läuft mit aktualisiertem Cortex als Bedrohungsschutz (EndPoint Protect)", value=True)
shared_drives = st.checkbox(f"**Shared Drives**: Mein Messrechner benötigt Zugriff auf die Laufwerke G: K: N: P: R:", value=False)
if not shared_drives:
    x_drive = st.checkbox(f"**Transfer-Drive**: Ich akzeptiere das Laufwerk X als Alternative zu den Laufwerken G: K: N: P: R:", value=False)
else:
    x_drive = True
internet = st.checkbox(f"**Internet**: Mein Messrechner benötigt Internet Zugriff", value=False)
printer = st.checkbox(f"**Drucker**: Mein Messrechner muss auf einem internen Drucker drucken können", value=False)

user = [ad_joined, os_update, cortex, shared_drives, x_drive, internet, printer]

kriterien_namen = [
    "AD Joined",
    "OS Update",
    "Cortex",
    "Shared Drives G/K/N/P/R",
    "X-Drive akzeptiert",
    "Internet Access",
    "EMPA Drucker"
]

zone_rules = {
    "B1": [(1,1), (1,0), (1,0), (1,1), (1,1), (0,1), (1,1)],
    "B2": [(1,0), (1,0), (1,0), (1,1), (1,1), (1,0), (1,1)],
    "D1": [(1,0), (1,1), (1,1), (0,1), (1,0), (0,1), (1,1)],
    "C1": [(0,1), (1,1), (1,1), (0,1), (1,0), (0,1), (0,1)],
    "E1": [(0,1), (1,1), (1,1), (0,1), (1,0), (1,0), (0,1)]
}

# Berechnung der Punktzahlen
scores = {}
for zone, rules in zone_rules.items():
    score = sum(true_val if u else false_val for u, (true_val, false_val) in zip(user, rules))
    scores[zone] = score

max_score = max(scores.values())
MAXIMALWERT = 7

# Beste Zone mit Priorität
if scores["B1"] == MAXIMALWERT:
    best_zone = "B1"
elif scores["B2"] == MAXIMALWERT:
    best_zone = "B2"
elif scores["D1"] == MAXIMALWERT:
    best_zone = "D1"
elif scores["C1"] == MAXIMALWERT:
    best_zone = "C1"
elif scores["E1"] == MAXIMALWERT:
    best_zone = "E1"
else:
    best_zone = max(scores, key=scores.get)

has_veeam = best_zone in ["B1", "B2", "D1"]

# ==================== ERGEBNIS ====================
st.markdown("---")
st.subheader("Gesamtresultat")

if max_score == MAXIMALWERT:
    st.success(f"**ZONE {best_zone}**")
    if has_veeam:
        st.info("**VEEAM-Backup möglich durch die IT**")
    else:
        st.warning("**Kein VEEAM-Backup durch die IT**")
else:
    st.error("**Keine Netzwerkzuordnung möglich**")

# ==================== TIPPS – ALLE MÖGLICHEN LÖSUNGEN (5 oder 6 Punkte) ====================
if max_score < MAXIMALWERT:
    st.markdown("---")
    st.markdown("### 💡 Mögliche Lösungen")
    st.write("Hier sind **alle Zonen**, die mit nur wenigen Änderungen erreichbar sind (5 oder 6 Punkte):")

    # Alle Zonen mit mindestens 5 Punkten
    viable_zones = {z: s for z, s in scores.items() if s >= 5}
    viable_zones = dict(sorted(viable_zones.items(), key=lambda x: x[1], reverse=True))

    for zone, score in viable_zones.items():
        st.subheader(f"**ZONE {zone}** – {score}/7 Punkte")
       
        conflicts = []
        for i, (u, (true_val, false_val)) in enumerate(zip(user, zone_rules[zone])):
            if (true_val if u else false_val) == 0:
                aktuell = "aktiviert" if u else "deaktiviert"
                empfehlung = "deaktivieren" if u else "aktivieren"
                conflicts.append(f"→ **{kriterien_namen[i]}** (aktuell {aktuell} → bitte {empfehlung})")
       
        if conflicts:
            for tipp in conflicts:
                st.write(tipp)
        else:
            st.write("✅ Alle Kriterien passen bereits perfekt.")

# ==================== DETAILLIERTE TABELLE MIT CONDITIONAL FORMATTING ====================
st.markdown("---")
st.markdown("### Detaillierte Übersicht")

data = {
    "Kriterium": [
        "AD Joined", "OS Update", "Cortex", "Shared Drives G/K/N/P/R", "X-Drive akzeptiert",
        "Internet Access", "EMPA Drucker",
        "Erfüllte Kriterien"
    ],
    "TRIFFT Zu": ["✅" if x else "❌" for x in user] + [""],
}

for zone in ["B1", "B2", "D1", "C1", "E1"]:
    values = []
    for u, (true_val, false_val) in zip(user, zone_rules[zone]):
        result = true_val if u else false_val
        values.append("✅" if result == 1 else "❌")
    values.append(scores[zone])
    data[f"ZONE {zone}"] = values

df = pd.DataFrame(data)

def style_table(row):
    styles = [''] * len(row)
    if row.name == 7:
        styles[0] = 'font-weight: bold'
        max_val = max(scores.values())
        for i, zone in enumerate(["B1", "B2", "D1", "C1", "E1"], start=2):
            if row.iloc[i] == max_val:
                styles[i] = 'background-color: #28a745; color: white; font-weight: bold'
            elif row.iloc[i] >= 5:
                styles[i] = 'background-color: #ffc107; color: black'
    else:
        for i, cell in enumerate(row[2:7], start=2):
            if cell == "✅":
                styles[i] = 'background-color: #d4edda; color: #155724'
            else:
                styles[i] = 'background-color: #f8d7da; color: #721c24'
    return styles

styled_df = df.style.apply(style_table, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True)
 

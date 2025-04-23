import streamlit as st
import matplotlib.pyplot as plt

class RealEstateAnalyzer:
    def __init__(self, prezzo_acquisto: float, spese_extra: float, costo_ristrutturazione: float = 0,
                 finanziamento: bool = False, percentuale_mutuo: float = 0.8,
                 tasso_interesse: float = 0.04, durata_anni: int = 20):
        self.prezzo_acquisto = prezzo_acquisto
        self.spese_extra = spese_extra
        self.costo_ristrutturazione = costo_ristrutturazione
        self.finanziamento = finanziamento
        self.percentuale_mutuo = percentuale_mutuo
        self.tasso_interesse = tasso_interesse
        self.durata_anni = durata_anni
        self.costo_totale = prezzo_acquisto + spese_extra + costo_ristrutturazione
        self._calcola_mutuo()
    
    def _calcola_mutuo(self):
        if self.finanziamento:
            capitale = self.prezzo_acquisto * self.percentuale_mutuo
            r = self.tasso_interesse / 12
            n = self.durata_anni * 12
            self.rata_mensile = capitale * (r * (1 + r)**n) / ((1 + r)**n - 1)
            self.costo_totale_mutuo = self.rata_mensile * n
        else:
            self.rata_mensile = 0
            self.costo_totale_mutuo = 0

    def buy_to_rent(self, canone_mensile: float, tasso_occupazione: float, spese_annue: float):
        entrate_annue = canone_mensile * 12 * tasso_occupazione
        cash_flow_annuo = entrate_annue - spese_annue - self.rata_mensile * 12
        ROI = (cash_flow_annuo / self.costo_totale) * 100
        break_even_anni = self.costo_totale / cash_flow_annuo if cash_flow_annuo > 0 else None
        return {
            "Entrate annue": entrate_annue,
            "Cash flow annuo": cash_flow_annuo,
            "ROI (%)": ROI,
            "Break-even (anni)": break_even_anni
        }

    def short_term_rent(self, tariffa_notte: float, occupazione_media: float, spese_annue: float):
        entrate_annue = tariffa_notte * 365 * occupazione_media
        cash_flow_annuo = entrate_annue - spese_annue - self.rata_mensile * 12
        ROI = (cash_flow_annuo / self.costo_totale) * 100
        break_even_anni = self.costo_totale / cash_flow_annuo if cash_flow_annuo > 0 else None
        return {
            "Entrate annue": entrate_annue,
            "Cash flow annuo": cash_flow_annuo,
            "ROI (%)": ROI,
            "Break-even (anni)": break_even_anni
        }

    def flipping(self, valore_rivendita: float, tasse_su_plusvalenza: float = 0.2):
        utile_lordo = valore_rivendita - self.costo_totale
        tasse = utile_lordo * tasse_su_plusvalenza
        utile_netto = utile_lordo - tasse
        ROI = (utile_netto / self.costo_totale) * 100
        return {
            "Utile lordo": utile_lordo,
            "Utile netto": utile_netto,
            "ROI (%)": ROI
        }

st.title("Analisi investimento immobiliare - Rex Consulting")

strategia = st.selectbox("Seleziona la strategia", ["Buy to Rent", "Short Term Rent", "Flipping"])

with st.sidebar:
    st.header("Dati generali immobile")
    prezzo = st.number_input("Prezzo d'acquisto (€)", value=150000)
    spese = st.number_input("Spese extra (€)", value=10000)
    lavori = st.number_input("Costo ristrutturazione (€)", value=20000)
    finanziamento = st.checkbox("Usi un mutuo?", value=True)
    if finanziamento:
        percentuale = st.slider("Percentuale mutuo", 0.0, 1.0, 0.8)
        tasso = st.number_input("Tasso interesse (%)", value=4.0) / 100
        anni = st.number_input("Durata mutuo (anni)", value=20)
    else:
        percentuale = 0.0
        tasso = 0.0
        anni = 0

analyzer = RealEstateAnalyzer(prezzo, spese, lavori, finanziamento, percentuale, tasso, anni)

if strategia == "Buy to Rent":
    st.subheader("Parametri Buy to Rent")
    affitto = st.number_input("Canone mensile (€)", value=850)
    occupazione = st.slider("Tasso occupazione (%)", 0.0, 1.0, 0.95)
    spese_annue = st.number_input("Spese annuali (€)", value=1500)
    risultati = analyzer.buy_to_rent(affitto, occupazione, spese_annue)

elif strategia == "Short Term Rent":
    st.subheader("Parametri Short Term Rent")
    prezzo_notte = st.number_input("Prezzo per notte (€)", value=60)
    occupazione_breve = st.slider("Occupazione media (%)", 0.0, 1.0, 0.65)
    spese_annue = st.number_input("Spese annuali (€)", value=3000)
    risultati = analyzer.short_term_rent(prezzo_notte, occupazione_breve, spese_annue)

else:
    st.subheader("Parametri Flipping")
    rivendita = st.number_input("Valore atteso di rivendita (€)", value=220000)
    tasse_plusvalenza = st.slider("Tassazione su plusvalenza (%)", 0.0, 0.5, 0.2)
    risultati = analyzer.flipping(rivendita, tasse_plusvalenza)

st.subheader("Risultati")
for k, v in risultati.items():
    st.write(f"**{k}**: {round(v, 2) if isinstance(v, float) else v}")

if st.button("Genera report PDF"):
    fig, ax = plt.subplots()
    ax.bar(["ROI"], [risultati["ROI (%)"]])
    ax.set_ylabel("ROI (%)")
    ax.set_title("Ritorno sull'investimento (ROI)")
    plt.tight_layout()
    graph_path = "roi_chart.png"
    fig.savefig(graph_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Report Analisi Investimento Immobiliare - Rex Consulting", ln=True, align='C')
    pdf.ln(10)
    for key, value in risultati.items():
        val = str(value) if value is not None else "N/A"
        pdf.cell(200, 10, txt=f"{key}: {val}", ln=True)
    pdf.ln(10)
    pdf.image(graph_path, x=10, w=100)
    pdf.output("report.pdf")
    with open("report.pdf", "rb") as f:
        st.download_button("Scarica il report PDF", f, file_name="analisi_investimento.pdf")




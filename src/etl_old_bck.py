import logging
import pandas as pd

logger = logging.getLogger(__name__)

def calcola_paga_giornaliera(ore_lavorate: float, paga_oraria: float) -> float:
    if ore_lavorate is None:
        ore_lavorate = 0.0
 
    if ore_lavorate <= 8.0:
        return ore_lavorate * paga_oraria
    else:
        ore_normali = 8.0 * paga_oraria
        ore_extra = (ore_lavorate - 8.0) * paga_oraria * 1.5
        return ore_normali + ore_extra


def extract(dipendenti_path: str, presenze_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estrae i dati dai file CSV."""
    df_dipendenti = pd.read_csv(dipendenti_path)
    df_presenze = pd.read_csv(presenze_path)
    return df_dipendenti, df_presenze

def transform(df_dipendenti: pd.DataFrame, df_presenze: pd.DataFrame) -> pd.DataFrame:
    #Trasforma i dati: merge, filtri e aggregazioni.
    # 1. Merge tra dipendenti e presenze
    df_merged = pd.merge(df_dipendenti, df_presenze, on="id_dipendente", how="inner")
    df_merged.loc[df_merged["ore_lavorate"].isnull(), "ore_lavorate"] = 0

    # 2. Creiamo colonne aggiuntive con ore straordinari, paga per ore standard, paga per straordinari
    df_split_ore = df_merged.copy()
    df_split_ore["ore_straordinari"] = (df_split_ore["ore_lavorate"] - 8).clip(lower=0)
    df_split_ore["paga_standard"] = (df_split_ore["ore_lavorate"]-df_split_ore["ore_straordinari"]) * df_split_ore["paga_oraria"]
    df_split_ore["paga_straordinari"] = df_split_ore["ore_straordinari"] * df_split_ore["paga_oraria"] * 1.5

    return df_split_ore 

    #print("APPO ", df_split_ore)

    # 3. Aggreghiamo i dati 
    # df_report = df_split_ore.groupby(["id_dipendente", "nome", "cognome", "dipartimento"]).agg(
    #     tot_straordinari=("ore_straordinari", "sum"),
    #    # stipendio=("paga_standard", "sum")
    #     stipendio=(
    #         "paga_standard",
    #         lambda s: (s + df_split_ore.loc[s.index, "paga_straordinari"]).sum()
    #     )

    # ).reset_index()   

    # return df_report   

"""   
    # 4. Aggreghiamo i dati per capire quanto ha speso ogni cliente in totale
    df_report = df_filtered.groupby(["cliente_id", "nome", "cognome", "email"]).agg(
        numero_ordini=("ordine_id", "count"),
        totale_speso=("totale_riga", "sum")
    ).reset_index()
    
    # 5. Ordiniamo per chi ha speso di più
    df_report = df_report.sort_values(by="totale_speso", ascending=False)
 """   


def load(df_transformed: pd.DataFrame, output_path: str):
    #Carica i dati elaborati in un nuovo file CSV.
    df_transformed.to_csv(output_path, index=False)
    logger.info(f"Dati caricati con successo in: {output_path}")


import logging
import pandas as pd
from typing import Tuple

logger = logging.getLogger(__name__)

# -----------------------
# EXTRACT
# -----------------------
def extract(
    dipendenti_path: str,
    presenze_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ 
    Riceve in input i path dei file csv source
    e restituisce una lista di altrettanti DataFrame
    """
    logger.info("Estrazione dati dai CSV")
    df_dipendenti = pd.read_csv(dipendenti_path)
    df_presenze = pd.read_csv(presenze_path)
    return df_dipendenti, df_presenze

# -----------------------
# TRANSFORM 
# -----------------------
def transform(
    df_dipendenti: pd.DataFrame,
    df_presenze: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge dei due DataFrame ricevuti in input
    e gestione colonne:
       ore_lavorate: sostituisce valore NaN con 0
       ore_standard: calcolata, ore lavorate ridotte a 8 se > 8
       ore_straordinari: calcolata, ore lavorate eccedenti le 8 ore
       paga_standard: calcolata, importo dovuto per ore standard
       paga_straordinari: calcolata, importo dovuto per ore straordinario, comprensivo di maggiorazione 50% 
       compenso_giornaliero: calcolata, importo dovuto per il totale delle ore standard e straordinario   
    """
    df_merged = pd.merge(
        df_dipendenti,
        df_presenze,
        on="id_dipendente",
        how="left"
    )

    df_merged["ore_lavorate"] = df_merged["ore_lavorate"].fillna(0.0)

    # 2. Crea colonne aggiuntive con ore divise in standard e straordinari, paga per ore standard, paga per straordinari
    df_add_paga = df_merged.copy()
    df_add_paga["ore_standard"] = (df_add_paga["ore_lavorate"]).clip(lower=0, upper=8)    
    df_add_paga["ore_straordinari"] = (df_add_paga["ore_lavorate"] - 8).clip(lower=0)
    ##
    df_add_paga["paga_standard"] = df_add_paga["ore_standard"] * df_add_paga["paga_oraria"]
    df_add_paga["paga_straordinari"] = df_add_paga["ore_straordinari"] * df_add_paga["paga_oraria"] * 1.5   
    ##
    df_add_paga["compenso_giornaliero"] = (
                                          (df_add_paga["ore_standard"] * df_add_paga["paga_oraria"])
                                          + (df_add_paga["ore_straordinari"] * df_add_paga["paga_oraria"] * 1.5)) 
    
    logger.debug("Transform completata. Righe: %d", len(df_merged))
    return df_add_paga


# -----------------------
# DATAFRAME COMPENSO MENSILE
# -----------------------
def crea_dataframe_compenso_mese(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggrega il le ore standard, le ore straordinario, e il compenso giornaliero per mese (anno/mese).
    """

    df_mese = df.copy()
    df_mese["data"] = pd.to_datetime(df_mese["data"])
    df_mese["anno"] = df_mese["data"].dt.year
    df_mese["mese"] = df_mese["data"].dt.month

    df_mensile = (
        df_mese
        .groupby(
            ["id_dipendente","nome","cognome", "dipartimento", "anno", "mese"],
            as_index=False
        )
        .agg(
            totale_ore_standard=("ore_standard", "sum"),
            totale_ore_straordinari=("ore_straordinari", "sum"),           
            totale_paga_mese=("compenso_giornaliero", "sum")
        )
    )

    logger.info(
        "Creato DataFrame compensi mensili. Righe: %d",
        len(df_mensile)
    )

    return df_mensile

def salva_totale_compenso_csv(
    df_compenso: pd.DataFrame,
    output_file: str
) -> None:
    """Salva il compenso giornaliero su CSV."""
    #output_path = f"{output_dir}/totale_compenso.csv"
    df_compenso.to_csv(output_file, index=False)
    logger.info("Creato file CSV %s", "FINALE_PYTHON" + output_file.split("FINALE_PYTHON", 1)[1])


# -----------------------
# LOAD
# -----------------------
def load(df: pd.DataFrame, output_dir: str) -> None:
    """
    Scrive un file CSV per ogni dipartimento.
    """

    for dipartimento, df_dep in df.groupby("dipartimento"):
        output_path = f"{output_dir}_{dipartimento}.csv"
        df_dep.to_csv(output_path, index=False)
        logger.info("Creato file %s", "FINALE_PYTHON" + output_path.split("FINALE_PYTHON", 1)[1])

# def load(df: pd.DataFrame, output_dir: str, file_type: str = ".csv") -> None:
#     """
#     Scrive un file CSV per ogni dipartimento.
#     """

#     for dipartimento, df_dep in df.groupby("dipartimento"):
#         output_path = f"{output_dir}_{dipartimento}{file_type}"
#         if file_type == ".csv":
#             df_dep.to_csv(output_path, index=False)
#         elif file_type in (".xlsx", "xls"):
#             df_dep.to_excel(output_path, index=False)
#         else:
#             raise

#         logger.info("Creato file %s", output_path)


# -----------------------
# AGGREGAZIONE PER FINANCE
# -----------------------
# def aggrega_ore_e_paga(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Aggrega ore e paga per dipendente e dipartimento.
#     """

#     df_aggregato = (
#         df
#         .groupby(
#             ["id_dipendente","nome", "cognome", "dipartimento", "data" ,"paga_oraria","compenso_giornaliero"],
#             as_index=False
#         )
#         .agg(
#             totale_ore=("ore_lavorate", "sum"),
#             #totale_paga=("paga_oraria", "sum")
#         )
#     )
    
#     cols = list(df_aggregato.columns)
#     cols.remove("totale_ore")
#     idx = cols.index("paga_oraria") + 1
#     cols.insert(idx, "totale_ore")
#     df_aggregato = df_aggregato[cols]

#     logger.info(
#         "Aggregazione ore e paga completata. Righe: %d",
#         len(df_aggregato)
#     )

#     return df_aggregato        

# def salva_totale_compenso_mese_csv(
#     df_compenso_mese: pd.DataFrame,
#     output_dir: str
# ) -> None:
#     """Salva il compenso mensile su CSV."""
#     output_path = f"{output_dir}/totale_compenso_mese.csv"
#     df_compenso_mese.to_csv(output_path, index=False)
#     logger.info("Creato file CSV %s", output_path)



# -----------------------
# DATAFRAME COMPENSO GIORNALIERO
# -----------------------
# def crea_dataframe_compenso(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Crea un DataFrame con il compenso giornaliero per ogni riga.
#     """

#     df_compenso = df.copy()

#     df_compenso["compenso_giornaliero"] = df_compenso.apply(
#         lambda r: calcola_paga_giornaliera(
#             r["ore_lavorate"],
#             r["paga_oraria"]
#         ),
#         axis=1
#         )
    
#     logger.info(
#         "Creato DataFrame compensi giornalieri. Righe: %d",
#         len(df_compenso)
#     )

#     return df_compenso


# -----------------------
# BUSINESS LOGIC
# -----------------------
# def calcola_paga_giornaliera(
#     ore_lavorate: float,
#     paga_oraria: float
# ) -> float:
#     """
#     Calcola la paga giornaliera:
#     - ore mancanti → 0
#     - max 8 ore ordinarie
#     - straordinari +50%
#     """

#     if ore_lavorate is None:
#         ore_lavorate = 0.0

#     ordinario = min(ore_lavorate, 8) * paga_oraria
#     straordinario = max(ore_lavorate-8, 0) * paga_oraria * 1.5
#     risultato = ordinario + straordinario

#     return risultato

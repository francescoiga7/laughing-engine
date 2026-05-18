import logging
import pandas as pd

logger = logging.getLogger(__name__)

# estrazione dati
def extract(dipendenti_path: str, presenze_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Estrae i dati dai file CSV."""
    df_dipendenti = pd.read_csv(dipendenti_path)
    df_presenze = pd.read_csv(presenze_path)
    return df_dipendenti, df_presenze

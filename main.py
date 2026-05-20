#MAIN
import time
import os
import logging
from src.etl import (
    extract,
    transform,
    salva_totale_compenso_csv,
    crea_dataframe_compenso_mese,
    load,
)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Inizio processo ETL")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DIPENDENTI_PATH = os.path.join(BASE_DIR, "data", "raw", "dipendenti.csv")
    PRESENZE_PATH = os.path.join(BASE_DIR, "data", "raw", "presenze.csv")
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
    OUTPUT_DIR_GG_TOT = os.path.join(BASE_DIR, "data", "processed", "totale_compenso.csv")  
    OUTPUT_DIR_MM_TOT = os.path.join(BASE_DIR, "data", "processed", "totale_compenso_mese.csv")     
    OUTPUT_DIR_SPLIT = os.path.join(BASE_DIR, "data", "processed", "report") 
    OUTPUT_FILE_TYPE = ".csv"


    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        start = time.perf_counter()

        # 1. Extract
        df_dip, df_pre = extract(
            DIPENDENTI_PATH,
            PRESENZE_PATH
        )
        
        end = time.perf_counter()
        elapsed = end - start
        logger.info("EXTRAT completato in %.2f secondi", elapsed)

        # 2. Transform

        step_start = time.perf_counter()

        df_trasf = transform(
            df_dip,
            df_pre
        )

        end = time.perf_counter()
        elapsed = end - step_start
        logger.info("TRANSFORM completato in %.2f secondi", elapsed)     

        # 3. Compenso giornaliero totale
        # step_start = time.perf_counter()   

        # salva_totale_compenso_csv(df_trasf, OUTPUT_DIR_GG_TOT)

        # end = time.perf_counter()
        # elapsed = end - step_start
        # logger.info("CSV Giornaliero Totale creato in %.2f secondi", elapsed)          

        # 4. Compenso mensile totale
        step_start = time.perf_counter()  

        df_compenso_mese = crea_dataframe_compenso_mese(df_trasf)

        end = time.perf_counter()
        elapsed = end - step_start
        logger.info("Creato df Mensile in %.2f secondi", elapsed)          

        step_start = time.perf_counter()  

        salva_totale_compenso_csv(df_compenso_mese, OUTPUT_DIR_MM_TOT)

        end = time.perf_counter()
        elapsed = end - step_start
        logger.info("CSV Mensile Totale creato in %.2f secondi", elapsed)               

        # 5. Creazione file divisi per dipartimento
        step_start = time.perf_counter()           
        load(df_trasf, OUTPUT_DIR_SPLIT)

        end = time.perf_counter()
        elapsed = end - step_start
        logger.info("CSV per Dipartimento creati in %.2f secondi", elapsed)          

        end = time.perf_counter()
        elapsed = end - start

        logger.info("ETL completato con successo in %.2f secondi", elapsed)

    except FileNotFoundError as e:
        logger.error("File CSV mancante: %s", e)

    except Exception as e:
        logger.exception("Errore imprevisto durante l'ETL")


if __name__ == "__main__":
    main()
"""Read B3's data files."""

from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _to_float(x: Any) -> float:
    try:
        return float(x)
    except:
        return np.nan


def _parse_data_vencimento(data_vencimento: pd.Series) -> pd.Series:
    return pd.to_datetime(data_vencimento, format="%Y%m%d", errors="coerce")


def _remove_text_extra_spaces(s: pd.Series) -> pd.Series:
    return s.replace(" +", " ", regex=True)


def read_data(filepath: Path, rename_columns: bool = False) -> pd.DataFrame:
    registro01 = read_registro01()
    NAMES = registro01["NOME DO CAMPO"]
    WIDTHS = (registro01["POS. FINAL"] - registro01["POS. INIC."]) + 1
    df = pd.read_fwf(
        filepath,
        compression="zip",
        widths=WIDTHS,
        names=NAMES,
        skiprows=1,
        skipfooter=1,
        encoding="latin-1",
        parse_dates=["DATA", "DATVEN"],
    )
    df = df.assign(
        DATVEN=_parse_data_vencimento(df["DATVEN"]),
        PRAZOT=df["PRAZOT"].apply(_to_float),
        ESPECI=_remove_text_extra_spaces(df["ESPECI"]),
    )
    if rename_columns:
        names = {
            a: b
            for _, a, b in registro01[
                ["NOME DO CAMPO", "nome_normalizado"]
            ].itertuples()
        }
        df = df.rename(columns=names)
    return df


def read_registro00() -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "registro00.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_registro01() -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "registro01.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_registro99() -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "registro99.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_codbdi(rename_columns: bool = False) -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "codbdi.csv") as filepath:
        df = pd.read_csv(filepath)
    if rename_columns:
        df = df.rename(
            columns={
                "CODBDI": "bdi_id",
                "DESCRIÇÃO": "bdi",
            },
        )
    return df


def read_especi(rename_columns: bool = False) -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "especi.csv") as filepath:
        df = pd.read_csv(filepath)
    if rename_columns:
        df = df.rename(
            columns={
                "ESPECI": "especificacao_id",
                "DESCRIÇÃO": "especificacao",
            },
        )
    return df


def read_indopc(rename_columns: bool = False) -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "indopc.csv") as filepath:
        df = pd.read_csv(filepath)
    if rename_columns:
        df = df.rename(
            columns={
                "INDOPC": "indice_correcao_id",
                "SÍMBOLO": "simbolo",
                "DESCRIÇÃO": "indice_correcao",
            },
        )
    return df


def read_tpmerc(rename_columns: bool = False) -> pd.DataFrame:
    with resources.path("b3data.auxiliary_tables", "tpmerc.csv") as filepath:
        df = pd.read_csv(filepath)
    if rename_columns:
        df = df.rename(
            columns={
                "TPMERC": "tipo_mercado_id",
                "DESCRIÇÃO": "tipo_mercado",
            },
        )
    return df

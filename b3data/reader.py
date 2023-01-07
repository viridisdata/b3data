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


def read_registro(filepath: Path) -> pd.DataFrame:
    layout = {
        "tipreg": [1, 2],
        "data": [3, 10],
        "bdi_id": [11, 12],
        "simbolo": [13, 24],
        "tipo_mercado_id": [25, 27],
        "nome_resumido": [28, 39],
        "especificacao": [40, 49],
        "prazo": [50, 52],
        "simbolo_moeda": [53, 56],
        "preco_abertura": [57, 69],
        "preco_maximo": [70, 82],
        "preco_minimo": [83, 95],
        "preco_medio": [96, 108],
        "preco_ultimo_negocio": [109, 121],
        "preco_melhor_oferta_compra": [122, 134],
        "preco_melhor_oferta_venda": [135, 147],
        "quantidade_negocios": [148, 152],
        "quantidade_titulos_negociados": [153, 170],
        "volume_negociado": [171, 188],
        "preco_exercicio": [189, 201],
        "indice_correcao_id": [202, 202],
        "data_vencimento": [203, 210],
        "fator_cotacao": [211, 217],
        "preco_exercicio_pontos": [218, 230],
        "codisi": [231, 242],
        "dismes": [243, 245],
    }
    NAMES = list(layout.keys())
    WIDTHS = [y - x + 1 for x, y in layout.values()]
    d = pd.read_fwf(
        filepath,
        compression="zip",
        widths=WIDTHS,
        names=NAMES,
        skiprows=1,
        skipfooter=1,
        encoding="latin-1",
        parse_dates=["data", "data_vencimento"],
    )
    d = d.assign(
        data_vencimento=_parse_data_vencimento(d["data_vencimento"]),
        prazo=d["prazo"].apply(_to_float),
        especificacao=_remove_text_extra_spaces(d["especificacao"]),
    )
    d = d.drop(columns=["tipreg"])
    return d


def read_codbdi():
    with resources.path("b3data.auxiliary_tables", "codbdi.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_especi():
    with resources.path("b3data.auxiliary_tables", "especi.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_indopc():
    with resources.path("b3data.auxiliary_tables", "indopc.csv") as filepath:
        df = pd.read_csv(filepath)
    return df


def read_tpmerc():
    with resources.path("b3data.auxiliary_tables", "tpmerc.csv") as filepath:
        df = pd.read_csv(filepath)
    return df

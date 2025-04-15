import os
import platform
import can
import cantools
from typing import List, Dict, Any, Optional, Tuple, TypeAlias, Union
from cantools.database import Database

StringPathLike: TypeAlias = Union[str, os.PathLike]

if platform.system() == "Windows":
    ENCODING = "gbk"
else:
    ENCODING = "utf-8"


def __load_dbc_single(dbc_url: StringPathLike) -> Database:
    """
    Load a DBC file and return the database object.
    """
    with open(dbc_url, "r", encoding=ENCODING) as f:
        dbc_content = cantools.db.load(f, database_format="dbc", strict=False)
    return dbc_url, dbc_content


def load_dbc_multi(
    dbc_url: Union[StringPathLike, List[StringPathLike]],
) -> List[Tuple[StringPathLike, Database]]:

    dbcs = []
    if isinstance(dbc_url, str):
        if os.path.isdir(dbc_url):
            dbc_urls = [
                os.path.join(dbc_url, file)
                for file in os.listdir(dbc_url)
                if file.endswith(".dbc")
            ]
            dbcs.extend(map(__load_dbc_single, dbc_urls))

        elif os.path.isfile(dbc_url):
            dbcs.append(__load_dbc_single(dbc_url))
    elif isinstance(dbc_url, list):
        dbcs.extend(map(__load_dbc_single, dbc_url))

    return dbc_url, dbcs


def __load_can_multi(
    can_url: Union[StringPathLike, List[StringPathLike]],
) -> Tuple[List[StringPathLike], List[StringPathLike]]:
    blf_urls = []
    asc_urls = []
    if isinstance(can_url, str):
        if os.path.isdir(can_url):
            for file in os.listdir(can_url):
                full_path = os.path.join(can_url, file)
                if file.endswith(".blf"):
                    blf_urls.append(full_path)
                elif file.endswith(".asc"):
                    asc_urls.append(full_path)
        elif os.path.isfile(can_url):
            if can_url.endswith(".blf"):
                blf_urls.append(can_url)
            elif can_url.endswith(".asc"):
                asc_urls.append(can_url)
    elif isinstance(can_url, list):
        for url in can_url:
            if url.endswith(".blf"):
                blf_urls.append(url)
            elif url.endswith(".asc"):
                asc_urls.append(url)

    return blf_urls, asc_urls


def __decode_can(
    dbc_data,
    can_data,
    signal_names: Optional[List[StringPathLike]] = None,
    signal_corr: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Decode CAN data using the provided DBC data.
    """
    decoded_data = []
    for message in can_data:
        try:
            decoded_message = dbc_data.decode(message.arbitration_id, message.data)
            if signal_names is not None:
                filtered_message = {
                    name: decoded_message[name] for name in signal_names
                }
                decoded_data.append(filtered_message)
            else:
                decoded_data.append(decoded_message)
        except Exception as e:
            print(f"Error decoding message: {e}")
    return decoded_data

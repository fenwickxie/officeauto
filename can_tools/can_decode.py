import cantools
import can
import pandas as pd
import os
from typing import Union, List, TypeAlias, Optional

StringPathLike: TypeAlias = Union[str, os.PathLike]


def load_dbc_files(dbc_input: Union[StringPathLike, List[StringPathLike]]) -> List[cantools.database.Database]:
    dbcs = []
    if isinstance(dbc_input, str):
        if os.path.isdir(dbc_input):
            for file in os.listdir(dbc_input):
                if file.endswith('.dbc'):
                    dbc_path = os.path.join(dbc_input, file)
                    dbcs.append(cantools.db.load_file(dbc_path))
        else:
            dbcs.append(cantools.db.load_file(dbc_input))
    elif isinstance(dbc_input, list):
        for dbc_path in dbc_input:
            dbcs.append(cantools.db.load_file(dbc_path))
    return dbcs


def load_blf_files(can_input: Union[StringPathLike, List[StringPathLike]]) -> List[str]:
    blfs = []
    ascs = []
    if isinstance(can_input, str):
        if os.path.isdir(can_input):
            for file in os.listdir(can_input):
                if file.endswith('.blf'):
                    blf_path = os.path.join(can_input, file)
                    blfs.append(blf_path)
                elif file.endswith('.asc'):
                    asc_path = os.path.join(can_input, file)
                    ascs.append(asc_path)
        else:
            if can_input.endswith('.blf'):
                blfs.append(can_input)
            elif can_input.endswith('.asc'):
                ascs.append(can_input)
    elif isinstance(can_input, list):
        for file in can_input:
            if file.endswith('.blf'):
                blfs.append(file)
            elif file.endswith('.asc'):
                ascs.append(file)
    return blfs, ascs


def _read_can_files(dbc_input: Union[StringPathLike, List[StringPathLike]],
                    blf_input: Union[StringPathLike, List[StringPathLike]],
                    signal_names: Optional[List[str]] = None):
    dbcs = load_dbc_files(dbc_input)
    blfs = load_blf_files(blf_input)

    for blf in blfs:
        log_data = can.BLFReader(blf)
        for dbc_path, dbc in dbcs:
            decoded = {}
            for msg in log_data:
                try:
                    dec = dbc.decode_message(msg.arbitration_id, msg.data)
                    if dec:
                        for key, data in dec.items():
                            if signal_names is None or key in signal_names:
                                if key not in decoded:
                                    decoded[key] = []
                                decoded[key].append([msg.timestamp, data])
                except:
                    pass

            sigs = []
            for k, v in decoded.items():
                timestamps = [i[0] for i in v]
                data = [i[1] for i in v]
                s = pd.Series(data, name=k)
                sigs.append(s)

            df = pd.concat(sigs, axis=1)
            df['timestamp'] = timestamps

            # Create a unique filename for each combination of DBC and BLF files
            base_name = f"{os.path.splitext(os.path.basename(dbc_path))[0]}_{os.path.splitext(os.path.basename(blf))[0]}"
            csv_filename = f"{base_name}.csv"
            parquet_filename = f"{base_name}.parquet"
            df.to_csv(csv_filename, encoding='utf-8-sig')
            df.to_parquet(parquet_filename)



# Example usage:
# dbc_input = ["path/to/dbc1.dbc", "path/to/dbc2.dbc"]
# blf_input = ["path/to/blf1.blf", "path/to/blf2.blf"]
# _read_can_files(dbc_input, blf_input)

import cantools
import pandas as pd
import os
from typing import Union, List, Optional
from asammdf import MDF

StringPathLike = Union[str, os.PathLike]

def load_dbc_files(dbc_input: Union[StringPathLike, List[StringPathLike]]) -> List[cantools.database.Database]:
    dbcs = []
    if isinstance(dbc_input, str):
        if os.path.isdir(dbc_input):
            for file in os.listdir(dbc_input):
                if file.endswith('.dbc'):
                    dbc_path = os.path.join(dbc_input, file)
                    dbcs.append((dbc_path, cantools.db.load_file(dbc_path)))
        else:
            dbcs.append((dbc_input, cantools.db.load_file(dbc_input)))
    elif isinstance(dbc_input, list):
        for dbc_path in dbc_input:
            dbcs.append((dbc_path, cantools.db.load_file(dbc_path)))
    return dbcs

def load_can_files(can_input: Union[StringPathLike, List[StringPathLike]]) -> List[str]:
    can_files = []
    if isinstance(can_input, str):
        if os.path.isdir(can_input):
            for file in os.listdir(can_input):
                if file.lower().endswith(('.blf', '.asc')):
                    can_path = os.path.join(can_input, file)
                    can_files.append(can_path)
        else:
            can_files.append(can_input)
    elif isinstance(can_input, list):
        for can_path in can_input:
            can_files.append(can_path)
    return can_files

def _read_can_files(dbc_input: Union[StringPathLike, List[StringPathLike]],
                    can_input: Union[StringPathLike, List[StringPathLike]],
                    signal_names: Optional[List[str]] = None):
    dbcs = load_dbc_files(dbc_input)
    can_files = load_can_files(can_input)

    for can_file in can_files:
        mdf = MDF(can_file)

        # Filter signals based on signal_names if provided
        if signal_names is not None:
            filtered_mdf = mdf.filter(signal_names)
        else:
            filtered_mdf = mdf

        # Convert to DataFrame with automatic interpolation
        df = filtered_mdf.to_dataframe(raster=None, time_from_zero=False)

        # Decode messages using DBC files
        for dbc_path, dbc in dbcs:
            decoded_signals = {}
            for column in df.columns:
                try:
                    message_id = int(column.split()[0], 16)
                    message = dbc.get_message_by_arbitration_id(message_id)
                    if message:
                        decoded_signal = {}
                        for signal in message.signals:
                            if signal.name in df.columns:
                                decoded_signal[signal.name] = df[signal.name]
                        decoded_signals.update(decoded_signal)
                except:
                    pass

            # Create a DataFrame from decoded signals
            decoded_df = pd.DataFrame(decoded_signals)

            # Interpolate missing values
            decoded_df.interpolate(method='time', inplace=True)

            # Create a unique filename for each combination of DBC and CAN files
            base_name = f"{os.path.splitext(os.path.basename(dbc_path))[0]}_{os.path.splitext(os.path.basename(can_file))[0]}"
            csv_filename = f"{base_name}.csv"
            decoded_df.to_csv(csv_filename, encoding='utf-8-sig')
if __name__ == '__main__':
    # Example usage:
    dbc_input = ["path/to/dbc1.dbc", "path/to/dbc2.dbc"]
    can_input = ["path/to/blf1.blf", "path/to/asc1.asc"]
    signal_names = ['Signal1', 'Signal2']
    _read_can_files(dbc_input, can_input, signal_names)




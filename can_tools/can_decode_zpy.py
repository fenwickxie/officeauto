import os
import can
import cantools
import pandas as pd
from asammdf import MDF, Signal
import warnings

warnings.filterwarnings("ignore")


def get_raw_data_type(file):
    raw_data_type = file[-3:]
    if raw_data_type == 'asc':
        return 0
    elif raw_data_type == 'blf':
        return 1


def decode_data(raw_data, signals, databases):
    decoded = {}
    # 数据解码
    for msg in raw_data:
        for database in databases:
            try:
                signal_value = database.decode_message(msg.arbitration_id, msg.data)
                if signal_value:
                    for key, data in signal_value.items():
                        if key in signals:
                            if key not in decoded:
                                decoded[key] = []
                            decoded[key].append([msg.timestamp, data])
                            continue
            except Exception as e:

                pass
    sigs = []
    for sig_name, sig_value in decoded.items():
        timestamps = [value[0] for value in sig_value]
        data = [value[1] for value in sig_value]
        # data = [float(value[1]) for value in sig_value]
        s = Signal(data, timestamps, name=sig_name)
        sigs.append(s)
    return sigs


def count_duplicates(directory, filename):
    unique_filenames = set()
    duplicates_count = 0
    for item in os.listdir(directory):
        if item == filename:
            if item in unique_filenames:
                duplicates_count += 1
            else:
                unique_filenames.add(item)
    return duplicates_count


def sigle_Can_2_mat(file_name, signals, dbc_path, save_path, options):
    """
    file_name:     blf文件名
    signals:        读取信号的表格
    dbc_path:       dbc所在的文件夹
    save_path:      .mat 文件保存的路径
    option:         1,文件名增加油门位置前缀，0 不增加
    return:         dataframe
    """
    dbc_files = os.listdir(dbc_path)  # DBC文件
    databases = [cantools.db.load_file(dbc_path + dbc_file, strict=False) for dbc_file in dbc_files]
    raw_data_type = get_raw_data_type(file_name)
    if raw_data_type:
        raw_data = can.BLFReader(file_name)
    else:
        raw_data = can.ASCReader(file_name)
    sigs = decode_data(raw_data, signals, databases)
    mdf = MDF()
    mdf.append(sigs)
    df = mdf.to_dataframe()  # 这一步不影响插值结果
    df.insert(0, 'Time', df.index)
    return df


# test
if __name__ == "__main__":
    dbc_path = 'D:\\SRM自动报告\\SRM_Auto_Tes\\DBC\\'
    save_folder = 'D:\\SRM自动报告'
    data_dir = 'D:\\SRM自动报告\\SRM_Auto_Tes\\raw_data'  # 一组数据
    # data_dir = 'D:\\SRM自动报告\\SRM_Auto_Tes\\data_2'  # 多组数据
    signals_file = 'D:\\SRM自动报告\\SRM_Report.csv'  # 所需信号csv文件
    fig_folder = 'D:\\SRM自动报告\\SRM_Auto_Tes\\数据分析报告\\figure'
    signals = pd.read_csv(signals_file)['signals'].astype(str).tolist()
    options = 0
    file_name = 'D:\\SRM自动报告\\SRM_Auto_Tes\\raw_data\\对开-100-ON-5ms.asc'
    signals = pd.read_csv(signals_file)['signals'].astype(str).tolist()
    df = sigle_Can_2_mat(file_name, signals, dbc_path, 1, 1)
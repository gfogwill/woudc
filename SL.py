import pandas as pd


def load_solar_light_file(file_path):
    """" Cargo archivo de Solar Light """

    dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%Y %H:%M')
    data = pd.read_csv(file_path, header=1, parse_dates={'datetime': ['Date', 'Time']}, date_parser=dateparse,index_col='datetime')

    return data


if __name__ == "__main__":
    load_solar_light_file('BA170101.uvb')
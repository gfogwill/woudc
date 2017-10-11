import pandas as pd


class SL:
    def __init__(self):
        self.data = pd.DataFrame()

    def load_solar_light_file(file_path):
        """" Cargo archivo de Solar Light """

        dateparse = lambda x: pd.datetime.strptime(x, '%d.%m.%Y %H:%M')

        text = "\"Date\",\"Time\""
        f= open(file_path)
        i=0
        for i, line in enumerate(f, 1):
            if text in line:
                init_line = i
                break
        f.close()

        data = pd.read_csv(file_path,
                           header=init_line-1,
                           parse_dates={'datetime': [0, 1]},
                           date_parser=dateparse,
                           index_col='datetime',
                           error_bad_lines=False)

        data.columns = ['Sensor1', 'Sensor2', 'Temp1', 'Temp2']
        date = data.ix[-1].name.date()

        return data, date


if __name__ == "__main__":
    SL.load_solar_light_file('BA170101.uvb')
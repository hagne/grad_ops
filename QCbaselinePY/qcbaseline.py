# import os
from pathlib import Path
import pandas as pd


class QC(object):
    def __init__(self, folder_path = '/Users/htelg/data/baseline/scaled/brw/2018/',
                 num_files_to_be_opened = 1,
                 verbose = False):

        self.folder_path = folder_path
        self._verbose = verbose
        self._num_files_to_be_opened = num_files_to_be_opened
        # Generate the database
        fldpath = Path(folder_path)
        l = [fp for fp in fldpath.iterdir() if fp.is_file()]
        l.sort()
        df_files = pd.DataFrame(l, columns = ['file_name'])
        df_files['dataobject'] = [type('DataObject', (object,), {'thedata' :None})() for i in range(len(df_files))]
        self._data = df_files
        self._data['date'] = pd.to_datetime(self._data.file_name.apply(lambda x: x.name.split('.')[2]))

        idx_open = self._data.index[-1]
        self.adjust_should_be_opened(idx_open)
        self.open_required_files()

    def read_file(self, fname = '/Users/htelg/data/baseline/scaled/brw/2018/gradobs.brw.20180102.txt'):
        df = pd.read_csv(fname, sep='\t',
                         index_col= False,
                         skip_blank_lines=True
                         )
        # df

        df.index = pd.to_datetime(df.Year, format = '%Y') + pd.to_timedelta(df.DayFrac -1, 'D').dt.round('1min')
        df.drop(['HourMin', 'DOY', 'Year', 'DayFrac'], axis=1, inplace=True)
        return df

    def adjust_should_be_opened(self, idx_open):
        self._data['should_be_open'] = self._data.index - idx_open

    def open_required_files(self):
        df_files = self._data
        should_be_open = df_files[df_files.should_be_open.abs() <= self._num_files_to_be_opened]
        for idx in should_be_open.index:
            data = df_files.loc[idx ,'dataobject']
            #     if isinstance(data, type(None)):
            if isinstance(data.thedata, type(None)):
                #         print('did it: {}'.format(data))
                data.thedata = self.read_file(df_files.loc[idx ,'file_name'])
                df_files.loc[idx ,'dataobject'] = data
                if self._verbose:
                    print('opend file: {}'.format(df_files.loc[idx ,'file_name']))
            #             print(type(df_files.loc[idx,'file_name']).__name__)
            else:
                if self._verbose:
                    print('already opened: {}'.format(df_files.loc[idx ,'file_name']))

    #     @property
    def shift2next_day(self):
        df_files = self._data
        other = self.next_day
        if other.shape[0] == 0:
            print('You see the newest file availble')
        else:
            self.adjust_should_be_opened(df_files[df_files.should_be_open == 1].index.values[0])
            self.open_required_files()
        return self.current_day

    @property
    def next_day(self):
        data = self._data[self._data.should_be_open == 1]
        if data.shape[0] == 0:
            return None
        else:
            return data

    #     @property
    def shift2previous_day(self):
        self.adjust_should_be_opened(self.previous_day.index.values[0])
        self.open_required_files()
        return self.current_day

    @property
    def previous_day(self):
        return self._data[self._data.should_be_open == -1]

    @property
    def current_day(self):
        return self._data[self._data.should_be_open == 0]
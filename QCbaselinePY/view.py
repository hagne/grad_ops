from copy import deepcopy
import numpy as np
import matplotlib.pylab as plt
import itertools
from IPython.display import display
from ipywidgets import widgets
import pandas as pd

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
colorcyc = itertools.cycle(colors)

view_dict =  {'rad': {'DW_long':  ['DownwellingLongwave[Wm-2]'],
                      'DW_short': ['DownwellingShortwave[Wm-2]', 'DiffuseBW[Wm-2]', 'DirectNormal[Wm-2]', 'DirectNormal2[Wm-2]'],
                      'DW_long_status': ['DLcase[degC]', 'DLdome[deg C]'],
                      'logger_status': ['SZA'],},
              'albedo': {'UW_long':['UpwellingLongwave[Wm-2]'],
                         'UW_short': ['UpwellingShortwave[Wm-2]'],
                         'UW_long_status':['ULcase[deg C]', 'ULdome[deg C]']},
              'sp02': {'direct_spectral':['sp02_412[nm]',
                                          'sp02_500[nm]',
                                          'sp02_675[nm]',
                                          'sp02_862[nm]',
                                          'sp02_368[nm]',
                                          'sp02_1050[nm]',
                                          'sp02_610[nm]',
                                          'sp02_778[nm]',],
                       'sp02_status': ['Albedo']},
              'snow_soil': {'snowdepth':['SnowDepth[mm]'],
                            'soiltemp': ['Therm5[deg C]',
                                        'Therm10[deg C]',
                                        'Therm15[deg C]',
                                        'Therm20[deg C]',
                                        'Therm25[deg C]',
                                        'Therm30[deg C]',
                                        'Therm45[deg C]',
                                        'Therm70[deg C]',
                                        'Therm95[deg C]',
                                        'Therm120[deg C]',]},
             }


prop_dict ={'DownwellingShortwave[Wm-2]': {'ylim' : None},
            'DownwellingLongwave[Wm-2]': {'ylim' : (100,400)},
            'DLcase[degC]': {'ylim' : (-50, 50)},
            'DLdome[deg C]': {'ylim' : None},
            'UpwellingShortwave[Wm-2]': {'ylim' : None},
            'UpwellingLongwave[Wm-2]': {'ylim' : None},
            'ULcase[deg C]': {'ylim' : None},
            'ULdome[deg C]': {'ylim' : None},
            'DiffuseBW[Wm-2]': {'ylim' : None},
            'DirectNormal[Wm-2]': {'ylim' : None},
            'DirectNormal2[Wm-2]': {'ylim' : None},
            'sp02_412[nm]': {'ylim' : None},
            'sp02_500[nm]': {'ylim' : None},
            'sp02_675[nm]': {'ylim' : None},
            'sp02_862[nm]': {'ylim' : None},
            'sp02_368[nm]': {'ylim' : None},
            'sp02_1050[nm]': {'ylim' : None},
            'sp02_610[nm]': {'ylim' : None},
            'sp02_778[nm]': {'ylim' : None},
            'SnowDepth[mm]': {'ylim' : None},
            'Therm5[deg C]': {'ylim' : None},
            'Therm10[deg C]': {'ylim' : None},
            'Therm15[deg C]': {'ylim' : None},
            'Therm20[deg C]': {'ylim' : None},
            'Therm25[deg C]': {'ylim' : None},
            'Therm30[deg C]': {'ylim' : None},
            'Therm45[deg C]': {'ylim' : None},
            'Therm70[deg C]': {'ylim' : None},
            'Therm95[deg C]': {'ylim' : None},
            'Therm120[deg C]': {'ylim' : None},
            'SZA': {'ylim' : None},
            'Albedo': {'ylim' : None},}


class QcView(object):
    def __init__(self, qc):
        self.qc = qc
        self._view_dict = None
        for key in self.view_dict:
            setattr(self, key, QcViewFigure(self, self.view_dict[key]))
        self._update_plot = None

    @property
    def view_dict(self):
        if isinstance(self._view_dict, type(None)):
            colums = list(self.qc.current_day.dataobject.iloc[0].thedata.columns)
            view_dict_cleaned = deepcopy(view_dict)
            for fk in view_dict:
                #     print('fk: {}'.format(fk))
                fk_list = []
                for ak in view_dict[fk]:
                    #         print('ak: {}'.format(ak))
                    ak_list = []
                    for para in view_dict[fk][ak]:
                        #             print('para: {}'.format(para))
                        if para in colums:
                            ak_list.append(colums.pop(colums.index(para)))
                    if len(ak_list) == 0:
                        #                         print('\t pop ak: {}'.format(ak))
                        view_dict_cleaned[fk].pop(ak)
                    else:
                        view_dict_cleaned[fk][ak] = ak_list
                        fk_list.append(ak)
                if len(fk_list) == 0:
                    #                     print('\tpoped fk: {}'.format(fk))
                    view_dict_cleaned.pop(fk)
            if len(colums) != 0:
                print('the following colums where not defined: {}'.format('\n'.join(colums)))
            self._view_dict = view_dict_cleaned
        return self._view_dict

    def _callback(self, plot, a, **kwargs):
        self._update_plot = plot
        self._update_a = a
        self._update_kwargs = kwargs

    def update(self):
        if isinstance(self._update_a, (list, np.ndarray)):
            ylim = []
            for a in self._update_a:
                ylim.append(a.get_ylim())
                a.clear()
        else:
            ylim = self._update_a.get_ylim()
            self._update_a.clear()
        self._update_plot(self._update_a, **self._update_kwargs)

        if isinstance(self._update_a, (list, np.ndarray)):
            for e, a in enumerate(self._update_a):
                a.set_ylim(ylim[e])
        else:
            self._update_a.set_ylim(ylim)


class QcViewFigure(object):
    def __init__(self, parent, fig_dict):
        self._parent = parent
        self.qc = parent.qc
        self.fig_dict = fig_dict
        self.ax_dict = {}
        for key in fig_dict:
            setattr(self, key, QcViewAxis(self, fig_dict[key]))
            self.ax_dict[key] = getattr(self, key)

    def plot(self, axlist=None, schnickschnack=True):

        if isinstance(axlist, type(None)):
            no_of_axis = len(self.fig_dict)
            self.f, self.a = plt.subplots(no_of_axis, sharex=True, gridspec_kw={'hspace': 0})
            self.f.set_figheight(self.f.get_figheight() * 0.4)
            self.f.set_figheight(self.f.get_figheight() * no_of_axis)
        for e, key in enumerate(self.ax_dict):
            qcax = self.ax_dict[key]
            ax = self.a[e]
            qcax.plot(ax=ax, schnickschnack=True)
        self._parent._callback(self.plot, self.a, schnickschnack=False)


class QcViewAxis(object):
    def __init__(self, parent, para_list):
        self._parent = parent
        self.para_list = para_list
        self.qc = parent.qc
        self._param_dict = {}
        for para in self.para_list:
            name = para.split('[')[0]
            setattr(self, name, QcViewParameter(self, para))
            self._param_dict[name] = getattr(self, name)

    def plot(self, ax=None, schnickschnack=True):
        if isinstance(ax, type(None)):
            self.f, self.a = plt.subplots()
        else:
            self.a = ax
        for e, para in enumerate(self._param_dict):
            lastparam = self._param_dict[para]
            lastparam.plot(ax=self.a, color=colors[e], schnickschnuck=False)

        lastparam.update_xlim()
        lastparam.grayout_current_day()

        if schnickschnack:
            lastparam.update_ylim()
            self.a.legend()
            self._parent._parent._callback(self.plot, self.a, schnickschnack=False)
        #         else:
        #             self.a.set_ylim(ylim)
        return self.a


class QcViewParameter(object):
    def __init__(self, parent, para):
        self._parent = parent
        self.qc = parent.qc
        self.para = para

    def plot(self, ax=None, color=None, schnickschnuck=True):
        if isinstance(ax, type(None)):
            self.f, self.a = plt.subplots()
        else:
            self.a = ax
        if isinstance(color, type(None)):
            color = colors[0]

        alpha = 0.5
        self.qc.current_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color)
        if not isinstance(self.qc.previous_day, type(None)):
            self.qc.previous_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color, alpha=alpha,
                                                                            label='_nolegend_')
        if not isinstance(self.qc.next_day, type(None)):
            self.qc.next_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color, alpha=alpha,
                                                                        label='_nolegend_')
        if schnickschnuck:
            self.update_xlim()
            self.grayout_current_day()
            self.update_ylim()
            self._parent._parent._parent._callback(self.plot, self.a, color=color, schnickschnuck=False)

        return self.a

    def grayout_current_day(self):
        self.a.axvspan(self.qc.current_day.date.iloc[0], self.qc.current_day.date.iloc[0] + pd.to_timedelta(1, 'D'),
                       color='0.95')

    def update_xlim(self, margins=3):
        start = self.qc.current_day.date.iloc[0] - pd.to_timedelta(margins, 'h')
        end = self.qc.current_day.date.iloc[0] + pd.to_timedelta(24 + margins, 'h')
        self.a.set_xlim(start, end)

    def update_ylim(self):
        lim = prop_dict[self.para]['ylim']
        if not isinstance(lim, type(None)):
            self.a.set_ylim(lim)


class Controlls(object):
    def __init__(self, qc, plotview):
        self.qc = qc
        self.plotview = plotview

        button_next_day = widgets.Button(description='next day')
        button_prev_day = widgets.Button(description='previous day')

        display(button_next_day)
        display(button_prev_day)

        button_next_day.on_click(self.on_button_next_day)
        button_prev_day.on_click(self.on_button_previous_day)

    def on_button_next_day(self, evt):
        #     try:
        self.qc.shift2next_day()
        self.plotview.update()

    def on_button_previous_day(self, evt):
        self.qc.shift2previous_day()
        self.plotview.update()
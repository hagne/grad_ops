from copy import deepcopy
import numpy as np
import matplotlib.pylab as plt
import itertools
from IPython.display import display
from ipywidgets import widgets
import pandas as pd

from QCbaselinePY import qcbaseline

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

get_color_cycler = lambda: itertools.cycle(colors)

view_dict =  {'rad': {'DW_long':  ['DownwellingLongwave[Wm-2]'],
                      'DW_short': ['DownwellingShortwave[Wm-2]', 'DiffuseBW[Wm-2]', 'DirectNormal[Wm-2]', 'DirectNormal2[Wm-2]', 'DirectNormal3[Wm-2]', 'Diffuse2[Wm-2]'],
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
                       # 'sp02_status': ['Albedo']
                       },
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
              'met': {'pressure': ['Pressure[mb]'],
                      'air_temp': ['AirTemp[deg C]'],
                      'RH': ['RH[%]'],
                      'wind_speed': ['Wspd[m/s]'],
                      'wind_direct': ['Wdir[Deg]']}
             }


prop_dict ={'DownwellingShortwave[Wm-2]': {'ylim' : None},
            'DownwellingLongwave[Wm-2]': {'ylim' : (100,450)},
            'DLcase[degC]': {'ylim' : (-30, 40)},
            'DLdome[deg C]': {'ylim' : (-30, 40)},
            'UpwellingShortwave[Wm-2]': {'ylim' : None},
            'UpwellingLongwave[Wm-2]': {'ylim' : None},
            'ULcase[deg C]': {'ylim' : (-30, 30)},
            'ULdome[deg C]': {'ylim' : (-30, 30)},
            'DiffuseBW[Wm-2]': {'ylim' : (-10,1000)},
            'Diffuse2[Wm-2]': {'ylim': (-10,1000)},
            'DirectNormal[Wm-2]': {'ylim' : (-10,1200)},
            'DirectNormal2[Wm-2]': {'ylim' : (-10,1200)},
            'DirectNormal3[Wm-2]': {'ylim' : (-10,1200)},
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
            'Albedo': {'ylim' : None},
            'Pressure[mb]': {'ylim' : None},
            'AirTemp[deg C]': {'ylim' : None},
            'RH[%]': {'ylim' : None},
            'Wspd[m/s]': {'ylim' : None},
            'Wdir[Deg]': {'ylim' : None},
            # : {'ylim' : None},
            # : {'ylim' : None},
            # : {'ylim' : None},
            }

folder_dict = {'ber': ['/Volumes/grad/gradobs/scaled/ber/2018/','/Volumes/grad/gradobs/raw/ber/2018/'],
               'brw': ['/Volumes/grad/gradobs/scaled/brw/2018/','/Volumes/grad/gradobs/raw/brw/2018/'],
               'kwj': ['/Volumes/grad/gradobs/scaled/kwj/2018/','/Volumes/grad/gradobs/raw/kwj/2018/'],
               'mlo': ['/Volumes/grad/gradobs/scaled/mlo/2018/','/Volumes/grad/gradobs/raw/mlo/2018/'],
               'smo': ['/Volumes/grad/gradobs/scaled/smo/2018/','/Volumes/grad/gradobs/raw/smo/2018/'],
               'spo': ['/Volumes/grad/gradobs/scaled/spo/2018/','/Volumes/grad/gradobs/raw/spo/2018/'],
               'sum': ['/Volumes/grad/gradobs/scaled/sum/2018/','/Volumes/grad/gradobs/raw/sum/2018/'],}

class QcView(object):
    def __init__(self, station = 'ber', verbose = False):
        self._plotview = None
        self._message_txt = ''
        # self.current_station = station
        # self._qc = qcbaseline.QC(folder_dict[station])
        self._verbose = verbose
        self._view_dict = None
        self.qc = station
        self.controlls = QcViewControlls(self)


    def send_message(self, txt):
        self._message_txt = txt + '\n - \n' + self._message_txt
        if hasattr(self, 'controlls'):
            self.controlls.message_display.value = self._message_txt

    @property
    def plotview(self):
        if isinstance(self._plotview, type(None)):
            self._plotview = QcViewPlotter(self)
        return self._plotview

    @property
    def qc(self):
        # if isinstance(self._qc, type(None)):
        #     self._qc = qcbaseline.QC(folder_dict[self.current_station])
        return self._qc

    @qc.setter
    def qc(self, station):
        if not station in folder_dict.keys():
            raise ValueError('{} is not a designated station. Pick one from the following list: {}'.format(station, ','.join(folder_dict.keys())))
        self.current_station = station
        self._qc = qcbaseline.QC(folder_dict[station][0], folder_path_raw= folder_dict[station][1], view = self)
        if self._verbose:
            print('just updated qc')
        traw = pd.to_datetime(self._qc.last_file_raw.stat().st_mtime, unit='s')
        tproc = pd.to_datetime(self._qc.last_file.stat().st_mtime, unit='s')
        txt = ('dt raw&processed (h): {}\n'
               't_raw:\t {}\n'
               't_proc:\t {}'.format(round(self._qc.time_diff_processed_raw/ pd.Timedelta(1, unit = 'h')),
                                     traw, tproc))
        self.send_message(txt)
        self._view_dict = None

    def update_plotview(self):
        f = self.plotview._f
        self._plotview = QcViewPlotter(self, fig = f)
        # self.plotview.update()


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
                self.send_message('the following colums where not defined: {}'.format('\n'.join(colums)))
            self._view_dict = view_dict_cleaned
        return self._view_dict

class QcViewPlotter(object):
    def __init__(self, parent, fig = None, verbose = False):
        self._update_plot = None
        self._update_a = None
        self._update_kwargs = None

        self._verbose = verbose
        self.view = parent
        self._a = None
        self._f = fig
        # self.qc = parent.qc
        self.update_groups()

    def update_groups(self):
        for key in self.view.view_dict:
            setattr(self, key, QcViewFigure(self, self.view.view_dict[key]))
        # self._f.clear()
        # self._update_plot = None # we can not use the old plot because we have to plot with the new ax_dict

    def plot(self, para_group = 'rad'):
        if isinstance(self._f, type(None)):
            self._f = plt.figure()
        else:
            self._f.clear()

        current_figure = getattr(self, para_group)
        current_figure.plot(fig = self._f)

    def _callback(self, plot, a, **kwargs):
        self._update_plot = plot
        self._update_a = a
        self._update_kwargs = kwargs

    def update(self, group = None):
        """

        Parameters
        ----------
        group: str
           had to be added for the case that the site changed. The site change button can then select a particular
           group that is then plotted again (with the updated ax_dict)

        Returns
        -------

        """
        if isinstance(self._update_plot, type(None)):
            if isinstance(group, type(None)):
                print('no update')
            else:
                group = getattr(self, group)
                print('update a: ', self._update_a)
                print('type:', type(self._update_a))
                group.plot(self._update_a)
            return

        elif isinstance(self._update_a, (list, np.ndarray)):
            ylim = []
            for a in self._update_a:
                ylim.append(a.get_ylim())                           #remanber old zoom
                a.clear()                                           #clear to make room for new plots
        else:
            ylim = self._update_a.get_ylim()
            self._update_a.clear()
        self._update_plot(self._update_a, **self._update_kwargs)    #do the plot again on the old axis ... should have new data though

        if isinstance(self._update_a, (list, np.ndarray)):
            for e, a in enumerate(self._update_a):
                a.set_ylim(ylim[e])
        else:
            self._update_a.set_ylim(ylim)

        if self._verbose:
            print('just updated plotview')


class QcViewFigure(object):
    def __init__(self, parent, fig_dict):
        self._parent = parent
        self.view = parent.view
        # self.qc = parent.qc
        self.fig_dict = fig_dict
        self._ax_dict = None

    @property
    def ax_dict(self):
        if isinstance(self._ax_dict, type(None)):
            self._ax_dict = {}
            for key in self.fig_dict:
                setattr(self, key, QcViewAxis(self, self.fig_dict[key]))
                self._ax_dict[key] = getattr(self, key)
        return self._ax_dict

    def plot(self, axlist=None, fig = None, schnickschnack=True):
        self._ax_dict = None
        if isinstance(axlist, type(None)):
            no_of_axis = len(self.fig_dict)
            if isinstance(fig, type(None)):
                self.f, self.a = plt.subplots(no_of_axis, sharex=True, gridspec_kw={'hspace': 0})
            else:
                self.f = fig
                self.a = fig.subplots(no_of_axis, sharex=True, gridspec_kw={'hspace': 0})

            self.f.set_figheight(plt.rcParams['figure.figsize'][1] * 1.5)
            # self.f.set_figheight(self.f.get_figheight() * no_of_axis)
            self.f.set_figwidth(plt.rcParams['figure.figsize'][0] * 1.5)
        else:
            self.a = axlist

        if not isinstance(self.a, (list, np.ndarray)):
            self.a = [self.a]

        self.f = self.a[0].get_figure()

        self._parent._f, self._parent._a = self.f, self.a

        for e, key in enumerate(self.ax_dict):
            qcax = self.ax_dict[key]
            ax = self.a[e]
            qcax.plot(ax=ax, schnickschnack=True)

        for at in self.a:
            at.yaxis.set_major_locator(plt.MaxNLocator(prune='both'))

        self._parent._callback(self.plot, self.a, schnickschnack=False)


class QcViewAxis(object):
    def __init__(self, parent, para_list):
        self._parent = parent
        self.para_list = para_list
        self.view = parent.view
        # self.qc = parent.qc
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
            # self.f = self.a.get_figure()
        colorcyc = get_color_cycler()
        for e, para in enumerate(self._param_dict):
            lastparam = self._param_dict[para]
            lastparam.plot(ax=self.a, color=next(colorcyc), schnickschnuck=False)

        lastparam.update_xlim()
        lastparam.grayout_current_day()

        if schnickschnack:
            lastparam.update_ylim()
            self.a.legend(fontsize = 'x-small')
            # self.f.autofmt_xdate()
            self._parent._parent._callback(self.plot, self.a, schnickschnack=False)
        #         else:
        #             self.a.set_ylim(ylim)
        return self.a


class QcViewParameter(object):
    def __init__(self, parent, para):
        self._parent = parent
        # self.qc = parent.qc
        self.view = parent.view
        self.para = para

    def plot(self, ax=None, color=None, schnickschnuck=True):
        if isinstance(ax, type(None)):
            self.f, self.a = plt.subplots()
        else:
            self.a = ax
            self.f = self.a.get_figure()
        if isinstance(color, type(None)):
            color = colors[0]

        alpha = 1
        lw = 1
        ms = 5
        try:
            self.view.qc.current_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color, linewidth = lw, marker = '.', markersize = ms)
        except TypeError:
            print('The parameter {} does not contain any data'.format(self.para))
            return

        if not isinstance(self.view.qc.previous_day, type(None)):
            self.view.qc.previous_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color, alpha=alpha,
                                                                            label='_nolegend_', linewidth = lw, marker = '.', markersize = ms)
        if not isinstance(self.view.qc.next_day, type(None)):
            self.view.qc.next_day.dataobject.iloc[0].thedata[self.para].plot(ax=ax, color=color, alpha=alpha,
                                                                        label='_nolegend_', linewidth = lw, marker = '.', markersize = ms)
        if schnickschnuck:
            self.update_xlim()
            self.grayout_current_day()
            self.update_ylim()
            # self.f.autofmt_xdate()
            self._parent._parent._parent._callback(self.plot, self.a, color=color, schnickschnuck=False)

        return self.a

    def grayout_current_day(self):
        self.a.axvspan(self.view.qc.current_day.date.iloc[0], self.view.qc.current_day.date.iloc[0] + pd.to_timedelta(1, 'D'),
                       color='0.95')

    def update_xlim(self, margins=24):
        start = self.view.qc.current_day.date.iloc[0] - pd.to_timedelta(margins, 'h')
        end = self.view.qc.current_day.date.iloc[0] + pd.to_timedelta(24, 'h')
        self.a.set_xlim(start, end)

    def update_ylim(self):
        lim = prop_dict[self.para]['ylim']
        if not isinstance(lim, type(None)):
            self.a.set_ylim(lim)


class QcViewControlls(object):
    def __init__(self,
                 parent,
                 # qc,
                 # plotview
                 ):
        self.view = parent
        self.current_station = parent.current_station
        # self.qc = parent.qc
        self.plotview = parent.plotview

    # def update(self):
    #     dr

    def show(self):
    # next/previous day
        button_next_day = widgets.Button(description='next day')
        button_prev_day = widgets.Button(description='previous day')

        button_next_day.on_click(self.on_button_next_day)
        button_prev_day.on_click(self.on_button_previous_day)

        box_day = widgets.Box([button_prev_day, button_next_day])
        display(box_day)
    # box
    ## select site
        dropdown_sites = widgets.Dropdown(
                                options=folder_dict.keys(),#'ber', 'brw', 'kwj', 'mlo', 'smo', 'spo', 'sum'],
                                value=self.current_station,
                                description='Site',
                                disabled=False,
                            )
        # display(dropdown_sites)
        dropdown_sites.observe(self.observe_dropdown_sites)

    ## select parameter group
        dropdown_para_group = widgets.Dropdown(
                                options=self.view.view_dict.keys(),#'ber', 'brw', 'kwj', 'mlo', 'smo', 'spo', 'sum'],
                                value=list(self.view.view_dict.keys())[0],
                                description='parameter group',
                                disabled=False,
                            )
        # display(dropdown_para_group)
        dropdown_para_group.observe(self.observe_dropdown_para_group)

        self.dropdown_para_group = dropdown_para_group

        boxII = widgets.Box([dropdown_sites, dropdown_para_group])
        display(boxII)


    ## text aerea for messages
        self.message_display = widgets.Textarea()
        self.message_display.value = self.view._message_txt
        display(self.message_display) # messages are added to this field through QCView.send_message()


    def observe_dropdown_para_group(self, evt):
        if evt['name'] == 'value':
            self.view.plotview.plot(evt['new'])
        pass

    def observe_dropdown_sites(self, evt):
        if evt['name'] == 'value':
            self.dropdown_para_group.index = False
            self.view.qc = evt['new']
            self.view.plotview.update_groups()
            self.update_dropdown_para_group()
            self.view.plotview.plot(para_group = self.dropdown_para_group.value)


    def update_dropdown_para_group(self):
        self.dropdown_para_group.index = False
        self.dropdown_para_group.options = self.view.view_dict.keys()
        self.dropdown_para_group.value = list(self.view.view_dict.keys())[0]

    def on_button_next_day(self, evt):
        #     try:
        self.view.qc.shift2next_day()
        self.plotview.update()

    def on_button_previous_day(self, evt):
        self.view.qc.shift2previous_day()
        self.plotview.update()
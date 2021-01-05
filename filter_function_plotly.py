import matplotlib.pyplot as plt
from IPython.display import display, HTML, Markdown

import pandas as pd
import numpy as np
from imp import reload
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go

from IPython.display import display, HTML, Markdown
import plotly.io as pio
from plotly.tools import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)


def filter_maker(figure, data, data_filters_list=[], traces_filters_list=[], traces_visibility_list=[],
                x_start=1.05, y_start=1.10, x_move=-0.1, y_move=0, dict_form=False):

    """
    filter_maker adds filters to the figures. An important note - there can be only one dropdown menu for
    traces filters and as many as you can fit for the data filters. If you are using traces filter, you need to create the initial
    figure in a way that traces for the same visibility are together
    INPUTS:

        figure - plotly figure object or a dictionary defining a figure

        data - dataframe that was used to create the original figure

        data_filters_list - a list of column names (as strings) from the data dataframe - what needs to be filtered in the data

        traces_filters_list - a list of options (as strings) for the dropdown - what needs to be filtered in the data

        traces_visibility_list - a list of integers indicating how the traces are grouped. For e.g. if you have 3 options in your
        traces_filters_list and first 2 traces are for the 1st option, then another 3 - for the 2nd option and the last one is for
        the 3rd option, your traces_visibility_list will be [2, 3, 1]

        x_start - where to start filters on the graph (horizontally)

        y_start - where to start filters on the graph (vertically)

        x_move - where to move any addition filters on the graph (horizontally)

        y_move - where to move any addition filters on the graph (vertically)

        dict_form - boolean indicating if the figure you provided is in dictionary form
    OUTPUTS:

        iplot figure with filters
    """

    # check if the traces_filters_list and traces_visibility_list
    # has the same amount of values

    if len(traces_filters_list) != len(traces_visibility_list):
        raise Exception('Your traces_filters_list and traces_visibility_list have different length!')

    # filters that filters the data

    filter_buttons = []
    transforms = []
    transf_i = 0

    for record in data_filters_list:

        dict_button = dict(type = 'dropdown',
                           active = 0,
                           x = x_start, y = y_start,
                           # when creating a button, instead of giving a True/False matrix,
                           # you change transforms values with args
                           buttons = list(pd.DataFrame(data[record].unique())[0].apply(
                               lambda x: dict(method='restyle', args=[{'transforms['+str(transf_i)+'].value': x}],
                                              label=x))))
        filter_buttons.append(dict_button)

        transf_i+=1
        x_start+=x_move
        y_start+=y_move

        transform_dict = dict(type = 'filter',
                              # target is the column where the filtered values are
                              target = data[record],
                              orientation = 'h',
                              # 'value' is current value
                              value = data[record].unique()[0])
        transforms.append(transform_dict)

    # filters that changes which axes are visible

    list_buttons = []

    traces = sum(traces_visibility_list)
    dicts = len(traces_filters_list)
    vector_size = traces*dicts
    true_start = 0

    for label, visible in zip(traces_filters_list, traces_visibility_list):
        visibility_list = [False for i in range(vector_size)]
        visibility_list[true_start:(true_start+visible)] = [True]*visible
        dict_button = dict(label=label,method="update",
                           args=[{"visible": visibility_list}])
        list_buttons.append(dict_button)
        true_start+=visible

    dict_for_visibility = dict(type = 'dropdown',
                               active=0,
                               x=x_start, y=y_start,
                               buttons=list_buttons)

    filter_buttons.append(dict_for_visibility)

    # adding buttons to the layout

    if dict_form:
        figure['layout']['updatemenus']=filter_buttons
    else:
        figure.layout.update(updatemenus=filter_buttons)

    # converting figure to dict

    if not dict_form:
        data = figure.to_dict()
    else:
        data = figure

    # updating transforms

    for trace in data['data']:
        trace['transforms'] = transforms

    # showing the plot. validate=False is important! It stops go (graph objects) from validating your figure
    iplot(data, validate=False)

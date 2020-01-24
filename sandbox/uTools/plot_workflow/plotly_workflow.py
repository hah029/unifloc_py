"""
Кобзарь О.С. Хабибуллин Р.А.

Модуль для построения графиков через plotly

"""


import sys
sys.path.append('../')
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.figure_factory as ff
import pandas as pd

def create_plotly_trace(data_x, data_y, namexy, chosen_mode='lines', use_gl = True):
    """
    Создание одного trace по данным

    :param data_x: данные для оси x
    :param data_y:  данные для оси y
    :param namexy: название для trace
    :param chosen_mode: настройка отображения 'lines', 'markers'
    :return: один trace
    """
    if use_gl == True:
        one_trace = go.Scattergl(
			x=data_x,
			y=data_y,
			name=namexy,
			mode=chosen_mode,
            hovertemplate = namexy + ": %{y:.3f}<extra></extra>"
		)
    else:
        one_trace = go.Scatter(
            x=data_x,
            y=data_y,
            name=namexy,
            mode=chosen_mode,
            hovertemplate=namexy + ": %{y:.3f}<extra></extra>"
        )
    return one_trace


def plot_func(data, plot_title_str, filename_str):
    """
    Итоговая функция для построения графиков

    :param data: созданный список из trace
    :param plot_title_str: название графика
    :param filename_str: названия html файлика
    :return: None
    """
    layout = dict(title=plot_title_str)

    fig = dict(data=data, layout=layout)

    # fig = make_subplots(rows=8, cols=1)

    plot(fig, filename=filename_str)
    # iplot(fig)


def plot_subplots(data_traces, filename_str, two_equal_subplots=False, auto_open = True):
    """
    Построение нескольких графиков

    :param data_traces: подготовленный список trace
    :param filename_str: имя файла .html
    :param two_equal_subplots: если True график будет разделен на 2 одинаковых друг по другом, если False - все в колонку
    :return: None
    """
    if two_equal_subplots:
        items_in_one_subplot = int(len(data_traces))
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
        for i in range(items_in_one_subplot):
            fig.append_trace(data_traces[i], row=1, col=1)
            fig.append_trace(data_traces[i], row=2, col=1)
    else:
        fig = make_subplots(rows=len(data_traces), cols=1, shared_xaxes=True, vertical_spacing=0.02)
        for i in range(len(data_traces)):
            fig.append_trace(data_traces[i], row=i + 1, col=1)
    fig.layout.hovermode = 'x'
    plot(fig, filename=filename_str, auto_open=auto_open)


def create_traces_list_for_all_columms(data_frame, chosen_mode='lines', use_gl = False):
    """
    Создание списка из trace для данного DataFrame для передачи их в data и последующего строительства графика.

    :param data_frame: подготовленный Pandas DataFrame с названиями колонок и обработанным индексом
    :param chosen_mode: выбор отображения 'lines', 'markers' и т.п.
    :return: trace_list для data
    """
    trace_list = []
    columns_name_list = data_frame.columns
    for i in columns_name_list:
        column_name = i
        this_series = data_frame[column_name].dropna()
        this_trace = create_plotly_trace(this_series.index, this_series, column_name, chosen_mode, use_gl)
        trace_list.append(this_trace)
    return trace_list


def connect_traces(traces1, trace2):
    """
    Создание единого списка trace из двух. Удобно при построении графиков из разных DataFrame

    :param traces1: первый список с trace
    :param trace2: второй список с trace
    :return: объединенный вариант
    """
    connected_traces = []
    for i in traces1:
        connected_traces.append(i)
    for j in trace2:
        connected_traces.append(j)
    return connected_traces


def create_report_html(df, all_banches, filename, auto_open = True):
    """
    Создание шаблонизированного и удобного набора графиков
    :param df:
    :param all_banches:
    :param filename:
    :return:
    """
    subplot_amount = len(all_banches)
    subplot_titles = []
    for z in all_banches:
        subplot_titles.append(list(z.keys())[0])
    fig = make_subplots(
        rows=subplot_amount, cols=1, shared_xaxes=True,
        vertical_spacing=0.01,
        subplot_titles=subplot_titles
    )
    for i in range(subplot_amount):
        this_df = df[all_banches[i][subplot_titles[i]]]
        this_banch_trace = create_traces_list_for_all_columms(this_df, chosen_mode='lines+markers', use_gl=True)
        for j in this_banch_trace:
            fig.add_trace(j, row=i + 1, col=1)

    fig.layout.hovermode = 'x'
    fig.layout.height = 450 * subplot_amount
    plot(fig, filename=filename, auto_open=auto_open)


def create_heat_map_data(df, name):
    data = go.Heatmap(
        z=df.values,
        x=list(df.columns),
        y=list(df.index), showscale=False, colorscale='RdBu', zmid=0, name=name)
    return data


def plot_corr_heatmap(df, filename_str):
    corrs = df.corr()
    figure = ff.create_annotated_heatmap(
        z=corrs.values,
        x=list(corrs.columns),
        y=list(corrs.index),
        annotation_text=corrs.round(2).values,
        showscale=True)
    figure.layout.update(
        margin=go.layout.Margin(
            l=400,
            r=50,
            b=100,
            t=250
        ))
    plot(figure, filename=filename_str)


def plot_scatterplotmatrix(df, file_name):
    figure = ff.create_scatterplotmatrix(df, diag='histogram')
    figure.layout.update(width=2000, height=1500)
    figure.layout.update(font=dict(size=7))

    plot(figure, filename=file_name)


def create_esp_traces(UniflocVBA, q_esp_nom_m3day, head_esp_nom_m):
    h_m = []
    efficency_perc = []
    power_wt = []
    q_m3day = list(range(1, int(q_esp_nom_m3day * 1.8), 10))
    pump_id = UniflocVBA.calc_ESP_id_by_rate(q_esp_nom_m3day)
    num_stages = int(head_esp_nom_m / UniflocVBA.calc_ESP_head_m(q_esp_nom_m3day, pump_id=pump_id))
    for i in q_m3day:
        h_m.append(UniflocVBA.calc_ESP_head_m(i, num_stages=num_stages, pump_id=pump_id))
        power_wt.append(UniflocVBA.calc_ESP_power_W(i, num_stages=num_stages, pump_id=pump_id) / 1000)
        efficency_perc.append(UniflocVBA.calc_ESP_eff_fr(i, num_stages=num_stages, pump_id=pump_id) * 100)
    esp_curve = pd.DataFrame({'Напор, м/100': h_m, 'Мощность, кВт': power_wt, 'КПД, %.': efficency_perc})
    esp_curve.index = q_m3day

    esp_curve.head()

    head_trace = create_plotly_trace(q_m3day, h_m, 'Напор, м')
    power_trace = create_plotly_trace(q_m3day, power_wt, 'Мощность, кВт')
    efficiency_trace = create_plotly_trace(q_m3day, efficency_perc, 'КПД, %.')
    close_f = UniflocVBA.book.macro('close_book_by_macro')
    close_f()
    return {'head_trace': head_trace, 'power_trace':power_trace, 'efficiency_trace': efficiency_trace}


def create_overall_report(overall_data, overall_data_dimensionless, esp_traces, filename, auto_open=True):
    nedeed_param_list = ['Q ж, м3/сут (Модель) (ADAPT)',
                         'ГФ (Модель) (ADAPT)',
                         'Обв, % (Модель) (ADAPT)',
                         'К. калибровки по напору - множитель (Модель) (ADAPT)',
                         'К. калибровки по мощности - множитель (Модель) (ADAPT)',
                         'F тока, ГЦ (Модель) (ADAPT)',
                         'Мощность, передаваемая СУ (Модель) (ADAPT)',
                         'КПД ЭЦН, д.ед. (Модель) (ADAPT)',
                         'Перепад давления в ЭЦН, атм (Модель) (ADAPT)',
                         'P буф., атм (Модель) (ADAPT)',
                         'Рлин ТМ (Ш) (ADAPT)',
                         'Давление на приеме насоса (пласт. жидкость) (СУ) (ADAPT)'
                         ]
    all_data_corr = overall_data[nedeed_param_list]
    all_data_corr = all_data_corr.corr()
    data = go.Heatmap(
        z=all_data_corr.values,
        x=list(all_data_corr.columns),
        y=list(all_data_corr.index), showscale=False, colorscale='RdBu', zmid=0)
    q_wc_gor = overall_data_dimensionless[
        ['Q ж, м3/сут (Модель) (ADAPT)', 'ГФ (Модель) (ADAPT)', 'Обв, % (Модель) (ADAPT)']]
    q_wc_gor_trace = create_traces_list_for_all_columms(q_wc_gor)
    calibrs = overall_data_dimensionless[['К. калибровки по напору - множитель (Модель) (ADAPT)',
                                          'К. калибровки по мощности - множитель (Модель) (ADAPT)']]
    calibrs_trace = create_traces_list_for_all_columms(calibrs)
    loss = overall_data_dimensionless[['P буф., атм (Модель) (ADAPT)',
                                       'Рлин ТМ (Ш) (ADAPT)',
                                       'Мощность, передаваемая СУ (Модель) (ADAPT)']]
    loss_trace = create_traces_list_for_all_columms(loss)
    fig = make_subplots(
        rows=7, cols=1,
        specs=[[{"type": "scattergl"}], [{"type": "scattergl"}],
               [{"type": "scattergl"}], [{"type": "heatmap"}],
               [{"type": "scattergl"}], [{"type": "scattergl"}],
               [{"type": "scattergl"}]]
    )
    fig.add_trace(q_wc_gor_trace[0],
                  row=1, col=1)
    fig.add_trace(q_wc_gor_trace[1],
                  row=1, col=1)
    fig.add_trace(q_wc_gor_trace[2],
                  row=1, col=1)

    fig.add_trace(calibrs_trace[0],
                  row=2, col=1)
    fig.add_trace(calibrs_trace[1],
                  row=2, col=1)

    fig.add_trace(loss_trace[0],
                  row=3, col=1)
    fig.add_trace(loss_trace[1],
                  row=3, col=1)
    fig.add_trace(loss_trace[2],
                  row=3, col=1)

    fig.add_trace(esp_traces['head_trace'],
                  row=4, col=1)
    fig.add_trace(esp_traces['power_trace'],
                  row=5, col=1)

    fig.add_trace(esp_traces['efficiency_trace'],
                  row=6, col=1)

    fig.add_trace(data,
                  row=7, col=1)

    fig.update_layout(height=7 * 500, showlegend=True)
    plot(fig, filename=filename, auto_open = auto_open)
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
import numpy as np
import pandas as pd

from wordcloud import WordCloud

def plot_moving_average(
    series: pd.Series, 
    window: int, 
    label: str, 
    plot_intervals: bool = False, 
    scale: float = 1.96,
    plot_anomalies: bool = False, 
    color: str = 'g',
) -> None:
    """Plots a moving average graph.

    Args:
        series (pd.Series): The time series data.
        window (int): The window size for the moving average.
        label (str): Label for the moving average series.
        plot_intervals (bool, optional): Whether to plot the confidence intervals. Defaults to False.
        scale (float, optional): The scale for the upper/lower bounds. Defaults to 1.96.
        plot_anomalies (bool, optional): Whether to plot anomalies from the confidence interval. Defaults to False.
        color (str, optional): Color of the moving average series. Defaults to 'g'. 
    """
    rolling_mean = series.rolling(window=window).mean()

    plt.title("Moving average\n window size = {}".format(window), size=30)
    plt.plot(rolling_mean, color, label=label, linewidth=3)

    # Plot confidence intervals for smoothed values
    if plot_intervals:
        mae = mean_absolute_error(series[window:], rolling_mean[window:])
        deviation = np.std(series[window:] - rolling_mean[window:])        
        #lower_bond = rolling_mean - (mae + scale * deviation)
        upper_bond = rolling_mean + (mae + scale * deviation)
        plt.plot(upper_bond, f"r--", label="Upper Bond")
        #plt.plot(lower_bond, f"r--", label='Lower Bond')

        # Having the intervals, find abnormal values
        if plot_anomalies:
            anomalies = pd.DataFrame(index=series.index, columns=series.columns)
            #anomalies[series < lower_bond] = series[series < lower_bond]
            anomalies[series > upper_bond] = series[series > upper_bond]
            anomalies = anomalies[anomalies < 4000]
            plt.plot(anomalies, "ro", markersize=10)

    #plt.plot(series[window:], label="Actual values")
    plt.legend(loc="upper left", prop={'size': 26})
    plt.xlabel('Date', size=25)  
    plt.xticks(size=20)
    plt.yticks(size=20)
    plt.ylabel('Likes', size=25)
    plt.grid(True)  


def plot_cloud(wordcloud: WordCloud, save_path: str, save: bool = False, ) -> None:
    """Plot a WordCloud object from text data.

    Args:
        wordcloud (WordCloud): The WordCloud object to plot.
        save_path (str): The path to save the image if save=True.
        save (bool, optional): Whether to save the image. Defaults to False.
    """
    plt.figure(figsize=(16, 9)) 
    plt.imshow(wordcloud)  
    plt.axis("off") 
    if save:
        plt.savefig(save_path)
# fledge-plugins
To setup a to send form the test rack measurements to the ktp-server (korte termijn) we developed a filter plugin and a north plugin. 
# Windowed moving average wma_filter:
The purpose of the wma filter is to compute for each data point the n-windowed average based on the n-1 datapoints ahead. The computed averages is tagged with the WMA datapoint string and sent to the north bridge at an interval of n points.

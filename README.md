# fledge-plugins
To setup a Fledge pipeline to send from the test rack measurements to the OpenSTEF-server (ktp-server) we use the wma_filter plugin and the ktp_north plugin. For the south plugin we use the iec61850 plugin:

https://github.com/fledge-iot/fledge-south-iec61850

To establish an approximate one second ‘requesting’ interval and to reduce the processor load when the plugin is out of connection, we changed  the timespan for 4 milliseconds to 1000 miliseconds. The lines 164 and 168 in iec61850.cpp were changed to: 

std::chrono::milliseconds timespan(1000);

# Windowed moving average wma_filter:
The purpose of the wma filter is to compute for each data point the n-windowed average based on the n-1 datapoints ahead. The computed averages is tagged with the WMA datapoint string and sent to the north bridge at an interval of n points. The timing is based on a datapoint per second. Then, e.g. a five minute windowed average corresponds to a window size of 300 points and sending upward at an interval of 300 points (modulo 300). The north plugin will select the filtered value according to the WMA datapoint string and sends it to the required OpenSTEF address.

To meet additional time requirements of the OpenSTEF server we send in this version the data onward at a rate of modulo N//2. Hence, in our case, a 5 minute average and the 5 minute average is considered.

# The ktp_north plugin:
The plugin sends datapoints with the string of Wma_filter to the location specified at System_id of the OpenSTEF server.
If the datapoint is an unfiltered value (during the initialization of the service), it be processed as ‘sent’ in order to empty the buffer of Fledge. 

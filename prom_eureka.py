#!/usr/bin/env python
import urllib.request, json, sys, datetime, re, random, time
from prometheus_client import start_http_server, Summary, Gauge

info_keys = {'renewPerMinT': 'Gets the threshold for the renewals per minute',
             'renewLastMin': 'Number of total heartbeats received in the last minute',
             'localRegSize': 'Number of Instances locally registered',
             'replsInLastM': 'Gets the number of renewals in the last minute',
             'belowThreshd': 'Checks if the number of renewals is lesser than threshold (This imply PANIC MODE)'
            }

eurekas = {
    'eureka-single-pri.dev.your.md': 'pri_dev',
    'eureka-single-bck.dev.your.md': 'bck_dev',
    'eureka-master.staging.your.md': 'pri_stg',
    'eureka-single-pri.staging.your.md': 'pri_stg_s',
    'eureka-single-bck.staging.your.md': 'bck_stg_s',
    'eureka.prod.your.md:8080': 'pri_prd',
    'eureka2.prod.your.md:8080': 'bck_prd'
    }

def extractValue(url):
    ret = {}
    time = datetime.datetime.now().isoformat()

    try:
        response = urllib.request.urlopen(url, timeout=2)
    except:
        ret['renewPerMinT'] = 'NaN'
        ret['renewLastMin'] = 'NaN'
        ret['localRegSize'] = 'NaN'
        ret['replsInLastM'] = 'NaN'
        ret['belowThreshd'] = 'NaN'
        return ret

    data = json.loads(response.read())

    ret['renewPerMinT'] = data["gauge.servo.numofrenewsperminthreshold"]
    ret['renewLastMin'] = data["gauge.servo.numofrenewsinlastmin"]
    ret['localRegSize'] = data["gauge.servo.localregistrysize"]
    ret['replsInLastM'] = data["gauge.servo.numofreplicationsinlastmin"]
    ret['belowThreshd'] = data["gauge.servo.isbelowrenewthreshold"]
    # ret['uptime'] = humanfriendly.format_timespan(data["uptime"]/1000)

    # if ret['renewLastMin'] < ret['renewPerMinT']:
    #     ret['emergency'] = True
    # else:
    #     ret['emergency'] = False
    return ret



# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

metr_url = 'http://eureka-single-pri.dev.your.md/eureka/metrics'
pattern = r"^.*?eureka([0-9]?)-?([a-z\-]*\.[a-z]*)\.your\.md.*$"
host = ''.join(re.findall(pattern, metr_url)[0])


g = {}

for url, inst in eurekas.items():
    for key, description in info_keys.items():
        k = inst + '_' + key
        g[k] = Gauge(k, description + 'for '+ inst)

if __name__ == '__main__':
    start_http_server(9000)
    while True:
        for url, inst in eurekas.items():
            metr_url = 'http://' + url + '/eureka/metrics'

            for key, value in extractValue(metr_url).items():
                k = inst + '_' + key
                g[k].set(value)

Tkinter dashboard

Designed to be lightweight dashboard for raspberry-pi

Features:
- text
- gauge
- graph
- time

Data sources:
- mysql

More can be added

Dashboard is configured by config.py

```
import os

config = {
    'sources': {
        'mysql': {
            'type': 'mysql',
            'host': os.environ.get('MYSQL_HOST'),
            'user': os.environ.get('MYSQL_USER'),
            'password': os.environ.get('MYSQL_PASSWORD'),
        }
    },
    'subs': {  # Subscribe variables to data-sources
        '$temp': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, created_at FROM nodered.metrics where name = 'zigbee2mqtt/temp_1' order by created_at desc limit 1"],
            'select': '$[*].value',  # JSON-path expression
            'get': 'first',  # Get only first value
        },
        '$power_data': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, time FROM nodered.power where time >= DATE_SUB(NOW(), interval 12 hour) order by time desc"],
            'select_x': '$[*].time',
            'select_y': '$[*].value',
            'get': 'chart',  # Get graph array ([x values, y values])
        }
    },
    'variables': {  # Variables and initial values
        '$temp': {
            'type': 'double',  # allowed str, int, double, generic
            'value': 0.0,
        },
        '$power_data': {
            'type': 'generic',  # Generic can store anything
            'value': [
                [],
                [],
            ]
        }
    },
    'layout': [
        [  # Row
            {'_': 'frame', 'title': 'Temperature', 'children': [
                {'_': 'label', 'var': '$temp'}
            ]},
        ],
        [
            {'_': 'frame', 'children': [
                {'_': 'clocks'}
            ]}
        ],
        [
            {'_': 'frame', 'title': 'Power consumption', 'children': [{
                '_': 'chart',
                'var': '$power_data',
                'mode': 'data',
                'size_y': 1
            }]},
        ],
    ]
}

```


Text:
```
{'_': 'label', 'var': '$temp'}
```

Gauge:
```
{
    '_': 'gauge',
    'width': 150,
    'height': 50,
    'var': '$power',
    'max': 200,
    'arc_size': 5,
    'fontsize': 20,
    'unit': ' W',
    'thresholds': {
        '_': 'white',
        '50': 'yellow',
        '100': 'red',
    }
}
```

Graph:
```
{
    '_': 'chart',
    'var': '$power_data',
    'mode': 'data',  # data or value (value appends, x is current time)
    'size_y': 1
}
```

Clocks:
```
{'_': 'clocks'}
```

MySQL source:

```
source = mysql
action = get
args = [sql_query]
```

```
'subs': {  # Subscribe variables to data-sources
	'$var': {
	    'source': 'mysql',
	    'action': 'get',
	    'args': ["SELECT value, created_at FROM nodered.metrics where name = 'zigbee2mqtt/temp_1' order by created_at desc limit 1"],
	   ...
	},
	...
}
```

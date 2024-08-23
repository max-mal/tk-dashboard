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
    'subs': {
        '$temp': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, created_at FROM nodered.metrics where name = 'zigbee2mqtt/temp_1' order by created_at desc limit 1"],
            'select': '$[*].value',
            'get': 'first',
        },
        '$humidity': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, created_at FROM nodered.metrics where name = 'zigbee2mqtt/temp_1/humidity' order by created_at desc limit 1"],
            'select': '$[*].value',
            'get': 'first',
        },
        '$power': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, time FROM nodered.power order by time desc limit 1"],
            'select': '$[*].value',
            'get': 'first',
        },
        '$power_data': {
            'source': 'mysql',
            'action': 'get',
            'args': ["SELECT value, time FROM nodered.power where time >= DATE_SUB(NOW(), interval 12 hour) order by time desc"],
            'select_x': '$[*].time',
            'select_y': '$[*].value',
            'get': 'chart',
        }
    },
    'variables': {
        '$temp': {
            'type': 'double',
            'value': 0.0,
        },
        '$humidity': {
            'type': 'double',
            'value': 0.0,
        },
        '$power': {
            'type': 'double',
            'value': 0.0,
        },
        '$var2': {
            'type': 'str',
            'value': 10,
        },
        '$power_data': {
            'type': 'generic',
            'value': [
                [],
                [],
            ]
        }
    },
    'layout': [
        [
            {'_': 'frame', 'title': '[Ch.] Power', 'children': [
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
            ]},
            {'_': 'frame', 'title': 'Temperature', 'children': [
                {'_': 'label', 'var': '$temp'}
            ]},
            {'_': 'frame', 'title': 'Humidity', 'visible': '$humidity', 'children': [
                {'_': 'label', 'var': '$humidity'}
            ]},
        ],
        [
            {'_': 'frame', 'children': [
                {'_': 'clocks'}
            ]}
        ],
        # [
        #     {'_': 'frame', 'title': 'Power meter', 'children': [
        #         {
        #             '_': 'gauge',
        #             'width': 250,
        #             'var': '$power',
        #             'max': 100,
        #             'unit': ' W',
        #             'thresholds': {
        #                 '_': 'green',
        #                 '50': 'yellow',
        #                 '100': 'red',
        #             }
        #         }
        #     ]},
        # ],
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

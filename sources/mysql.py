import mysql.connector


class MysqlSource:
    def __init__(self, config: dict) -> None:
        self.host = config.get('host')
        self.user = config.get('user')
        self.password = config.get('password')

        self.connect()

    def connect(self):
        self.db = mysql.connector.connect(
          host=self.host,
          user=self.user,
          password=self.password,
          autocommit=True
        )

    def get(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)

        row_headers = [x[0] for x in cursor.description]

        result = cursor.fetchall()
        data = []
        for result in result:
            data.append(dict(zip(row_headers, result)))

        return data

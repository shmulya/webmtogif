import mysql.connector


class MysqlCollector:

    def __init__(self, server, username, passwd, db):
        self.my = mysql.connector.connect(user=username, password=passwd, host=server,
                                          database=db)
        self.cursor = self.my.cursor()

    def select(self, table, cols='*', where=None):
        sql = f'SELECT {", ".join(cols)} FROM `{table}`'
        add = ';' if where is None else f' WHERE {where};'
        sql = sql + add
        try:
            self.cursor.execute(sql)
        except Exception as err:
            return {'status': False, 'data': str(err)}
        else:
            raw = self.cursor.fetchall()
            if len(raw) > 1:
                result = []
                for row in raw:
                    result.append(dict(zip(self.cursor.column_names, row)))
            elif len(raw) == 1:
                result = dict(zip(self.cursor.column_names, raw[0]))
            else:
                result = []
            return {'status': True, 'data': result}

    def insert(self, table, data):
        cols = [f'{x}' for x in data.keys()]
        vals = [f'"{x}"' for x in data.values()]
        sql = f'INSERT INTO `{table}` ({", ".join(cols)}) VALUES ({", ".join(vals)});'
        try:
            self.cursor.execute(sql)
            self.my.commit()
        except Exception as err:
            return {'status': False, 'data': str(err)}
        else:
            return {'status': True, 'data': None}

    def update(self, table, values, where=None):
        f_values = [f'{k}="{v}"' for k, v in values.items()]
        sql = f'UPDATE `{table}` SET {", ".join(f_values)}'
        add = ';' if where is None else f' WHERE {where};'
        sql = sql + add
        try:
            self.cursor.execute(sql)
            self.my.commit()
        except Exception as err:
            return {'status': False, 'data': str(err)}
        else:
            return {'status': True, 'data': None}

    def close(self):
        self.my.close()

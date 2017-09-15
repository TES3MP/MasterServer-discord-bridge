from typing import List


class Column:
    def __init__(self, name: str, centred_content: bool = True, length: int = 0):
        self.name = name
        if length == 0:
            self.length = len(name)
        else:
            self.length = length
        self.centred = centred_content


class TableGen:
    def __init__(self, columns: List[Column], max_length: int = 1994):
        self._columns = columns
        self._max_length = max_length
        self.__row = ''
        self.__sep_row = ''
        for column in columns:
            self.__row += '| ' + column.name[0:column.length].center(column.length, ' ') + ' '
            self.__sep_row += '+' + '-' * (column.length + 2)

        self.__sep_row += '+\n'
        self.__row += '|\n'

        self.__header_len = len(self.__row) + len(self.__sep_row) * 2
        self.__length = self.__header_len
        self.__rows = [self.__sep_row, self.__row, self.__sep_row]
        self._chunks = []

    @property
    def max_length(self):
        return self._max_length

    @property
    def columns(self):
        return self._columns

    @property
    def chunks(self):
        if self.__length != self.__header_len:  # if the last chunk is not completed, then force push it now.
            self.add_sep()
            self.__push_chunk()
        return self._chunks

    def add(self, *args: str):
        row = ''

        if len(args) == 0:  # add empty line
            for column in self._columns:
                row += '|' + ' ' * (column.length + 2)
        else:
            if len(args) != len(self._columns):
                raise ValueError('Passed wrong number of arguments.')
            for i in range(0, len(self._columns)):
                column_header = self._columns[i]
                column = args[i]

                if column_header.length != 0 and len(column) > column_header.length:
                    column = column[0:column_header.length]

                if len(column) < column_header.length:
                    if column_header.centred:
                        column = column.center(column_header.length, ' ')
                    else:
                        column += ' ' * (column_header.length - len(column))  # add spaces to the end

                row += '| ' + column + ' '

        self.__append(row + '|\n')

    def empty(self) -> bool:
        return len(self._chunks) == 0

    def add_sep(self):
        self.__append(self.__rows[0])

    def clean(self):
        if len(self._chunks) != 0:
            self.__rows = [self._chunks[0][0], self._chunks[0][1], self._chunks[0][0]]
        self._chunks.clear()
        self.__length = self.__header_len

    def __push_chunk(self):
        self._chunks.append(self.__rows)
        self.__rows = [self._chunks[0][0], self._chunks[0][1], self._chunks[0][0]]  # rewrite rows with header
        self.__length = self.__header_len

    def __append(self, data: str):
        length = len(data)
        if self.__length + length >= self.max_length:  # header
            self.__push_chunk()

        self.__length += length
        self.__rows.append(data)


if __name__ == '__main__':
    def main():  # make linter happy
        table_gen = TableGen([Column('Server addr', length=15), Column('Date', length=8), Column('Time', length=8),
                              Column('Reason', length=31, centred_content=False), Column('By', length=20)])

        table_gen.add('255.255.255.255', '30/12/17', '23:59:59', 'gamemode name', 'Koncord')
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()
        table_gen.add()

        table_gen.add()  # moved to another chunk
        table_gen.add()

        import sys

        print('First chunk: ')
        for row in table_gen.chunks[0]:
            sys.stdout.write(row)

            sys.stdout.flush()

        print('Second chunk: ')
        for row in table_gen.chunks[1]:
            sys.stdout.write(row)

        sys.stdout.flush()

    main()

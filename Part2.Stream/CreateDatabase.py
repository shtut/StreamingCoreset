import csv
import pandas as pd
import scipy.sparse as sps


class createDB:
    """
    This class purpose is to manipulate database in CSV format
    The constructor generates 2 sparse matrices and zip between them
    """
    def __init__(self, rows, cols):
        """
        The constructor generates 2 sparse matrices and zip between them
        :param rows: given number of rows
        :param cols: given number of columns
        """
        a = sps.rand(rows, cols, density=0.10, format='csr')
        a.data[:] = 1
        a = a.toarray()
        b = sps.random(rows, cols, density=0.25, format='csr')
        b.data[:] = 1
        b = b.toarray()
        c = []
        for elem in zip(a, b):
            c.extend(elem)
        self._db = c

    @property
    def db(self):
        """
        The generated data base
        :return: returns the DB
        """
        return self._db

    @staticmethod
    def write_matrix_to_csv(file_name, array):
        """
        The purpose of this method is to write a given array into CSV file
        :param file_name: given file name to write into
        :param array: the written array
        """
        with open(file_name, 'wb') as file:
            writer = csv.writer(file)
            for row in array:
                writer.writerow(row)

    @staticmethod
    def read_from_csv(file_name):
        """
        The purpose of this method is to read from a given file and create an array from it
        :param file_name: given file name to read from
        :return: the loaded array
        """
        df = pd.read_csv(file_name, sep=',', header=None)
        return df.values


# c = createDB(1000000, 10)
# createDB.write_matrix_to_csv('1.csv', c.db)
a = createDB.read_from_csv('1.csv')

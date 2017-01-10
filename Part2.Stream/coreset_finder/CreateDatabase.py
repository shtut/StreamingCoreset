import csv

import numpy as np
import scipy.sparse as sps


def process_chunk(chuck):
    print len(chuck)
    # do something useful ...


# noinspection PyMethodMayBeStatic
class createDB:
    """
    This class purpose is to manipulate database in CSV format
    The constructor generates 2 sparse matrices and zip between them
    """

    def __init__(self, method_to_run):
        self._processChunkMethod = method_to_run
        pass

    def create_matrix(self, rows, cols):
        """
        Generates 2 sparse matrices and zip between them
        :param rows: given number of rows
        :param cols: given number of columns
        """
        first_sparse = self.generate_uniform_sparse_matrix(rows, cols, 0.10)
        second_sparse = self.generate_random_sparse_matrix(rows, cols, 0.25)
        merged_sparse = []
        for elem in zip(first_sparse, second_sparse):
            merged_sparse.extend(elem)
        self._db = merged_sparse

    def generate_random_sparse_matrix(self, rows, cols, density):
        """
        Generate a sparse matrix with random distribution
        :param cols: number of columns in generated matrix
        :param rows: number of rows in generated matrix
        :param density: the density of values in the sparse matrix
        :return: the sparse matrix
        """
        temp = sps.random(rows, cols, density, format='csr')
        temp.data[:] = 1
        return temp.toarray()

    def generate_uniform_sparse_matrix(self, rows, cols, density):
        """
        Generate a sparse matrix with uniform distribution
        :param cols: number of columns in generated matrix
        :param rows: number of rows in generated matrix
        :param density: the density of values in the sparse matrix
        :return: the sparse matrix
        """
        temp = sps.rand(rows, cols, density, format='csr')
        temp.data[:] = 1
        return temp.toarray()

    @property
    def db(self):
        """
        The generated data base
        :return: returns the DB
        """
        return self._db

    def write_matrix_to_csv(self, file_name, array):
        """
        The purpose of this method is to write a given array into CSV file
        :param file_name: given file name to write into
        :param array: the written array
        """
        with open(file_name, 'wb') as file:
            writer = csv.writer(file)
            for row in array:
                writer.writerow(row)

    def read_from_csv(self, file_name, chunksize):
        """
        The purpose of this method is to read from a given file and create an array from it
        The method reads chunk by chunk from a CSV file and process it
        :param chunksize: given size of chunk to read from CSV
        :param file_name: given file name to read from
        """
        reader = csv.reader(open(file_name, 'rb'))
        # chunk = np.array([])
        chunk = None
        for i, line in enumerate(reader):
            if i % chunksize == 0 and i > 0:
                self._processChunkMethod(chunk)
                # del chunk[:]
                chunk = None
            if chunk is None:
                l = []
                for v in line:
                    l.append(float(v))
                chunk = np.asanyarray(l)
            else:
                chunk = np.vstack([chunk, np.asanyarray(line)])
        if chunk is not None:
            self._processChunkMethod(chunk)


# c = createDB(process_chunk)
# c.create_matrix(5000, 5)
# c.write_matrix_to_csv('2.csv', c.db)
# c.read_from_csv('1.csv', 500)

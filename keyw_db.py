"""database management for keyw application"""

__version__ = '15.01.2023'
__author__ = 'Serhiy Kobyakov'
__license__ = "MIT"


import os
import sqlite3


class KeywDB:
    """Class for the keyw database management"""
    THE_DB_FILE = 'my_metadata.sqlite3'

    def __init__(self, db_dir: str):
        if not os.path.isdir(db_dir):
            print(f"Error: the directory {db_dir} does not exists or it is not a directory!")
            print("  Please edit the keyw.ini properly:")
            print("  release_dir = <path to the directory where the database and all the relevant documents are>")
            exit(1)

        self.THE_DB_FILE = os.path.join(db_dir, self.THE_DB_FILE)

        # check for DB file
        if not os.path.exists(self.THE_DB_FILE):
            # create new database
            with open(self.THE_DB_FILE, "w") as f:
                pass
            print("keyw DB: file created")

            conn = self.create_db_conn(self.THE_DB_FILE)
            if conn is not None:
                c = conn.cursor()
                # create tables
                c.execute("""CREATE TABLE Models (
                             model_full_name TEXT PRIMARY KEY,
                             date_of_birth TEXT,
                             gender TEXT
                             ) WITHOUT ROWID""")
                c.execute("""CREATE TABLE Property (
                             property TEXT PRIMARY KEY,
                             owner_full_name TEXT
                             ) WITHOUT ROWID""")
                c.execute("""CREATE TABLE Images (
                             thumbnail BLOB NOT NULL,
                             file_name TEXT PRIMARY KEY,
                             isolation TEXT,
                             models TEXT,
                             property TEXT,
                             title TEXT,
                             description TEXT,
                             concept TEXT,
                             news TEXT,
                             action TEXT,
                             emotions TEXT,
                             model_spec TEXT,
                             objects TEXT,
                             image_spec TEXT,
                             location TEXT,
                             composition TEXT,
                             wwwww TEXT,
                             the_rest TEXT
                             ) WITHOUT ROWID""")
                c.execute("""CREATE VIEW Img_data AS SELECT
                             file_name,
                             isolation,
                             models,
                             property,
                             title,
                             description,
                             concept,
                             news,
                             action,
                             emotions,
                             model_spec,
                             objects,
                             image_spec,
                             location,
                             composition,
                             wwwww,
                             the_rest from Images""")
                conn.commit()
                print("keyw DB: tables created")
                conn.close()
            else:
                print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
                exit(1)

        # check DB before work
        conn = self.create_db_conn(self.THE_DB_FILE)
        if conn is not None:
            # check tables
            c = conn.cursor()
            c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Models' """)
            if not c.fetchone()[0] == 1:
                print(f'Error: Table "Models" does not exist in {self.THE_DB_FILE}!')
                exit(1)
            c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Property' """)
            if not c.fetchone()[0] == 1:
                print(f'Error: Table "Property" does not exist in {self.THE_DB_FILE}!')
                exit(1)
            c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Images' """)
            if not c.fetchone()[0] == 1:
                print(f'Error: Table "Images" does not exist in {self.THE_DB_FILE}!')
                exit(1)

            # maybe some data checks?

            conn.close()
        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)

    @staticmethod
    def create_db_conn(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Exception as e:
            print(e)
        return conn

    def insert_image_data(self, *args):
        """insert image data into DB"""
        n_args_expected = 18
        if not len(args) == n_args_expected:
            print(f"Error: number of insert_image() arguments is {len(args)} instead of {n_args_expected}!")
            exit(1)
        conn = self.create_db_conn(self.THE_DB_FILE)
        if conn is not None:
            try:
                c = conn.cursor()
                insert_query = """INSERT OR REPLACE 
                INTO Images VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                c.execute(insert_query, args)
                conn.commit()
            except sqlite3.Error as error:
                print(f"Error: can't insert the {args[1]} image data to DB:")
                print(f"  {error}")
            finally:
                if c.rowcount > 0:
                    print(f"image {args[1]} data has been inserted into DB successfully")
                conn.close()
        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)

    def data_exists(self, the_image: str):
        """check if data for the image the_image exists in DB"""
        conn = self.create_db_conn(self.THE_DB_FILE)
        if conn is not None:
            try:
                c = conn.cursor()
                insert_query = f"""SELECT file_name FROM Images WHERE file_name='{the_image}'"""
                c.execute(insert_query)
                if c.fetchone() is None:
                    result = False
                else:
                    result = True
            except sqlite3.Error as error:
                print(f"Error: problem with querying DB, table Images, for the value file_name={the_image}")
                print(f"  {error}")
            finally:
                # conn.commit()
                conn.close()
        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)
        return result

    def get_img_metadata(self, the_image: str):
        """get image the_image data"""
        result = None
        conn = self.create_db_conn(self.THE_DB_FILE)
        if conn is not None:
            try:
                c = conn.cursor()
                query = f"""SELECT * FROM Img_data WHERE file_name='{the_image}'"""
                c.execute(query)
                result = c.fetchone()
            except sqlite3.Error as error:
                print(f"Error: problem with getting image {the_image} data from DB")
                print(f"  {error}")
            finally:
                # conn.commit()
                conn.close()
        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)
        return result

    def get_imgs_metadata(self, images: list):
        """get image the_image data"""
        results = None
        conn = self.create_db_conn(self.THE_DB_FILE)
        if conn is not None:
            c = conn.cursor()
            q_result = ''
            for the_image in images:
                try:
                    c = conn.cursor()
                    query = f"""SELECT * FROM Img_data WHERE file_name='{the_image}'"""
                    c.execute(query)
                    q_result = c.fetchone()
                except sqlite3.Error as error:
                    print(f"Error: problem with getting image {the_image} data from DB")
                    print(f"  {error}")
                finally:
                    if len(q_result) > 0:
                        if results is None:
                            results = q_result
                        else:
                            results = [f'{results} {result}' for results, result in zip(results, q_result)]
            conn.close()

            # remove duplicates
            new_results = []
            counter = 0
            for line in results:
                if counter > 5:
                    tmp_str = line.replace('  ', ' ').replace('  ', ' ').strip()
                    new_results.append(' '.join(list(dict.fromkeys(tmp_str.split(' ')))))
                else:
                    new_results.append('')
                counter += 1
                # print(counter, new_results[-1])

        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)
        return new_results

    def get_search_data(self, search_str: str):
        """get list of images which have keywords"""
        conn = self.create_db_conn(self.THE_DB_FILE)
        result = None
        if conn is not None:
            try:
                c = conn.cursor()
                search_list = []
                for word in search_str.split(' '):
                    search_list.append(f"""(isolation LIKE '%{word}%' or
                    models LIKE '%{word}%' or
                    property LIKE '%{word}%' or
                    title LIKE '%{word}%' or
                    description LIKE '%{word}%' or
                    concept LIKE '%{word}%' or
                    news LIKE '%{word}%' or
                    action LIKE '%{word}%' or
                    emotions LIKE '%{word}%' or
                    model_spec LIKE '%{word}%' or
                    objects LIKE '%{word}%' or
                    image_spec LIKE '%{word}%' or
                    location LIKE '%{word}%' or
                    composition LIKE '%{word}%' or
                    wwwww LIKE '%{word}%' or
                    the_rest LIKE '%{word}%')""")
                insert_query = "SELECT thumbnail, file_name FROM Images WHERE (" +\
                               """ and """.join(search_list) + """) LIMIT 100"""
                # print(insert_query)
                c.execute(insert_query)
                result = c.fetchall()
                if not isinstance(result, list):
                    print("Error getting search results from DB (c.fetchall())!")
            except sqlite3.Error as error:
                print("Error: problem with DB:")
                print(f"  {error}")
            finally:
                # conn.commit()
                conn.close()
        else:
            print(f"Error: can't create the {self.THE_DB_FILE} database connection!")
            exit(1)
        return result

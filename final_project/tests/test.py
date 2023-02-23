import os.path

basedir = os.path.abspath(os.path.dirname(__file__))
# print(repr(os.path.join(basedir, 'database')))
print(os.path.isfile('./database/tracker.db'))

# os.path.exists()

# print(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
# os.path.exists(os.path.join(basedir, "database"))
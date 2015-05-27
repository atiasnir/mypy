# MYDATA

`download.py` automagically downloads all data sets specified in `db.tab`. The
most recent versions are kept in the folder `current` older versions can be
accessed by specifying the desired date. `read.py` provides access to all
db files.
A new set of db files can be downloaded by running

    python download.py

The `current` folder will now point to the new files and will be used by
`read.py`.

## Data sources: `db.tab`
All available data sets are listed in the `db.tab` table. In order to add a new data set one needs to specify

    DB<tab>SPECIES<tab>URL

or if species-unspecific

    DB<tab><tab>URL

## Reading fileformats `mypy.fileformats.py`

Any fileformat reader is implemented here. Note that `pandas` can be used to
read compressed files by providing `compression=...` to the `read_*(...)`
procedure.

## Configuration `download.py`

The variables `_ROOT_PATH`, `_CURRENT` and `_DB` can be changed to the desired
paths.

## TODO

1. report failed downloads
2. allow access by date
3. add more data sources
4. allow for more complex data downloads, independent of `db.tab`
5. deserialization of datasets if remained unchanged (symlink chain)

"""
A module with simple utilities for pandas.

"""
import pandas as pd

pd.options.display.width = 200

def split_and_stack(frame, colname, sep=None):
    """ Converts a row of delimited values in a dataframe to multiple rows.
        The resulting table is useful for joins.

        Parameters
        ----------
        frame:   the data frame to process
        colname: the name of the column containing the delimited data
        sep:     an optional pattern for split(). if not specified split on whitespace

        >>> import pandas as pd 
        >>> df = pd.DataFrame.from_items([('col1', ['1 2 3']), ('col2', ['a'])])
        >>> splitted = split_and_stack(df, 'col1')
        >>> splitted.shape
        (3, 2)

        >>> splitted
          col2 col1
        0    a    1
        0    a    2
        0    a    3
        
    """
    mask = frame[colname].isnull()

    masked_frame=frame[~mask]
    mapping = pd.DataFrame([{i: v for i,v in enumerate(x)} for x in
                             masked_frame[colname].str.split(sep).tolist()],
                             index=masked_frame.index).stack().reset_index(1,drop=True)
    mapping.name = colname # required for the merge

    return frame[[x for x in frame.columns if x!=colname]].join(mapping)

if __name__ == '__main__':
    import doctest

    doctest.testmod()

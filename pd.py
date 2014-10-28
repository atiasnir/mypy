"""
A module with simple utilities for pandas.

"""
import pandas as pd

pd.options.display.width = 200

def merge(df1, df2, how='inner', on=None, left_on=None, right_on=None,
          left_index=False, right_index=False, sort=False, suffixes=('', '_y'),
          copy=True, rename=None):
    """ Slightly nicer behavior relative to `pandas.DataFrame.join`.
        In particular:
        - joined columns are removed.
        - default suffix for the left table is empty

        Maybe used as drop-in replacement for the built-in pandas
        `merge` as follows:
        pd.DataFrame.merge = merge

        Parameters:
        -----------
        ... as per pandas documentation ... 

        Examples:
        ---------
        >>> import pandas as pd 
        >>> left = pd.DataFrame.from_items([('name', ['foo', 'bar']), ('id', [1, 2])])
        >>> right = pd.DataFrame.from_items([('name1', ['foo', 'bar']), ('id2', [10, 20])])
        >>> merge(left, right, left_on='name', right_on='name1')
          name  id  id2
        0  foo   1   10
        1  bar   2   20
        >>> merge(left, right, left_on='name', right_on='name1', rename={'id2': 'bla'})
          name  id  bla
        0  foo   1   10
        1  bar   2   20
    """
    result = pd.merge(df1, df2, how=how, on=on, left_on=left_on,
                      right_on=right_on, left_index=left_index,
                      right_index=right_index, sort=sort, suffixes=suffixes,
                      copy=copy)

    # remove columns appearing twice (due to different 'on' columns for left
    # and right)
    if left_on != right_on:
        if not hasattr(right_on, '__iter__'):
            right_on = (right_on,)
        right_cols = result.columns[df1.columns.shape[0]:]
        right_on_cols = [x for x in right_cols for j in right_on if x.startswith(j)]
        result.drop(right_on_cols, inplace=True, axis=1)

    if rename is not None:
        result.rename(columns=rename, inplace=True)

    return result

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

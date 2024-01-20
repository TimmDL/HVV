import pandas as pd

def perform_search(search_query, dataframe):
    def remove_spaces(text_input):
        return ''.join(text_input.split())

    normalized_query = remove_spaces(search_query.lower())

    def contains_query(row):
        row_string = remove_spaces(' '.join(map(str, row)).lower())
        return normalized_query in row_string

    return dataframe[dataframe.apply(contains_query, axis=1)]

def get_search_query(st):
    return st.text_input("Search:", "").strip()
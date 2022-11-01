import pandas as pd, magic, json, csv, jellyfish
from django.core.files.storage import FileSystemStorage
from io import StringIO

def load_excel(file):
    return pd.read_excel(file)

def load_csv(file, delimiters):
    sniffer = csv.Sniffer()
    with open(file) as f:
        dialect = sniffer.sniff(f.readline(), delimiters)
        f.seek(0)
        return pd.read_csv(file, delimiter=dialect.delimiter)

def find_jaro_similarity(target, df):
    max = 0
    name = None
    for column in df.columns:
        jaro = jellyfish.jaro_similarity(target, column)
        if (not name):
            name = column
            max = jaro
        elif (jaro > max):
            name = column
            max = jaro
    
    if max < 0.75: name = None
    return name

def override_jaro_similarity(target, df, overrides):
    if (target in df.columns):
        return target

    for alias in overrides[target]:
        if (alias in df.columns):
            return alias
    
    return None

def find_closest_df_col(target, df, overrides):
    name = None

    if (target in overrides):
        name = override_jaro_similarity(target, df, overrides)
    
    if (not name):
        name = find_jaro_similarity(target, df)
        
    return name

# NOTE: prioritises column names for df1
def merge_df(df1, df2, overrides):
    temp = pd.DataFrame()
    for col in df1:
        closest_df2_col = find_closest_df_col(col, df2, overrides)
        if (closest_df2_col):
            temp[col] = df1[col].tolist() + df2[closest_df2_col].tolist()
        else:
            temp[col] = df1[col].tolist() + [""] * df2.shape[0]

    return temp

def eva_main(files, overrides):
    df = []
    df_merge = None
    fs = FileSystemStorage()
    mime_types = json.load(fs.open('mime_types.json'))

    print("Importing files from INPUT folder...")

    for file_name in files:
        file = fs.open(file_name)
        file_mime = magic.from_buffer(file.readline(), mime=True)
        file.seek(0)
        df.append(load_excel(file)) if file_mime == mime_types["excel"] else df.append(load_csv(file, mime_types["delimiters"]))
        fs.delete(file_name)

    print("Files loaded. Merging...\nThis might take a while")

    # initiate the merge
    current_merge = 1
    if (not df_merge):
        if (len(df) < 2):
            print("ERROR: There must be more than 1 frame to merge")
        else:
            df_merge = merge_df(df[0], df[1], overrides)

    while current_merge < len(df):
        df_merge = merge_df(df_merge, df[current_merge], overrides)
        current_merge += 1

    print("Merging complete. Exporting...")

    #TODO: temperary storage - serve - then delete
    export_name = fs.save('export.csv', StringIO(df_merge.to_csv()))

    print("Export complete! Goodbye :)")
    return export_name
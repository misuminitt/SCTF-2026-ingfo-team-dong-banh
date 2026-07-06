from zipfile import ZipFile

with ZipFile("hidden_clean.zip") as z:
    for info in z.infolist():
        print(info.filename, info.file_size)
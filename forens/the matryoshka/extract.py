import pyzipper
password = b"SCTF_EXIF_S3CR3T"
with pyzipper.AESZipFile("hidden_clean.zip") as z:
    z.pwd = password
    z.extractall("out")
print(open("out/flag.txt").read())
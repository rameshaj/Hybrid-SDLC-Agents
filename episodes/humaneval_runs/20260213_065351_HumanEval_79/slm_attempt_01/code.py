def decimal_to_binary(decimal):
    return f"db{bin(decimal)[2:].zfill(8)}db"
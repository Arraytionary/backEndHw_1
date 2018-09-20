
def object_generator(path,listFile,lenFile,sIndex,eIndex):
    if sIndex == eIndex:
        yield get_content(path+listFile[i],sIndex,eIndex)
    else:
        for i in range(sIndex,eIndex+1):
            if i == 0:                                              #first file
                yield get_content(path+listFile[i],sIndex,lenFile[i])
            elif i == eIndex:
                get_content(path+listFile[i],0,eIndex)              #last file
            else:
                yield get_content(path+listFile[i],0,lenFile[i])    #middle file
def get_content(path, start, end):
        with open(path, "rb") as file:
            if start is not None:
                file.seek(start)
            if end is not None:
                remaining = end - (start or 0)
            else:
                remaining = None
            while True:
                chunk_size = 64 * 1024
                if remaining is not None and remaining < chunk_size:
                    chunk_size = remaining
                chunk = file.read(chunk_size)
                if chunk:
                    if remaining is not None:
                        remaining -= len(chunk)
                    yield chunk
                else:
                    if remaining is not None:
                        assert remaining == 0
                    return
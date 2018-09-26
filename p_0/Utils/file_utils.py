
def object_generator(path,listFile,lenFile,sIndex,eIndex,sByte,eByte):
    if sIndex == eIndex:
        gen =  get_content(path+listFile[sIndex],sByte,eByte)
        for g in gen:
            yield g

    else:
        for i in range(sIndex,eIndex+1):
            if i == 0:                                              #first file
                gen =  get_content(path+listFile[i],sByte,lenFile[i])
                for g in gen:
                    yield g 
            elif i == eIndex:
                gen = get_content(path+listFile[i],0,eByte)              #last file
                for g in gen:
                    yield g
            else:
                gen = get_content(path+listFile[i],0,lenFile[i])    #middle file
                for g in gen:
                    yield g
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
                    yield bytes(chunk)
                else:
                    if remaining is not None:
                        assert remaining == 0
                    return 
try:                    #Python 2
    from xmlrpclib import ServerProxy
    from xmlrpclib import Transport
except ImportError:     #Python 3
    from xmlrpc.client import ServerProxy
    from xmlrpc.client import Transport
import hashlib
import struct
import os
import zlib
import base64

class Setting(object):
    OPENSUBTITLES_SERVER ='http://api.opensubtitles.org/xml-rpc'
    USER_AGENT = 'OSTestUserAgent'
    LANGUAGE = 'en'


class Proxy_Trans(Transport):
    '''Proxy Support for xmlrpclib module
    '''
    def set_proxy(self, proxy):
        self.proxyurl = proxy
                
    def request(self, host, handler, request_body, verbose=0):
        import urllib2

        opener = urllib2.build_opener(urllib2.ProxyHandler({'http':self.proxyurl}))
        f = urllib2.Request(url = "http://%s%s"%(host,handler), data = request_body)
        self.verbose = verbose

        return self.parse_response(opener.open(f))

class OpenSubAPI(object):
    
    def __init__(self,proxy_url = None):
        if proxy_url:
            p = Proxy_Trans()
            p.set_proxy(proxy_url)
            self._os_server = ServerProxy(Setting.OPENSUBTITLES_SERVER,transport=p)

        else:
            self._os_server = ServerProxy(Setting.OPENSUBTITLES_SERVER)

    def _check_result(self, key):
        '''Return the key from data if the status code in data is 200
        else returns None
        '''
        status = self._data.get('status').split()[0]
        return self._data.get(key) if '200' == status else None


    def login(self,username="",password=""):
        '''Returns Token if successful else None'''
        
        self._data = self._os_server.LogIn(username,password,Setting.LANGUAGE,Setting.USER_AGENT)
        token = self._check_result('token')

        if token:
            self.token = token
        return token

    def logout(self):
        '''Returns True if successful else False'''
        self._data = self._os_server.LogOut(self.token)
        return '200' in self._data.get('status')

    def ping(self):
        '''Ping the server to keep connection alive. Return True if alive else returns False'''
        self._data = self._os_server.NoOperation(self.token)
        return '200' in self._data.get('status')

    def search_sub(self,path=None,imdbid=None,name=None,languageid=None,limit=None):
        '''Searches subtitles. Preference order- hash>imdbid>filename
        '''
        if languageid:
            lan = languageid
        else:
            lan = 'eng'
        if limit:
            lim = limit
        else:
            lim = 10
        result = None
        if path != None:
            self._data = self._os_server.SearchSubtitles(self.token,[{'sublanguageid':lan,'moviehash':self._get_hash(path),'moviebytesize':str(os.path.getsize(path))}],{'limit':lim})
            result = self._check_result('data')
            if result:
                return result
        if imdbid != None:
            self._data = self._os_server.SearchSubtitles(self.token,[{'sublanguageid':lan,'imdbid':imdbid}],{'limit':lim})
            result = self._check_result('data')
            return result
        if name == None and path != None:
            name = os.path.basename(path)
        if name != None:
            self._data = self._os_server.SearchSubtitles(self.token,[{'sublanguageid':lan,'query':name}],{'limit':lim})
            result = self._check_result('data')
        return result

    def search_sub_list(self,path_list=None,imdbid_list=None,name_list=None,languageid=None,limit=None):
        '''Taken an input contanining path_list or imdb_list or name_list. If the provided list is path_list and the movie
         is not found then the movie name from the path list is used to search for the movie.
         Returns a list contaning the info about subs of the corresponding movie. If the subs are not found for a movie then
        the corresponding element in the return list is None.
        '''
        if languageid:
            lan = languageid
        else:
            lan = 'eng'
        if limit:
            lim = limit
        else:
            lim = 10

        result = None
        query_list = []

        if path_list!=None:
            query_list = [{'sublanguageid':lan,'moviehash':self._get_hash(path),'moviebytesize':str(os.path.getsize(path))} for path in path_list]
        
        elif imdb_list != None:
            query_list = [{'sublanguageid':lan,'imdbid':imdbid} for imdbid in imdb_list]

        elif name_list != None:
            query_list = [{'sublanguageid':lan,'query':name} for name in name_list]
                
        else:
            return None

        self._data = self._os_server.SearchSubtitles(self.token,query_list,{'limit':lim})
        result = self._check_result('data')

        if result != None and path_list != None:
            if len(result) != len(path_list):
                print "Result Error! len(result) != len(path_list)"
                return None
            index = []
            query_list = []
            for num in range(len(result))
                if result[num] == None
                    index.append(num)
                    query_list.append({'sublanguageid':lan,'query':os.path.basename(path_list[num])})
            self._data = self._os_server.SearchSubtitles(self.token,query_list,{'limit':lim})
            temp_result = self._check_result('data')
            if temp_result:
                if len(index) != len(temp_result):
                    print "Result Error! len(index) != len(temp_result)"
                    return None
                i = 0
                for ind in index:
                    result[ind] = temp_result[i]
                    i+=1

        return result


    def check_movie(self,path):
        '''Check if the movie hash is present in the server
        '''
        result = self._os_server.CheckMovieHash(self.token,[self._get_hash(path)])
        return result

    def check_movie_list(self,path_list):
        '''Check if the hash of the movies in the list are present on the server
        '''
        hash_list = [self._get_hash(path) for path in path_list]
        result = self._os_server.CheckMovieHash(self.token,hash_list)
        return result

    def download_sub(self,sub_id):
        '''Return as dict with subtitleid as key and the corresponding subtitle file as its value
        '''
        self._data = self._os_server.DownloadSubtitles(self.token,[sub_id])
        data = self._check_result('data')
        if data:
            decoded_data = base64.decodestring(data[0]['data'])
            srt = zlib.decompress(decoded_data,16+zlib.MAX_WBITS)
            return {data[0]['idsubtitlefile']:srt}
            
        else:
            return None

    def downoad_sub_list(self,sub_id_list):
        '''Returns a dict with subtitleid as key and the corresponding subtitle file as its value
        '''
        self._data = self._os_server.DownloadSubtitles(self.token,sub_id_list)
        data = self._check_result('data')
        if data:
            return {subs['idsubtitlefile']:zlib.decompress(base64.decodestring(subs['data']),16+zlib.MAX_WBITS) for subs in data} 
        else:
            return None

    def guess_movie(self,path):
        name = os.path.basename(path)
        self._data = self._os_server.GuessMovieFromString(self.token,[name])
        result = self._check_result('data')
        if result:
            #!!! CHECK !!!#
            return result[0]['BestGuess']['IDMovieIMDB']

    def _get_hash(self,path):
        longlongformat = 'q'  # long long
        bytesize = struct.calcsize(longlongformat)

        try:
            f = open(path, "rb")
        except(IOError):
            return "IOError"

        size = str(os.path.getsize(path))

        hash = int(size)

        if int(size) < 65536 * 2:
            return "SizeError"

        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

        f.seek(max(0, int(size) - 65536), 0)
        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF

        f.close()
        returnedhash = "%016x" % hash
        return str(returnedhash)

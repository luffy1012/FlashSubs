import requests,os,sys,hashlib

class SubDBAPI():

	_HEADER = {'User-Agent':'SubDB/1.0 (SubsDownloader/0.1; http://github.com/luffy1012/subdb)'}
	_url= 'http://api.thesubdb.com'

	def get_hash(self,file_path):
		'''Returns file hash from the given file path
		'''
		readsize = 64*1024
		with open(file_path,"rb") as media_file:
			data = media_file.read(readsize)
			media_file.seek(-readsize,os.SEEK_END)
			data += media_file.read(readsize)
		return hashlib.md5(data).hexdigest()

	def get_subs(self,file_hash,language=None):
		'''Returns subtitles from the given file hash if found else returns None
		'''

		if language:
			lan = language
		else:
			lan = 'en'
		try:
			sub = requests.get(self._url,headers=self._HEADER,params={'action':'download','language':lan,'hash':file_hash})
			sub.raise_for_status()
		except Exception as e:
			return None
		else:
			return sub.content

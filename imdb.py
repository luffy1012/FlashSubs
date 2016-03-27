import os,sys,bs4,requests,re,string

class Imdb(object):
	'''Class containing functions related to imdb'''

	_search_url = "http://www.bing.com/search?q=site:imdb.com "
	_imdb_url = 'http://www.omdbapi.com'

	_spam_name = ['720p','480p','bluray','blu','x264','yify','brrip'\
				,'camrip','dvdrip','360p','retail','300mb','400mb'\
				,'700mb','800mb','600mb','900mb','hc','hd','hdrip'\
				,'1080p','3d','3ds','dual','dual audio','hindi','hin','putlocker'\
				,'eng','english','dual-audio','xvid','unrated','dvdscr'\
				,'bdrip','eng-hin','hin-eng','webrip','cdrip','web','dl','webdl','cd','dvd']



	def get_imdb_id(self,file_list):
		'''Returns a list containing the imdb_id (without initial 'tt') corresponding to the files in the file_list
		'''
		clean_list=[]
		for files in file_list:
			name,ext = os.path.splitext(files)
			name = os.path.basename(name)
			table = string.maketrans(string.punctuation,' '*len(string.punctuation))
			name = name.lower().translate(table).split()
			if(len(name) > 4):
				name = name[:5]
			clean = ""
			for component in name:
				if not component in self._spam_name:
					clean += " "+component
				else:
					break
			clean_list.append(clean.lstrip())


		id_list=[]
		for clean_name in clean_list:
			try:
				page = requests.get(self._search_url+clean_name)
				page.raise_for_status()
			except Exception as e:
				id_list.append(None)
			else:
				page_soup = bs4.BeautifulSoup(page.text,"lxml")
				links = page_soup.select(".b_attribution")
				for link in links:
					imdb_id = re.search(r"www.imdb.com/title/tt(\w+)",link.text.encode('utf-8'))
					if not imdb_id == None:
						id_list.append(imdb_id.group(1))
						break
				else:
					id_list.append(None)
		return id_list

	
	def get_info(self,id_list):
		'''Fetches important data from imdb using imdbid in the passed list.
		'''
		info_list = []

		for ids in id_list:
			if ids == None:
				info_list.append(None)
			else:
				try:
					info = requests.get(self._imdb_url,params={'i':ids,'plot':'full'})
					info.raise_for_status()
				except Exception as e:
					info_list.append(None)
					pass
				else:
					info = info.json()
					info_list.append(info)
		return info_list

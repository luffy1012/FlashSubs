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
		'''Returns a list containing the imdb_id corresponding to the files in the file_list
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
		return id_list

	
	def get_info(self,id_list):
		'''Fetches important data from imdb using imdbid in the passed list.
		'''
		info_list = []

		for ids in id_list:
			try:
				info = requests.get(self._imdb_url,params={'i':ids,'plot':'full'})
				info.raise_for_status()
			except Exception as e:
				info_list.append(None)
				pass
			else:
				info = info.json()
				info_list.append(info)


		# directories = [direc[1] for direc in file_list]
		# for files in file_list:
		# 	try:
		# 		info = requests.get(self.url,params={'i':files[0],'plot':'full'})
		# 		info.raise_for_status()
		# 	except Exception as e:
		# 		GLOBAL_LOCK.acquire()
		# 		print "{0} occured while getting IMDB info of {1}".format(str(e),files[1])
		# 		GLOBAL_LOCK.release()
		# 	else:
		# 		info = info.json()
		# 		with open(os.path.join(files[1],info['Title'].encode('utf-8')+".nfo"),"w") as info_file:
		# 			for key in info.keys():
		# 				info_file.write("{0:15}-->  {1}\n".format(key.encode('utf-8'),info[key].encode('utf-8')))

		# 		dir_name = files[1]
		# 		file_name = files[2]
		# 		full_path_sans_ext,ext = os.path.splitext(os.path.join(files[1],files[2]))

		# 		try:
		# 			os.rename(os.path.join(dir_name,file_name),os.path.join(dir_name,info['Title'].encode('utf-8')+ext))
		# 			GLOBAL_LOCK.acquire()
		# 			print "Renamed {0} to {1}".format(file_name,info['Title'].encode('utf-8'))
		# 			GLOBAL_LOCK.release()
		# 		except OSError:
		# 			pass
		# 		if os.path.exists(full_path_sans_ext+".srt"):
		# 			try:
		# 				os.rename(full_path_sans_ext+".srt",os.path.join(dir_name,info['Title'].encode('utf-8')+".srt"))
		# 			except OSError:
		# 				pass
		# 		#TODO: Improve Check
		# 		if not directories.count(dir_name) > 1:
		# 			try:
		# 				os.rename(dir_name,os.path.join(os.path.dirname(dir_name),info['Title'].encode('utf-8')))
		# 			except OSError:
		# 				pass


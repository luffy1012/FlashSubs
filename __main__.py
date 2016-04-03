import opensubapi
from subdb import SubDBAPI
from imdb import Imdb
import os,sys
from unicodedata import normalize
import traceback
import argparse

RUNNING_AS_WINDOW = False
DEV_NOTE = "\nFlashSubs v0.30\n\nDeveloped by:\nSuyash Agrawal (suyash1212@gmail.com)\n"
FORBIDDEN_CHARS = "*\"/\[]|<>:"

def get_list(dir_path):
	file_list = []
	for direc,fol,files in os.walk(dir_path):
		for fl in files:
			name = os.path.join(direc,fl)
			base_file,ext = os.path.splitext(name)
			if not (os.path.exists(base_file+".srt") and \
				os.path.exists(base_file+".nfo")) and\
				ext in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"] and\
				int(os.path.getsize(name)) > 1024*1024*60:
				file_list.append(name)
	return file_list

def prog_init():
	if len(sys.argv) > 1:
		parser = argparse.ArgumentParser()

		parser.add_argument("path",help="Path containing Movies and TV Series")
		parser.add_argument("-l","--login", metavar="Username:Password",help="Login details of opensubtitles.org account")
		parser.add_argument("-p","--proxy", metavar="Server_address:Port",help="Proxy address and port")
		args = parser.parse_args()
		path = args.path
		
		if not os.path.isdir(path):
			print "Enter Correct Path."
			sys.exit()
		
		if args.login:
			username,password = args.login.split(':')
		else:
			username = None
			password = None

		if args.proxy:
			proxy = args.proxy
			if proxy[:4] != "http":
				proxy = "http://"+proxy
		else:
			proxy = None
	else:
		RUNNING_AS_WINDOW = True
		path = raw_input("Enter the path of the directory: ")
		if not os.path.isdir(path):
			print "Path given is not valid!"
			sys.exit()
		
		conf = raw_input("Are you working behind a proxy? (y/n): ")
		if conf.lower() in ['y',"yes",'yup']:
			proxy = raw_input("Enter http proxy_server:port -> ")
			if proxy[:4] != "http":
				proxy = "http://"+proxy
		else:
			proxy = None

		conf = raw_input("Do you wish to login (opensubtitles.org account)? (y/n): ")
		if conf.lower() in ['y',"yes",'yup']:
			username = raw_input("Username- ")
			password = raw_input("Password- ")
		else:
			username = None
			password = None

	return (username,password,proxy,path)

def subdb_download(result,num_movie,movie_list,sub_list):
	for i in xrange(num_movie):
		if i%20 == 0:
			print"*",
		if not result[i]:
			movie_hash = subdb.get_hash(movie_list[i])
			if movie_hash == "SizeError":
				continue
			sub = subdb.get_subs(movie_hash,'en')
			if sub:
				sub_list[i] = sub

def opensub_download(open_subs_id,index_opensub,sub_list):
	down_subs = {}
	if opensub.get_down_lim() <= 0:
		print "Download Limit Reached!\nTry after 24 hours\n"
	else:
		for num in xrange(0,len(open_subs_id),20):
			print "*",
			sub = opensub.download_sub_list(open_subs_id[num:num+20])
			if sub==None:
				for index in xrange(num,num+20):
					if index < len(open_subs_id):
						temp_sub = opensub.download_sub(open_subs_id[index])
						if temp_sub:
							down_subs.update(temp_sub)
			else:
				down_subs.update(sub)

		for sub_id,index in zip(open_subs_id,index_opensub):
			try:
				down_subs[sub_id]
			except:
				pass
			else:
				sub_list[index] = down_subs[sub_id]

def opensub_download_id(no_sub_imdb_id,no_sub_imdb_id_index,sub_list):
	result = opensub.search_sub_list(imdbid_list=no_sub_imdb_id)
	sub_id=[]
	sub_id_index=[]
	#Using reversed so that the first MovieHash overwrites the same MovieHashes that come after it.
	result_dict = {res['IDMovieImdb']:res for res in reversed(result)}
	for ids,index in zip(no_sub_imdb_id,no_sub_imdb_id_index):
		try:
			result_dict[ids]
		except:
			pass
		else:
			sub_id_index.append(index)
			sub_id.append(result_dict[ids]['IDSubtitleFile'])
	
	down_sub = opensub.download_sub_list(sub_id)

	for ids,index in zip(sub_id,sub_id_index):
		try:
			down_sub[ids]
		except:
			pass
		else:
			sub_list[index] = down_sub[ids]

def save(base_path,base_name,new_name,ext,sub,info,log):
	if not os.path.exists(os.path.join(base_path,new_name)+ext):
		os.rename(path,os.path.join(base_path,new_name)+ext)
		log.write("Renamed \"{0}\" to \"{1}\"\n".format(base_name,new_name))
				
		if os.path.exists(os.path.join(base_path,base_name)+".srt"):
			log.write("Subtitle Exists!\n")
			os.rename(os.path.join(base_path,base_name)+".srt",os.path.join(base_path,new_name)+".srt")
		elif sub:
			log.write("Subtitle Added\n")
			with open(os.path.join(base_path,new_name)+".srt","w") as sub_file:
				sub_file.write(sub)
		if info:
			log.write("Info Added\n")
			with open(os.path.join(base_path,new_name)+".nfo","w") as info_file:
				for key in sorted(info.iterkeys()):
					info_file.write("{0}:\n{1}\n\n".format(key.encode('utf-8'),info[key].encode('utf-8')))
	else:
		if sub and not os.path.exists(os.path.join(base_path,base_name)+".srt"):
			log.write("Subtitle Added\n")
			with open(os.path.join(base_path,base_name)+".srt","w") as sub_file:
				sub_file.write(sub)
		if info and not os.path.exists(os.path.join(base_path,base_name)+".nfo"):
			log.write("Info Added\n")
			with open(os.path.join(base_path,base_name)+".nfo","w") as info_file:
				for key in sorted(info.iterkeys()):
					info_file.write("{0}:\n{1}\n\n".format(key.encode('utf-8'),info[key].encode('utf-8')))
#########################################################################################################################

if __name__ == "__main__":

	log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"log_flashsubs.txt")
	if os.path.isfile(log_file) and os.path.getsize(log_file) < 10*1024*1024:
		log = open(log_file,"a")
	else:
		log = open(log_file,"w")
	
	try:
		username,password,proxy,path = prog_init()

		subdb = SubDBAPI()
		if proxy:
			imdb = Imdb({'http':proxy})
		else:
			imdb = Imdb()

		opensub = opensubapi.OpenSubAPI(proxy)
		
		if username and password:
			try:
				token = opensub.login(username,password)
				assert type(token)==str
			except:
				print "Invalid username or password.\n"
				sys.exit()
			else:
				print "Login Successful\n"
		else:
			try:
				token = opensub.login()
				assert type(token)==str
			except:
				print "Check Internet Connection"
				sys.exit()

		#get file list
		movie_list = get_list(path)

		#Total Number of Movies
		num_movie = len(movie_list)
		
		#subtitle file for movies
		sub_list = [None]*num_movie
		
		#index number for movies whose imdbid are not yet found
		no_id_index = []
		
		#imdb id of movies in movie list
		imdb_id_list = [None]*num_movie
		
		#subtitles id for movies in opensubtitles.org
		open_subs_id = []
		
		#index for which subs are found in opensubtitles.org
		index_opensub = []
		
		print "Total Files - {}".format(num_movie)

		if num_movie ==0:
			opensub.logout()
			print "Nothing to do here!"
			sys.exit()


		#get imdb id for movies whose hash is present in opensubapi
		print "Searching"
		result = opensub.check_movie_list(movie_list)
		if result:
			for i in xrange(num_movie):
				if result[i]:
					imdb_id_list[i] = result[i]['MovieImdbID']

		print "Downloading Subs"
		subdb_download(result,num_movie,movie_list,sub_list)


		#get movies which are present in opensub database by name or hash
		print "\nSearching Subs"
		result = opensub.search_sub_list(movie_list)


		len_res = len(result)
		for i in xrange(num_movie):
			if i >= len_res or result[i] == None:
				if not imdb_id_list[i]:
					no_id_index.append(i)
			else:
				if not imdb_id_list[i]:
					imdb_id_list[i] = result[i]['IDMovieImdb']
							
				if not sub_list[i]:
					open_subs_id.append(result[i]['IDSubtitleFile'])
					index_opensub.append(i)
				
		#Download Subs which are found in opensubtitles database
		print "Downloading Subs"
		opensub_download(open_subs_id,index_opensub,sub_list)
		

		if len(no_id_index) != 0:
			print "\nSearching Info"
			no_id_file = []
			for index in no_id_index:
				no_id_file.append(movie_list[index])
			id_list = imdb.get_imdb_id(no_id_file)
			for ids,index in zip(id_list,no_id_index):
				imdb_id_list[index] = ids

		#get info from imdb about movies in movie list
		print "\nGetting Information"
		info_list = imdb.get_info(["tt"+"0"*(7-len(ids))+ids if ids else None for ids in imdb_id_list])

		#Now, sub_list = subtitles for corresponding movies in movie_list
		# info_list = info for correspoding movies in movie_list

		if len(info_list) != len(sub_list) != num_movie:
			print "ERROR"
			sys.exit()

		no_sub_imdb_id = []
		no_sub_imdb_id_index = []

		for i in xrange(num_movie):
			if imdb_id_list[i] != None and sub_list[i] == None:
				no_sub_imdb_id.append(imdb_id_list[i])
				no_sub_imdb_id_index.append(i)

		if opensub.get_down_lim() <= 0:
			print "Download Limit Reached!\nTry again after 24 hours\n"
		
		elif len(no_sub_imdb_id) != 0:
			conf = raw_input("\nWARNING: Experimental\nOnly proceed if the names of your file are not misleading \
like videoplayback, movie, s9e8 etc.\nDo you wish to use this feature?(y/n): ")
			if conf.lower() in ['yes','y']:
				opensub_download_id(no_sub_imdb_id,no_sub_imdb_id_index,sub_list)

		#Final - sub_list - subtitles of movies in movie_list
		#Final - info_list - info of movies in movie_list

		print "Saving"

		#dictionary with key as id of series and corresponding value as name of series.
		series_dict={}

		try:
			for num in xrange(num_movie):
				path = movie_list[num]
				base_path,name = os.path.split(path)
				base_name,ext = os.path.splitext(name)
				info = info_list[num]
				sub = sub_list[num]

				log.write("\nCurrently Processing - {}\n".format(path))

				try:
					title = normalize('NFKD',info['Title']).encode('ascii','ignore')
					new_name = title
				except:
					new_name = base_name
				else:
					if info['Type']=='series':
						continue
					elif info['Type'] == 'episode':
						Season = info['Season']
						Episode = info['Episode']
						if Season.isdigit() and Episode.isdigit():
							try:
								series_id = str(info['seriesID'])
								try:
									Series_name = series_dict[series_id]
								except:
									Series_name = normalize('NFKD',imdb.get_info([series_id])[0]['Title']).encode('ascii','ignore')
									if Series_name:
										series_dict[series_id] = Series_name
							except:
								Series_name = ""
							len_season = 2
							len_episode = 2
							if len(Episode) > len_episode:
								new_name = "{0} S{1:0>2}E{2} {3}".format(Series_name,str(Season),str(Episode),title)
							else:
								new_name = "{0} S{1:0>2}E{2:0>2} {3}".format(Series_name,str(Season),str(Episode),title)
							
				#Removing forbidden characters from files (Windows forbidden)
				new_name = str(new_name).translate(None,FORBIDDEN_CHARS).lstrip()

				#saving
				save(base_path,base_name,new_name,ext,sub,info,log)
		except:
			opensub.logout()
			raise

		log.write("-"*120)
		log.close()
		opensub.logout()
		print("\nDone!")
		print("Changes done are stored in {}\n".format(log_file))
		print(DEV_NOTE)

		if RUNNING_AS_WINDOW:
			raw_input("Press any key to exit...")
	
	except BaseException as e:
		if not type(e).__name__ in ["SystemExit","KeyboardInterrupt"]:
			print "\nOops...An Error Occured!\n"
			log.write("\nERROR:\n")
			log.write(traceback.format_exc())
			print "Error information stored in {}".format(log_file)
		print(DEV_NOTE)
		log.write("\n"+"-"*120)
		log.close()
		if RUNNING_AS_WINDOW:
			raw_input("Press any key to exit...")
		sys.exit()

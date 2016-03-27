import opensubapi
from subdb import SubDBAPI
from imdb import Imdb
import os,sys

def get_list(dir_path):
	file_list = []
	for direc,fol,files in os.walk(dir_path):
		for fl in files:
			name = os.path.join(direc,fl)
			base_file,ext = os.path.splitext(name)
			if not (os.path.exists(base_file+".srt") and os.path.exists(base_file+".nfo")) and ext in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
				file_list.append(name)
	return file_list


if __name__ == "__main__":
	if len(sys.argv) > 1:
		if not os.path.isdir(sys.argv[1]):
			print "Path provided is not a directory!"
		else:
			subdb = SubDBAPI()
			imdb = Imdb()
			#METHOD TO GET PROXY IF PROVIDED
			proxy = "10.10.78.22:3128"
			opensub = opensubapi.OpenSubAPI(proxy)
			try:
				token = opensub.login()
				assert type(token)==str
			except:
				print "Login to OpenSubtitles.org failed!"
			else:
				print "Login Successful"
				#get file list
				movie_list = get_list(sys.argv[1])
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
					print "No Movie to search subs for!"
					sys.exit()

				#get imdb id for movies whose hash is present in opensubapi
				result = opensub.check_movie_list(movie_list)
				if result:
					for i in range(num_movie):
						if result[i]:
							imdb_id_list[i] = result[i]['MovieImdbID']

				print "Downloading Subs from Source 1"
				for i in range(num_movie):
					if not result[i]:
						print "*",
						movie_hash = subdb.get_hash(movie_list[i])
						sub = subdb.get_subs(movie_hash,'en')
						if sub:
							sub_list[i] = sub

				#get movies which are present in opensub database by name or hash
				print "\nSearching Subs in Source 2"
				result = opensub.search_sub_list(movie_list)


				len_res = len(result)
				for i in range(num_movie):
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
				print "Downloading Subs from Source 2"
				down_subs = {}
				for num in range(0,len(open_subs_id),20):
					print "*",
					sub = opensub.download_sub_list(open_subs_id[num:num+20])
					if sub==None:
						for index in range(num,num+20):
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

				if len(no_id_index) != 0:
					print "Searching Subs from Source 3"
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

				for i in range(num_movie):
					if imdb_id_list[i] != None and sub_list[i] == None:
						no_sub_imdb_id.append(imdb_id_list[i])
						no_sub_imdb_id_index.append(i)

				if len(no_sub_imdb_id) != 0:
					print "Downloading Subs from Source 3"				
					result = opensub.search_sub_list(imdbid_list=no_sub_imdb_id)
					#print result
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

				#Final - sub_list - subtitles of movies in movie_list
				#Final - info_list - info of movies in movie_list

				print "Writing to Directory"

				for num in range(num_movie):
					path = movie_list[num]
					base_path,name = os.path.split(path)
					base_name,ext = os.path.splitext(name)
					info = info_list[num]
					sub = sub_list[num]

					try:
						new_name = info['Title']
					except:
						new_name = base_name
					else:
						if info['Type']=='series':
							continue
						elif info['Type'] == 'episode':
							Season = info['Season']
							Episode = info['Episode']
							if Season.isdigit() and Episode.isdigit():
								len_season = 2
								len_episode = 2
								if len(Episode) > len_episode:
									new_name = "S{0:0>2}E{1} - {2}".format(str(Season),str(Episode),info['Title'])
								else:
									new_name = "S{0:0>2}E{1:0>2} - {2}".format(str(Season),str(Episode),info['Title'])
							else:
								new_name = info['Title']
							

					if not os.path.exists(os.path.join(base_path,new_name)+ext):
						os.rename(path,os.path.join(base_path,new_name)+ext)
						print "Renamed {0} to {1}".format(base_name,new_name)
						
						if os.path.exists(os.path.join(base_path,base_name)+".srt"):
							os.rename(os.path.join(base_path,base_name)+".srt",os.path.join(base_path,new_name)+".srt")
						elif sub != None:
							with open(os.path.join(base_path,new_name)+".srt","w") as sub_file:
								sub_file.write(sub)
						if info:
							with open(os.path.join(base_path,new_name)+".nfo","w") as info_file:
								for key in info.keys():
									info_file.write("{0}:\n{1}\n\n".format(key.encode('utf-8'),info[key].encode('utf-8')))
					else:
						if not os.path.exists(os.path.join(base_path,base_name)+".srt") and sub != None:
							with open(os.path.join(base_path,base_name)+".srt","w") as sub_file:
								sub_file.write(sub)
						if info != None and not os.path.exists(os.path.join(base_path,base_name)+".nfo"):
							with open(os.path.join(base_path,base_name)+".nfo","w") as info_file:
								for key in info.keys():
									info_file.write("{0}:\n{1}\n\n".format(key.encode('utf-8'),info[key].encode('utf-8')))


				opensub.logout()
				print("Done!")			
	else:
		print "Usage: {} <path to directory>".format(sys.argv[0])
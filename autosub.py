import opensubapi
import subdb
import imdb

def get_list(dir_path):
	file_list = []
	for direc,fol,files in os.walk(dir_path):
		for fl in files:
			name = os.path.join(direc,fl)
			base_file,ext = os.path.splitext(name)
			if not os.path.exists(base_file+".srt") and ext in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
				file_list.append(name)
	return file_list


if __name__ == "__main__":
	if len(sys.argv) > 1:
		if not os.path.isdir(sys.argv[1]):
			print "Path provided is not a directory!"
		else:
			print "Starting"
			file_list = get_list(sys.argv[1])
			#METHOD TO GET PROXY IF PROVIDED
			proxy = "10.10.78.22"
			opensub = opensubapi.OpenSubAPI(proxy)
			
	else:
		print "Usage: {} <path to directory>".format(sys.argv[0])
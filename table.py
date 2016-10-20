from fcntl import flock, LOCK_EX, LOCK_UN

FILE = "/tmp/preorders"
def append(string):
	with open(FILE, 'a') as f:
		try:
			flock(f, LOCK_EX) # block until we have the exclusive lock
			f.write(string)
		finally:
			flock(f, LOCK_UN) # release lock

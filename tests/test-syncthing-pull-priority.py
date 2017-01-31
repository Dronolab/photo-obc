#!/usr/bin/env python
import string
import random

def writeToFile(path, filename):
    with open(path + filename, 'w') as outfile:
    	outfile.seek((1024 * 1024 * 10) - 1)
        outfile.write('\0')

def main():
	path='/home/dronolab/dev/photo/captures/'
	for i in range(0, 100):
		filename = 'A' + random.choice(string.letters) + random.choice(string.letters)
		writeToFile(path, filename)

if __name__ == '__main__':
	main()
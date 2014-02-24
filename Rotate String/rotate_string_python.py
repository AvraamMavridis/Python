def rotate(myword,monkey):
	temp = ' '
	for i in range(0,monkey):
		temp = myword[len(myword)-1];
		for z in range(len(myword)-1,0,-1):
			myword[z] = myword[z-1]
		myword[0] = temp
	return ''.join(myword)

def main():
    testcases = input()
    initialword = ""
    counts = [0] * eval(testcases)
    for i in range(0,eval(testcases)):
    	word = input()
    	myword = list(word)
    	initialword = word
    	monkey,pop = input().split(" ")
    	while True:
    		word = rotate(myword,eval(monkey))
    		counts[i] = counts[i] + 1
    		if word == initialword:
    			break
    		word = rotate(myword,eval(pop))
    		counts[i] = counts[i] + 1
    		if word == initialword:
    			break
    for i in range(0,eval(testcases)):
    	print(counts[i])
			

if __name__ == "__main__":
    main()
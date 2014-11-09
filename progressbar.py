import sys
import terminalsize

def truncatedprint(label, width):
	if len(label) <= width:
		print label.ljust(width, ' '),
	else:
		print '%s...' % label[0:width-3],

def printbar(label, n_done, n_size):
        width, height = terminalsize.get_terminal_size()
        barwidth = 12;

        while barwidth < width / 2:
                barwidth += 12

        percent = (100 * n_done) / n_size
        barfill = (barwidth * n_done) / n_size
        
        sys.stdout.write('\r')
	truncatedprint(label, width - barwidth - 8)
	
	if percent >= 0:
		print '%s%%' % str(percent).rjust(3, ' '),
	else:
		sys.stdout.write('     ')
	
	sys.stdout.write('[')
	
	if n_done < 0:
		sys.stdout.write(('{:#^' + str(barwidth) + '}').format('  FAILED  '))
	elif n_done == n_size:
		sys.stdout.write(('{:#^' + str(barwidth) + '}').format('  DONE  '))
	else:
		for i in range(0, barfill):
			sys.stdout.write('#')
		for i in range(barfill, barwidth):
			sys.stdout.write('-')
	
	print ']',
        sys.stdout.flush()

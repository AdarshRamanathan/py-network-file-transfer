import sys
import terminalsize

def truncatedprint(label, width):
	if len(label) <= width:
		print label.ljust(width, ' '),
	else:
		print '%s...' % label[0:width-3],

def prettyeta(eta):
        eta = 1 + int(eta)
        ret = ''
        suffixes = ('s', 'm', 'h', 'd', 'w', 'y', 'c')
        factors = (60, 60, 24, 7, 52, 100, 1)
        index = 0

        while eta > 0 and index < 7:
                ret = str(int(eta % factors[index])).rjust(2, ' ') + suffixes[index] + 'X' + ret
                eta /= factors[index]
                index += 1

        if eta > 0:
                ret = 'too long :('

        return ' '.join(ret.split('X')[0:3])
                
def printbar(label, n_done, n_size, elapsed_time = 0):
        width, height = terminalsize.get_terminal_size()
        barwidth = 12;

        while barwidth < width / 2:
                barwidth += 12

        barwidth -= 12

        percent = (100 * n_done) / n_size
        barfill = (barwidth * n_done) / n_size
        
        sys.stdout.write('\r')
	truncatedprint(label, width - barwidth - 20)
        
	if percent >= 0:
                if n_done == n_size:
                        print '%s' % prettyeta(elapsed_time).rjust(11, ' '),
                elif elapsed_time > 4:
                        eta = (elapsed_time * n_size) / n_done - elapsed_time
                        print '%s' % prettyeta(eta).rjust(11, ' '),
                else:
                        print '           ',
                
		print '%s%%' % str(percent).rjust(3, ' '),
	else:
		sys.stdout.write('                 ')
	
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

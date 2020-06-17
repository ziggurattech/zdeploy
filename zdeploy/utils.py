def reformat_time(time):
	h, m, s = [int(float(x)) for x in ('%s' % time).split(':')]
	return '%sh, %sm, and %ds' % (h, m, s)

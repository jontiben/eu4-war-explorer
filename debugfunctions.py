#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from datetime import datetime

def debug_out(event_text: str, event_type=None) -> None:
	# Outputs the time plus the event type and event to a text file.
	time = datetime.now().time()
	if event_type != None:
		fullstring = f"[{time}] {event_type}: {event_text}\n"
	else:
		fullstring = f"[{time}] *** {event_text}\n"
	out_file = open("debug.txt", 'a')
	out_file.write(fullstring)
	out_file.close()
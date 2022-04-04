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
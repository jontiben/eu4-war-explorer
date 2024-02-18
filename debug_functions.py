# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
# copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

from datetime import datetime

save_number = -1
messages = []

def debug_out(event_text: str, event_type: str | None = None) -> None:
    # Outputs the time plus the event type and event to a text file.
    time = str(datetime.now().time())[:-4]
    if save_number > -1:
        if event_type is not None:
            spacing = ' ' * (6 - len(event_type))
            fullstring = f"| S{save_number} [{time}] {event_type}:{spacing}{event_text}\n"
        else:
            fullstring = f"| S{save_number} [{time}]        {event_text}\n"
    else: # Before the first save's opened
        if event_type is not None:
            fullstring = f"[{time}] {event_type}: {event_text}\n"
        else:
            fullstring = f"[{time}] ***** {event_text}\n"
    with open("debug.txt", 'a') as out_file:
        out_file.write(fullstring)


def new_save() -> None:
    global save_number
    save_number += 1
    out_file = open("debug.txt", 'a')
    out_file.write(f"\n================================ SAVE {save_number} ================================\n")
    out_file.close()


def hold_until_start(event_text: str, event_type: str = None) -> None:
    global messages
    messages.append((event_text, event_type))


def output_message_backlog() -> None:
    global messages
    for message in messages:
        debug_out(message[0], event_type=message[1])
    messages = []





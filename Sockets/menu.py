# modified from: https://stackoverflow.com/questions/39488788/how-to-make-a-menu-in-python-navigable-with-arrow-keys

import curses

def menu(stdscr):
  classes = ["Create account", "List accounts", "Delete account"]
  attributes = {}
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
  attributes['normal'] = curses.color_pair(1)

  curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
  attributes['highlighted'] = curses.color_pair(2)

  c = 0  # last character read
  option = 0  # the current option that is marked
  while True:  # Enter in ascii
    stdscr.erase()
    stdscr.addstr("\nWelcome to ChatBot! What would you like to do?\n\n")
    for i in range(len(classes)):
      if i == option:
        attr = attributes['highlighted']
      else:
        attr = attributes['normal']
      #stdscr.addstr("{0}. ".format(i + 1))
      stdscr.addstr("{0}".format(" > "))
      stdscr.addstr(classes[i] + '\n', attr)
    c = stdscr.getch()
    if c == 10: # this means enter key has been pressed
      break
    elif c == curses.KEY_UP and option >= 0:
      if option == 0:
        option = 2
      else:
        option -= 1
    elif c == curses.KEY_DOWN and option < len(classes):
      if option == 2:
        option = 0
      else:
        option += 1

  return [option, classes[option]]

  #stdscr.addstr("You chose {0}".format(classes[option]))
  #stdscr.getch()

curses.wrapper(menu)
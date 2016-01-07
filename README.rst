============================================
Birthday - Manage birthdays of your friends.
============================================
Facebook notifies you when today is some your friends' birthday, that's great, but it won't show "tomorrow" or "7 days later" birthdays.

Some people don't use Facebook, or they just hide their birthday.

I want a command line tool, so that when I open a terminal, it shows birthdays of my friends upcoming in three days.

Usage
------
::

  birthday subcommand arguments ...

Available commands:

* help
* add
* update
* show
* delete
* rename
* examples

Examples: ::

  # I only know his/her age, but no date
  $ birthday add Dear-friend 1991/xx/xx
  $ birthday show
  1991/--/-- Dear-friend

  # Hey, he/she just tell me his/her birthday date!
  $ birthday update Dear-friend xxxx/11/02
  $ birthday show
  1991/11/02 Dear-friend

  # (add many many friends)

  # What's the birthday of Dear-friend?
  $ birthday show name=friend year=1991 month=11
  1991/11/02 Dear-friend

  # how to use?
  $ birthday examples

All records are stored into ``~/.birthday.sqlite``.

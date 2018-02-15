# Instructions

Clone: git clone git@github.com:dls-controls/EBEClient.git

Run Simulator:

  $ python
  >>> from ebe import EBESim
  >>> sim = EBESim("127.0.0.1", 8080)
  >>> sim._recv()

Run Client App:

  $ python ebe/app.py -h                                          # View Help
  $ python ebe/app.py -i 127.0.0.1 -p 8080                       # Read Device Name
  $ python ebe/app.py -i 127.0.0.1 -p 8080 --param 10            # Get param 10
  $ python ebe/app.py -i 127.0.0.1 -p 8080 --param 10 --value 2  # Set param 10 to 2
  

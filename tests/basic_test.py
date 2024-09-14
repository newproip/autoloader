from newpro_autoloader.loader import Loader

# No connection is made in the constructor
loader = Loader()

# Commands that require a connection will make one automatically
version, sub_version, number_of_slots = loader.get_version()
print(version)
print(sub_version)
print(number_of_slots)

# Home must be complete before other actions that include motion
print("Loader is initializing...")
loader.home()

# First call to load_cassette prepares the device to load the cassette
print("Preparing to load cassette")
loader.load_cassette()
input("Load lock is open, please load a new cassette.  Press enter when done.")

# Second call completes the process after the user has installed the cassette
loader.load_cassette()
print("Load lock is closed, new cassette loaded")

# Put a sample into the instrument.  Slot numbers are 1-based.
for slot in range(1, number_of_slots+1, 1):
    print(f"Loading sample {slot}, please wait...")
    loader.load(slot)
    input(f"Sample {slot} loaded, press enter to load next")
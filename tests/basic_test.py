
from signal import signal, SIGINT

from newpro_autoloader.loader import Loader

def print_status(loader: Loader):
    if loader.is_homed:
        print("loader is homed")
    else:
        print("loader is NOT homed")

    if loader.is_gripped:
        print("slot " + str(loader.index_loaded) + " is loaded")
    else:
        print("nothing is loaded")

    if loader.is_cassette_present:
        print("cassette is present")
    else:
        print("cassette is NOT present")

# Entering this context starts a background thread that polls the status
loader: Loader
with Loader() as loader:

    # This is one way to support cancellability.  You could
    # also call stop from another thread when loader is blocked
    # on a long-running command.
    signal(SIGINT, loader.stop)

    print("Loader is initializing...")
    print(f"version {loader.version}.{loader.sub_version}, {loader.number_of_slots} slot capacity")
    print_status(loader)

    # Home must be complete before other actions that include motion
    print("Homing...")
    loader.home()

    # First call to load_cassette prepares the device to load the cassette
    print("Preparing to load cassette")
    loader.load_cassette()
    input("Load lock is open, please load a new cassette.  Press enter when done.")

    # Second call completes the process after the user has installed the cassette
    loader.load_cassette()
    print("Load lock is closed, new cassette loaded")

    # Put a sample into the instrument.  Slot numbers are 1-based.
    for slot in range(1, loader.number_of_slots+1, 1):
        #print(f"Loading sample {slot}, please wait...")
        #loader.load(slot)
        #input(f"Sample {slot} loaded, press enter to load next")
        print(f"slot {slot} is {loader.slot_state(slot).name}")

    print_status(loader)
    loader.load(1)
    print_status(loader)
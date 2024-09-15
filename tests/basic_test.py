
from signal import signal, SIGINT

from newpro_autoloader.loader import Loader


# Entering this context starts a background thread that polls the status
loader: Loader
with Loader() as loader:

    # This is one way to support cancellability.  You could
    # also call stop from another thread when loader is blocked
    # on a long-running command.
    signal(SIGINT, loader.stop)

    version, sub_version, number_of_slots = loader.get_version()
    print(f"version {version}.{sub_version}, {number_of_slots} slot capacity")

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
        #print(f"Loading sample {slot}, please wait...")
        #loader.load(slot)
        #input(f"Sample {slot} loaded, press enter to load next")
        print(f"slot {slot} is {loader.slot_state(slot).name}")
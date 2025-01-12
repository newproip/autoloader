"""An example script that shows how to use the Loader class to interface to the hardware"""
from signal import signal, SIGINT

from newpro_autoloader.loader import Loader

def print_status(loader_in: Loader):
    """An example of displaying some information about the loader"""
    status_str = "STATUS: "
    if loader_in.is_homed:
        status_str = status_str + "homed, "
    else:
        status_str = status_str + "NOT homed, "

    status_str = status_str + "grip state is " + loader_in.grip_state.name + ", "

    if loader_in.is_gripped:
        status_str = status_str + "slot " + str(loader_in.index_loaded) + " is loaded, "
    else:
        status_str = status_str + "nothing is loaded, "

    if loader_in.is_cassette_present:
        status_str = status_str + "cassette is present"
    else:
        status_str = status_str + "cassette is NOT present"

    print(status_str)

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
    loader.clear()
    print_status(loader)

    # Home must be complete before other actions that include motion
    print("Homing...")
    loader.home()

    # First call to load_cassette prepares the device to load the cassette
    print("Preparing to load cassette")
    loader.load_cassette()
    input("Load lock is open, please load a new cassette.  Press enter when done.")

    # Second call completes the process after the user has installed the cassette
    print("Load lock is closed, please wait...")
    loader.load_cassette()
    print("New cassette is loaded and mapped")

    # Show the slot states
    for slot in range(1, loader.number_of_slots+1, 1):
        print(f"slot {slot} is {loader.slot_state(slot).name}")

    # Put a sample into the instrument.  Slot numbers are 1-based.
    slot_to_load: int = 3

    print_status(loader)
    print(f"Loading sample {slot_to_load}, please wait...")
    loader.load(slot_to_load)
    print_status(loader)
